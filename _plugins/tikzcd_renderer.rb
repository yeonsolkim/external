# frozen_string_literal: true

require "digest"
require "fileutils"
require "open3"
require "tmpdir"

module ExternalTikzcdRenderer
  CACHE_VERSION = "4"
  DEFAULT_CACHE_DIR = ".jekyll-cache/tikzcd"
  SVG_SCALE = 1.28
  CSS_PIXELS_PER_POINT = 4.0 / 3.0
  # assets/css/main.css: 15.5px root size times the desktop content scale.
  REFERENCE_FONT_SIZE_PX = 15.5 * 1.05
  DISPLAY_MATH_PATTERN = /\$\$(?<body>.*?)\$\$/m
  TIKZCD_ENVIRONMENT_PATTERN = /\A\s*(?<environment>\\begin\s*\{tikzcd\}(?:\[[^\]\r\n]*\])?.*?\\end\s*\{tikzcd\})\s*\z/m

  class RenderError < StandardError; end

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
      return content unless content&.include?("tikzcd")

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

        output << render_display_tikzcd(markdown)
        markdown.clear

        closing_index = find_closing_fence(lines, index + 1, opening[:fence])
        raise RenderError, "Unclosed fenced code block in #{item_path}" unless closing_index

        if opening[:language] == "tikzcd"
          source = lines[(index + 1)...closing_index].join
          output << render_diagram(tikzcd_environment(source))
        else
          output << lines[index..closing_index].join
        end

        index = closing_index + 1
      end

      output << render_display_tikzcd(markdown)
      output
    end

    private

    def opening_fence(line)
      match = line.match(/\A {0,3}(`{3,}|~{3,})([^\r\n]*)\r?\n?\z/)
      return unless match

      {
        fence: match[1],
        language: match[2].strip.split(/\s+/, 2).first
      }
    end

    def find_closing_fence(lines, start_index, fence)
      marker = Regexp.escape(fence[0])
      closing_pattern = /\A {0,3}#{marker}{#{fence.length},}\s*\z/

      (start_index...lines.length).find do |index|
        lines[index].chomp.match?(closing_pattern)
      end
    end

    def render_display_tikzcd(markdown)
      markdown.gsub(DISPLAY_MATH_PATTERN) do |display_math|
        body = Regexp.last_match(:body)
        environment_match = body.match(TIKZCD_ENVIRONMENT_PATTERN)

        if environment_match
          render_diagram(environment_match[:environment])
        else
          display_math
        end
      end
    end

    def tikzcd_environment(source)
      <<~LATEX.strip
        \\begin{tikzcd}
        #{source.rstrip}
        \\end{tikzcd}
      LATEX
    end

    def render_diagram(environment)
      @diagram_index += 1
      svg, digest = cached_svg(environment)
      svg = prepare_inline_svg(svg, digest, @diagram_index)

      <<~HTML

        <figure class="commutative-diagram" data-tikzcd-hash="#{digest[0, 12]}">
        #{svg}
        </figure>

      HTML
    end

    def cached_svg(environment)
      digest = Digest::SHA256.hexdigest([CACHE_VERSION, environment].join("\0"))
      cache_path = File.join(@cache_dir, "#{digest}.svg")

      return [File.read(cache_path), digest] if File.file?(cache_path)

      FileUtils.mkdir_p(@cache_dir)
      svg = compile_svg(environment)
      File.write(cache_path, svg)
      [svg, digest]
    end

    def compile_svg(environment)
      Dir.mktmpdir("jekyll-tikzcd-") do |directory|
        tex_path = File.join(directory, "diagram.tex")
        File.write(tex_path, latex_document(environment))

        run_command(
          ["latex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-no-shell-escape", "diagram.tex"],
          directory,
          "LaTeX"
        )
        run_command(
          ["dvisvgm", "--no-fonts", "--bbox=papersize", "--exact-bbox", "--output=diagram.svg", "diagram.dvi"],
          directory,
          "dvisvgm"
        )

        File.read(File.join(directory, "diagram.svg"))
      end
    rescue Errno::ENOENT => error
      raise RenderError,
            "#{error.message}. Install a TeX distribution providing latex and dvisvgm to render tikzcd blocks."
    end

    def run_command(command, directory, label)
      stdout, stderr, status = Open3.capture3(*command, chdir: directory)
      return if status.success?

      details = [stdout, stderr].join("\n").lines.last(35).join
      raise RenderError, "#{label} failed for #{item_path}:\n#{details}"
    end

    def latex_document(environment)
      <<~LATEX
        \\def\\pgfsysdriver{pgfsys-dvisvgm.def}
        \\documentclass[tikz,border=0pt]{standalone}
        \\usepackage{tikz-cd}
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

    def prepare_inline_svg(svg, digest, index)
      svg = svg.sub(/\A\s*<\?xml[^>]*>\s*/m, "")
      svg = svg.sub(/\A\s*<!DOCTYPE.*?>\s*/m, "")

      id_prefix = "tikzcd-#{digest[0, 10]}-#{index}-"
      svg = namespace_svg_ids(svg, id_prefix)
      title_id = "#{id_prefix}title"

      svg.sub(/<svg\b([^>]*)>/m) do
        attributes = normalize_svg_dimensions(Regexp.last_match(1))

        <<~SVG.chomp
          <svg class="commutative-diagram__svg" role="img" aria-labelledby="#{title_id}"#{attributes}>
          <title id="#{title_id}">Commutative diagram</title>
        SVG
      end.strip
    end

    def normalize_svg_dimensions(attributes)
      attributes.gsub(/\b(?<name>width|height)=(?<quote>["'])(?<value>\d+(?:\.\d+)?)(?<unit>[a-zA-Z%]*)\k<quote>/) do
        name = Regexp.last_match(:name)
        quote = Regexp.last_match(:quote)
        value = Regexp.last_match(:value).to_f
        unit = Regexp.last_match(:unit)

        if unit.casecmp("pt").zero?
          em_value = value * SVG_SCALE * CSS_PIXELS_PER_POINT / REFERENCE_FONT_SIZE_PX
          "#{name}=#{quote}#{format_number(em_value)}em#{quote}"
        else
          "#{name}=#{quote}#{format_number(value * SVG_SCALE)}#{unit}#{quote}"
        end
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
    raise Jekyll::Errors::FatalException, "TikZ-cd rendering failed: #{error.message}"
  end
end
