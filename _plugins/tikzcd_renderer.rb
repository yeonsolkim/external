# frozen_string_literal: true

require "digest"
require "fileutils"
require "json"
require "open3"
require "tmpdir"

module ExternalTikzcdRenderer
  CACHE_VERSION = "7"
  DEFAULT_CACHE_DIR = ".jekyll-cache/tikzcd"
  # The diagrams' 10pt math size in the SVG user unit, the big point.
  TEX_EM_BP = 10 * 72 / 72.27
  # MathJax sizes its SVG output in ex, taking the x-height of its font
  # (mathjax-newcm) to be the x-height of the surrounding text. Sizing diagrams
  # the same way makes 10pt equal MathJax's em at every font size.
  MATHJAX_X_HEIGHT = 0.442
  # New Computer Modern's own x-height is lower, so that MathJax's em is a little smaller than
  # the text's. A picture's text is the page's text and takes the text's em.
  TEXT_X_HEIGHT = 0.431
  TEXT_SCALE = format("%.5f", MATHJAX_X_HEIGHT / TEXT_X_HEIGHT)
  # New Computer Modern's outlines for the glyphs of TeX's fonts, and the symbol font's metrics
  # with its widths (scripts/diagram_glyphs.py).
  GLYPHS_PATH = File.expand_path("tikzcd_glyphs.json", __dir__)
  DISPLAY_MATH_PATTERN = /\$\$(?<body>.*?)\$\$/m
  # One diagram environment and nothing else: the body may not end another one.
  TIKZ_ENVIRONMENT_PATTERN = /\A\s*(?<environment>\\begin\s*\{(?<name>tikzcd|tikzpicture)\}(?:\[[^\]\r\n]*\])?(?:(?!\\end\s*\{\k<name>\}).)*\\end\s*\{\k<name>\})\s*\z/m
  TIKZ_BEGIN_PATTERN = /\\begin\s*\{(?:tikzcd|tikzpicture)\}/
  HASSE_PATTERN = /\\begin\s*\{tikzpicture\}\s*\[[^\]]*\bhasse\b/
  # What every diagram's document adds to TikZ. A post has no preamble of its own, and the
  # `hasse` style gives a tikzpicture what tikz-cd gives its diagrams: it sits centred on the
  # math axis, here 0.25em above the baseline, so it lines up with the math around it. The
  # Obsidian plugin's main.js defines the same; test_tikzcd_renderer.rb keeps them together.
  TIKZ_PREAMBLE = <<~'LATEX'.strip
    \usetikzlibrary{positioning}
    \tikzset{
      hasse/.style={
        baseline={([yshift=-.25em]current bounding box.center)},
        dot/.style={circle, fill, inner sep=0pt, minimum size=3pt},
      },
    }
  LATEX

  # A picture's text has fonts of its own, TeX's under another name, so that it can be told from
  # its math and set in the size of the page's text. The math keeps the size of MathJax's.
  TEXT_FONTS = <<~LATEX.strip
    \\DeclareFontFamily{OT1}{posttext}{}
    \\DeclareFontShape{OT1}{posttext}{m}{n}{<->s*[#{TEXT_SCALE}]newcmr10}{}
    \\DeclareFontShape{OT1}{posttext}{m}{it}{<->s*[#{TEXT_SCALE}]newcmti10}{}
    \\DeclareFontShape{OT1}{posttext}{bx}{n}{<->s*[#{TEXT_SCALE}]newcmbx10}{}
    \\renewcommand\\rmdefault{posttext}
  LATEX
  TEXT_STYLES = {
    "newcmr10" => %(font-style="normal" font-weight="normal"),
    "newcmti10" => %(font-style="italic" font-weight="normal"),
    "newcmbx10" => %(font-style="normal" font-weight="bold")
  }.freeze
  GLYPH_USE = %r{\A<use x=["'](?<x>[^"']*)["'] y=["'](?<y>[^"']*)["'] (?:xlink:)?href=["']#g(?<font>\d+)-(?<char>\d+)["']/>$}
  # In thousandths of an em: more than any kern, less than any space between words.
  WORD_GAP = 160
  # The characters of TeX's text fonts (OT1), but for the accents, which have no place in a <text>.
  TEXT_CHARACTERS = (33..122).to_h { |code| [code, code.chr] }.except(94, 95).merge(
    (0..10).zip("ΓΔΘΛΞΠΣΥΦΨΩ".chars).to_h,
    { 11 => "ﬀ", 12 => "ﬁ", 13 => "ﬂ", 14 => "ﬃ", 15 => "ﬄ", 16 => "ı", 17 => "ȷ", 25 => "ß", 26 => "æ", 27 => "œ",
      28 => "ø", 29 => "Æ", 30 => "Œ", 31 => "Ø", 34 => "”", 39 => "’", 60 => "¡", 62 => "¿", 92 => "“", 96 => "‘",
      123 => "–", 124 => "—" }
  ).freeze

  class RenderError < StandardError; end

  def self.glyphs
    @glyphs ||= JSON.parse(File.read(GLYPHS_PATH))
  end

  def self.glyphs_digest
    @glyphs_digest ||= Digest::SHA256.file(GLYPHS_PATH).hexdigest
  end

  class Processor
    def initialize(site, item)
      @site = site
      @item = item
      @diagram_index = 0
      @cache_dir = File.expand_path(
        site.config.dig("tikzcd", "cache_dir") || DEFAULT_CACHE_DIR,
        site.source
      )
    end

    def render(content)
      return content unless content&.include?("tikz")

      lines = content.lines
      output = +""
      markdown = +""
      index = 0

      while index < lines.length
        opening = opening_fence(lines[index])

        unless opening
          markdown << lines[index]
          index += 1
          next
        end

        output << render_display_tikz(markdown)
        markdown.clear

        closing_index = find_closing_fence(lines, index + 1, opening[:fence])
        raise RenderError, "Unclosed fenced code block in #{item_path}" unless closing_index

        if opening[:language] == "tikzcd"
          source = lines[(index + 1)...closing_index].join
          output << render_diagram(tikzcd_environment(source), opening[:indentation])
        else
          output << lines[index..closing_index].join
        end

        index = closing_index + 1
      end

      output << render_display_tikz(markdown)
      output
    end

    private

    def opening_fence(line)
      match = line.match(/\A( {0,3})(`{3,}|~{3,})([^\r\n]*)\r?\n?\z/)
      return unless match

      {
        indentation: match[1],
        fence: match[2],
        language: match[3].strip.split(/\s+/, 2).first
      }
    end

    def find_closing_fence(lines, start_index, fence)
      marker = Regexp.escape(fence[0])
      closing_pattern = /\A {0,3}#{marker}{#{fence.length},}\s*\z/

      (start_index...lines.length).find do |index|
        lines[index].chomp.match?(closing_pattern)
      end
    end

    def render_display_tikz(markdown)
      markdown.gsub(DISPLAY_MATH_PATTERN) do |display_math|
        body = Regexp.last_match(:body)
        # The indentation of the line the formula opens on, as in a list item.
        indentation = Regexp.last_match.pre_match.rpartition("\n").last[/\A[ \t]*/]
        environment_match = body.match(TIKZ_ENVIRONMENT_PATTERN)

        if environment_match
          render_diagram(environment_match[:environment], indentation)
        elsif body.match?(TIKZ_BEGIN_PATTERN)
          render_diagram(display_formula(body), indentation)
        else
          display_math
        end
      end
    end

    # Diagrams set among other math, as in
    #   \begin{tikzcd}...\end{tikzcd} \quad \text{or} \quad \begin{tikzcd}...\end{tikzcd},
    # form one display formula. Blank lines are dropped: TeX would end the formula there.
    def display_formula(body)
      "$\\displaystyle\n#{body.strip.gsub(/\n\s*\n/, "\n")}\n$"
    end

    def tikzcd_environment(source)
      <<~LATEX.strip
        \\begin{tikzcd}
        #{source.rstrip}
        \\end{tikzcd}
      LATEX
    end

    # The figure keeps the indentation of the source it replaces, so a diagram in a list item
    # stays in that item. Unindented, it would end the list, and kramdown would start the
    # items after it as a new list, numbered from 1 again.
    def render_diagram(environment, indentation = "")
      @diagram_index += 1
      svg, digest = cached_svg(environment)
      svg = prepare_inline_svg(svg, digest, @diagram_index, diagram_title(environment))

      <<~HTML.gsub(/^(?=.)/) { indentation }

        <figure class="commutative-diagram" data-tikzcd-hash="#{digest[0, 12]}">
        #{svg}
        </figure>

      HTML
    end

    def cached_svg(environment)
      digest = Digest::SHA256.hexdigest([CACHE_VERSION, ExternalTikzcdRenderer.glyphs_digest, environment].join("\0"))
      cache_path = File.join(@cache_dir, "#{digest}.svg")

      return [File.read(cache_path), digest] if File.file?(cache_path)

      FileUtils.mkdir_p(@cache_dir)
      svg = compile_svg(environment)
      File.write(cache_path, svg)
      [svg, digest]
    end

    def compile_svg(environment)
      Dir.mktmpdir("jekyll-tikzcd-") do |directory|
        File.write(File.join(directory, "diagram.tex"), latex_document(environment))
        write_fonts(directory)

        run_command(
          ["latex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-no-shell-escape", "diagram.tex"],
          directory,
          "LaTeX"
        )
        run_command(
          ["dvisvgm", "--fontmap=+diagram.map", "--no-fonts", "--bbox=papersize", "--exact-bbox", "--output=diagram.svg", "diagram.dvi"],
          directory,
          "dvisvgm"
        )
        # Glyph paths do not record their font and its size; the font output
        # keeps them per font number, which both runs assign alike.
        run_command(
          ["dvisvgm", "--fontmap=+diagram.map", "--bbox=papersize", "--exact-bbox", "--output=fonts.svg", "diagram.dvi"],
          directory,
          "dvisvgm"
        )

        draw_characters(
          File.read(File.join(directory, "diagram.svg")),
          # Only its ASCII style sheet is read; the embedded glyphs may not be UTF-8.
          File.binread(File.join(directory, "fonts.svg"))
        )
      end
    rescue Errno::ENOENT => error
      raise RenderError,
            "#{error.message}. Install a TeX distribution providing latex and dvisvgm to render TikZ diagrams."
    end

    def run_command(command, directory, label)
      stdout, stderr, status = Open3.capture3(*command, chdir: directory)
      return if status.success?

      details = [stdout, stderr].join("\n").lines.last(35).join
      raise RenderError, "#{label} failed for #{item_path}:\n#{details}"
    end

    # The metrics the document adds to TeX's own. dvisvgm needs an outline for their characters
    # too, and takes Computer Modern's until draw_glyphs puts New Computer Modern's in its place.
    def write_fonts(directory)
      fonts = ExternalTikzcdRenderer.glyphs["tfm"]
      fonts.each { |font, tfm| File.binwrite(File.join(directory, "#{font}.tfm"), tfm.unpack1("m")) }
      File.write(
        File.join(directory, "diagram.map"),
        fonts.keys.map { |font| "#{font} #{font.delete_prefix('new').upcase} <#{font.delete_prefix('new')}.pfb\n" }.join
      )
    end

    # TeX sets the diagram in Computer Modern, and every character stays where TeX put it. The
    # text becomes text again, which the page sets in its own font, New Computer Modern; the math
    # is drawn with New Computer Modern's outlines, as MathJax draws the math around it.
    def draw_characters(svg, font_svg)
      fonts = font_svg.scan(/\btext\.f(\d+)\s*\{[^}]*\bfont-family:\s*([^;}\s]+)[^}]*\bfont-size:\s*(\d+(?:\.\d+)?)px/)
                      .to_h { |number, family, size| [number, [family, size]] }

      draw_glyphs(drop_unused(set_text(svg, fonts)), fonts)
    end

    # dvisvgm draws a character as <use x='…' y='…' xlink:href='#g<font>-<char>'/>, one to a line.
    # The characters of one font on one baseline are a run of text.
    def set_text(svg, fonts)
      svg.lines.chunk_while do |line, following|
        use, other = line.match(GLYPH_USE), following.match(GLYPH_USE)
        use && other && use[:font] == other[:font] && use[:y] == other[:y]
      end.map { |lines| text_element(lines.filter_map { |line| line.match(GLYPH_USE) }, fonts) || lines.join }.join
    end

    # A run as a <text>, with each character where TeX put it, kerns and all. TeX leaves a space
    # between words as a gap, and the words are told apart by it.
    def text_element(uses, fonts)
      family, size = fonts[uses.first[:font]] unless uses.empty?
      return unless TEXT_STYLES.key?(family) && uses.all? { |use| TEXT_CHARACTERS.key?(use[:char].to_i) }

      places = []
      text = +""
      uses.each_with_index do |use, index|
        if index.positive? && word_gap?(uses[index - 1], use, family, size.to_f)
          places << use[:x]
          text << " "
        end
        places << use[:x]
        text << TEXT_CHARACTERS[use[:char].to_i]
      end

      text = text.gsub(/[&<>]/, "&" => "&amp;", "<" => "&lt;", ">" => "&gt;")
      %(<text x="#{places.join(' ')}" y="#{uses.first[:y]}" font-size="#{size}" #{TEXT_STYLES[family]} fill="currentColor">#{text}</text>\n)
    end

    def word_gap?(use, following, family, size)
      width = ExternalTikzcdRenderer.glyphs["widths"][family][use[:char]]
      following[:x].to_f - use[:x].to_f > (width + WORD_GAP) * size / 1000
    end

    # The glyphs of what is text now are drawn no more.
    def drop_unused(svg)
      loop do
        used = svg.scan(/\bhref=["']#(g\d+-\d+)["']/).flatten
        smaller = svg.gsub(%r{^<(?:path|use) id=["'](g\d+-\d+)["'][^>]*/>\n}) { |tag| used.include?(Regexp.last_match(1)) ? tag : "" }
        return svg if smaller == svg

        svg = smaller
      end
    end

    # dvisvgm defines each glyph once, as <path id="g<font>-<char>"> at that
    # font's size, and draws other sizes of the same font through a scaled
    # <use>. Multiplying the path's stroke by its font size lets post.css give
    # the stroke per em, and the <use> scaling carries it to every size, as
    # MathJax's own glyph strokes scale with its script sizes. A glyph without
    # an outline in New Computer Modern (scripts/diagram_glyphs.py) stays
    # Computer Modern's, with the stroke that makes up for its weight.
    def draw_glyphs(svg, fonts)
      outlines = ExternalTikzcdRenderer.glyphs["glyphs"]

      svg.gsub(/<path id=(["'])g(\d+)-(\d+)\1\s+d=(["'])([^"']*)\4/) do
        quote, font, char, outline = Regexp.last_match.values_at(1, 2, 3, 5)
        raise RenderError, "dvisvgm did not report the size of font #{font} for #{item_path}" unless fonts.key?(font)

        family, size = fonts[font]
        own = outlines.dig(family, char) || outlines.dig(family.delete_prefix("new"), char)
        outline = scale_outline(own, size.to_f / 1000) if own
        stroke = own ? "--tikzcd-glyph-stroke" : "--tikzcd-cm-glyph-stroke"
        %(<path id=#{quote}g#{font}-#{char}#{quote} style="stroke-width:calc(var(#{stroke}, 0px) * #{size})" d=#{quote}#{outline}#{quote})
      end
    end

    def scale_outline(outline, factor)
      outline.gsub(/-?\d+(?:\.\d+)?/) { |number| format_number(number.to_f * factor) }
    end

    # MathJax draws sub- and superscripts by scaling its 10pt glyphs by 0.707,
    # where TeX switches to the heavier optical sizes (cmmi7, cmmi5, ...). Use
    # the 10pt designs at every size and MathJax's script sizes so that labels
    # match the surrounding math.
    #
    # A lone diagram is typeset as its own tikzpicture. A display formula has to
    # stay on one page, which the tikz option (a page per tikzpicture) would
    # prevent. A picture's box leaves out half of a line along its edge, a
    # frame's, so a picture has a border of half TikZ's line width.
    def latex_document(environment)
      diagram = environment[TIKZ_ENVIRONMENT_PATTERN, :name]
      <<~LATEX
        \\def\\pgfsysdriver{pgfsys-dvisvgm.def}
        \\documentclass[#{"tikz," if diagram}border=#{diagram == "tikzpicture" ? "0.2pt" : "0pt"}]{standalone}
        \\DeclareFontShape{OT1}{cmr}{m}{n}{<->cmr10}{}
        \\DeclareFontShape{OT1}{cmr}{m}{it}{<->cmti10}{}
        \\DeclareFontShape{OT1}{cmr}{bx}{n}{<->cmbx10}{}
        \\DeclareFontShape{OML}{cmm}{m}{it}{<->cmmi10}{}
        \\DeclareFontShape{OML}{cmm}{b}{it}{<->cmmib10}{}
        \\DeclareFontShape{OMS}{cmsy}{m}{n}{<->newcmsy10}{}
        \\DeclareFontShape{OMS}{cmsy}{b}{n}{<->cmbsy10}{}
        \\DeclareFontShape{OMX}{cmex}{m}{n}{<->cmex10}{}
        \\DeclareFontFamily{U}{msa}{}
        \\DeclareFontShape{U}{msa}{m}{n}{<->msam10}{}
        \\DeclareFontFamily{U}{msb}{}
        \\DeclareFontShape{U}{msb}{m}{n}{<->msbm10}{}
        \\DeclareMathSizes{10}{10}{7.07}{5}
        #{TEXT_FONTS if diagram == "tikzpicture"}
        \\usepackage{amsmath,amssymb}
        \\usepackage{tikz-cd}
        #{TIKZ_PREAMBLE}
        \\makeatletter
        \\def\\pgfsys@papersize#1#2{}
        \\let\\tikzcd@typesetpicturebox\\pgfsys@typesetpicturebox
        \\def\\pgfsys@typesetpicturebox#1{%
          \\pgf@sys@svg@inpicturetrue
          \\tikzcd@typesetpicturebox#1%
        }
        \\makeatother
        \\begin{document}
        #{environment}
        \\end{document}
      LATEX
    end

    def diagram_title(environment)
      return "Hasse diagram" if environment.match?(HASSE_PATTERN)

      environment.include?("{tikzcd}") ? "Commutative diagram" : "Diagram"
    end

    def prepare_inline_svg(svg, digest, index, title)
      svg = svg.sub(/\A\s*<\?xml[^>]*>\s*/m, "")
      svg = svg.sub(/\A\s*<!DOCTYPE.*?>\s*/m, "")

      id_prefix = "tikzcd-#{digest[0, 10]}-#{index}-"
      svg = namespace_svg_ids(svg, id_prefix)
      title_id = "#{id_prefix}title"

      svg.sub(/<svg\b([^>]*)>/m) do
        attributes = normalize_svg_dimensions(Regexp.last_match(1))

        <<~SVG.chomp
          <svg class="commutative-diagram__svg" role="img" aria-labelledby="#{title_id}"#{attributes}>
          <title id="#{title_id}">#{title}</title>
        SVG
      end.strip
    end

    # dvisvgm gives the page size in pt, meaning big points.
    def normalize_svg_dimensions(attributes)
      attributes.gsub(/\b(?<name>width|height)=(?<quote>["'])(?<value>\d+(?:\.\d+)?)pt\k<quote>/) do
        name = Regexp.last_match(:name)
        quote = Regexp.last_match(:quote)
        ex_value = Regexp.last_match(:value).to_f / TEX_EM_BP / MATHJAX_X_HEIGHT

        "#{name}=#{quote}#{format_number(ex_value)}ex#{quote}"
      end
    end

    def format_number(value)
      format("%.6f", value)
        .sub(/0+\z/, "")
        .sub(/\.\z/, "")
    end

    def namespace_svg_ids(svg, prefix)
      ids = svg.scan(/\bid=(["'])([^"']+)\1/).map { |match| match[1] }.uniq

      ids.each do |id|
        namespaced_id = "#{prefix}#{id}"
        svg = svg.gsub(/\bid=(["'])#{Regexp.escape(id)}\1/, %(id="#{namespaced_id}"))
        svg = svg.gsub(/(["'])##{Regexp.escape(id)}\1/, %("##{namespaced_id}"))
        svg = svg.gsub(/url\(##{Regexp.escape(id)}\)/, "url(##{namespaced_id})")
      end

      svg
    end

    def item_path
      if @item.respond_to?(:relative_path)
        @item.relative_path
      elsif @item.respond_to?(:path)
        @item.path
      else
        "Markdown document"
      end
    end
  end

  module_function

  def enabled?(site)
    (site.config["tikzcd"] || {})["enabled"] != false
  end

  def markdown_item?(item)
    path = item.respond_to?(:relative_path) ? item.relative_path : item.path
    [".md", ".markdown"].include?(File.extname(path.to_s).downcase)
  end
end

if defined?(Jekyll)
  Jekyll::Hooks.register [:pages, :documents], :pre_render do |item|
    site = item.respond_to?(:site) ? item.site : nil
    next unless site
    next unless ExternalTikzcdRenderer.enabled?(site)
    next unless ExternalTikzcdRenderer.markdown_item?(item)

    item.content = ExternalTikzcdRenderer::Processor.new(site, item).render(item.content)
  rescue ExternalTikzcdRenderer::RenderError => error
    raise Jekyll::Errors::FatalException, "TikZ rendering failed: #{error.message}"
  end
end
