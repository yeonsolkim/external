#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for where the tikzcd renderer puts a diagram in the Markdown around it, checked on
# kramdown's HTML, and for how it draws the characters in one. LaTeX is not run: a stand-in SVG
# takes the place of the compiled one.
#
#   ruby _tests/test_tikzcd_renderer.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

require "kramdown"
require "kramdown-parser-gfm"
require_relative "../_plugins/inline_math_preprocessor"
require_relative "../_plugins/tikzcd_renderer"

$failures = 0

def check(label)
  result = yield
  if result
    puts "  ok   #{label}"
  else
    $failures += 1
    puts "  FAIL #{label}"
  end
rescue StandardError => e
  $failures += 1
  puts "  FAIL #{label} — #{e.class}: #{e.message}"
end

class StubProcessor < ExternalTikzcdRenderer::Processor
  # What LaTeX would have been given.
  def environments
    @environments ||= []
  end

  private

  def cached_svg(environment)
    environments << environment
    svg = %(<svg width="20pt" height="10pt" viewBox="0 0 20 10">\n<path d="M0 5H20"/>\n</svg>)
    [svg, Digest::SHA256.hexdigest(environment)]
  end
end

Site = Struct.new(:config, :source)
Item = Struct.new(:relative_path)

# Jekyll's kramdown settings: GFM input, its default, and the site's math engine.
def processor
  StubProcessor.new(Site.new({}, Dir.pwd), Item.new("test.md"))
end

def html(markdown)
  Kramdown::Document.new(processor.render(markdown), input: "GFM", hard_wrap: false, math_engine: "mathjax").to_html
end

def name(markdown)
  html(markdown)[/<svg [^>]*aria-label="([^"]*)"/, 1]
end

# The diagrams of a page, as the build gets them: after the inline-math step.
def environments_after_inline_math(markdown)
  renderer = processor
  renderer.render(ExternalInlineMathPreprocessor.protect(markdown).first)
  renderer.environments
end

def indent(block, spaces)
  block.gsub(/^(?=.)/, " " * spaces)
end

def list_around(block)
  "1. first\n\n2. second\n\n#{indent(block, 3)}\n3. third\n"
end

def figure_in_item?(html, number)
  items = html.scan(%r{<li>(.*?)</li>}m).flatten
  items.each_index.map { |index| items[index].include?("commutative-diagram") } ==
    items.each_index.map { |index| index == number - 1 }
end

DIAGRAM = <<~'MD'
  $$
  \begin{tikzcd}
  A \arrow[r] & B
  \end{tikzcd}
  $$
MD

FENCED_DIAGRAM = <<~'MD'
  ```tikzcd
  A \arrow[r] & B
  ```
MD

DIAGRAMS_AMONG_MATH = <<~'MD'
  $$
  \begin{tikzcd}
  A \arrow[r] & B
  \end{tikzcd}
  \quad \text{or} \quad
  \begin{tikzcd}
  B \arrow[r] & A
  \end{tikzcd}
  $$
MD

PICTURE = <<~'MD'
  $$
  \begin{tikzpicture}
  \node (a) at (0,0) {$a$};
  \end{tikzpicture}
  $$
MD

HASSE_DIAGRAM = PICTURE.sub("{tikzpicture}", "{tikzpicture}[hasse]")

PICTURES_AMONG_MATH = <<~'MD'
  $$
  \begin{tikzpicture}[hasse]
  \node (a) at (0,0) {$a$};
  \end{tikzpicture}
  \quad \text{and} \quad
  \begin{tikzpicture}[hasse]
  \node (b) at (0,0) {$b$};
  \end{tikzpicture}
  $$
MD

puts "list items"
{ "a display formula" => DIAGRAM,
  "a fenced block" => FENCED_DIAGRAM,
  "a formula with diagrams among other math" => DIAGRAMS_AMONG_MATH,
  "a tikzpicture" => PICTURE,
  "a formula with tikzpictures among other math" => PICTURES_AMONG_MATH }.each do |form, block|
  output = html(list_around(block))
  check("#{form} in an item stays in that item") { figure_in_item?(output, 2) }
  check("#{form} in an item does not restart the list") do
    output.scan("<ol>").size == 1 && output.scan("<li>").size == 3
  end
end

nested = html("1. outer\n\n   - inner\n\n#{indent(DIAGRAM, 5)}\n   - inner again\n\n2. outer again\n")
check("a diagram in a nested item stays in it") do
  inner = nested[%r{<ul>(.*?)</ul>}m, 1].to_s
  figure_in_item?(inner, 1) && nested.scan("<ol>").size == 1 && nested.scan("<li>").size == 4
end

puts "top level"
top = html("Text.\n\n#{DIAGRAM}\nMore text.\n")
check("a diagram between paragraphs stays a block of its own") do
  top.match?(/^<figure class="commutative-diagram"/) && !top.include?("<pre") &&
    top.scan("<p>").size == 2
end
check("a tikzpicture is rendered in a page that has no tikzcd") do
  html("Text.\n\n#{PICTURE}\nMore text.\n").match?(/^<figure class="commutative-diagram"/)
end
check("a tikzpicture's options may run over several lines") do
  picture = "\\begin{tikzpicture}[\n  scale=.7\n]\n\\end{tikzpicture}"
  environments_after_inline_math("$$\n#{picture}\n$$\n") == [picture]
end

puts "names"
check("a tikzcd diagram is a commutative diagram") { name(DIAGRAM) == "Commutative diagram" }
check("a tikzpicture is a diagram") { name(PICTURE) == "Diagram" }
check("the hasse style makes it a Hasse diagram") { name(HASSE_DIAGRAM) == "Hasse diagram" }
check("the hasse style may sit among other options") do
  name(PICTURE.sub("{tikzpicture}", "{tikzpicture}[scale=.7, hasse]")) == "Hasse diagram"
end
check("pictures among other math keep the style's name") { name(PICTURES_AMONG_MATH) == "Hasse diagram" }
check("no diagram has a title, which a browser would show in a tooltip") do
  [DIAGRAM, FENCED_DIAGRAM, DIAGRAMS_AMONG_MATH, PICTURE, HASSE_DIAGRAM, PICTURES_AMONG_MATH]
    .none? { |markdown| html(markdown).match?(/<title|\btitle=/) }
end
check("the Obsidian plugin gives a diagram nothing Obsidian or Chromium shows in a tooltip") do
  plugin = File.read(File.expand_path("../_posts/.obsidian/plugins/tikzcd-preview/main.js", __dir__), encoding: "UTF-8")
  !plugin.match?(/createElementNS\([^)]*"title"|setAttribute\(\s*"(?:aria-label|title)"/)
end

puts "math in node text"
[0, 3, 4, 5].each do |spaces|
  check("it reaches LaTeX from a block indented #{spaces} spaces") do
    markdown = "1. item\n\n#{indent(PICTURE, spaces)}\nAfter $b$.\n"
    environments_after_inline_math(markdown).first&.include?("{$a$}")
  end
end

puts "documents"
check("a lone tikzpicture is typeset as its own picture, with the whole of a frame's line") do
  processor.send(:latex_document, "\\begin{tikzpicture}\n\\end{tikzpicture}").include?("[tikz,border=0.2pt]")
end
check("two pictures in a formula stay on one page") do
  renderer = processor
  renderer.render(PICTURES_AMONG_MATH)
  !renderer.send(:latex_document, renderer.environments.first).include?("[tikz,")
end
check("the text of a tikzpicture, and of nothing else, has the size of the page's") do
  text = "\\renewcommand\\rmdefault{posttext}"
  renderer = processor
  renderer.render(PICTURES_AMONG_MATH)
  processor.send(:latex_document, "\\begin{tikzpicture}\n\\end{tikzpicture}").include?(text) &&
    !processor.send(:latex_document, "\\begin{tikzcd}\n\\end{tikzcd}").include?(text) &&
    !renderer.send(:latex_document, renderer.environments.first).include?(text)
end
check("the Obsidian plugin adds to TikZ what the site's documents add") do
  File.read(File.expand_path("../_posts/.obsidian/plugins/tikzcd-preview/main.js", __dir__))
      .include?("String.raw`\n#{ExternalTikzcdRenderer::TIKZ_PREAMBLE}\n`")
end

puts "characters"
DVISVGM_FONTS = <<~CSS
  text.f0 {font-family:newcmsy10;font-size:10px}
  text.f1 {font-family:newcmr10;font-size:10px}
  text.f2 {font-family:cmtt10;font-size:5px}
CSS

# What dvisvgm writes: the glyphs, then each place one is drawn.
def drawn(*uses)
  glyphs = uses.map(&:last).uniq.map { |glyph| "<path id='#{glyph}' d='M1 1H2Z'/>\n" }
  places = uses.map { |x, y, glyph| "<use x='#{x}' y='#{y}' xlink:href='##{glyph}'/>\n" }
  processor.send(:draw_characters, "<defs>\n#{glyphs.join}</defs>\n<g>\n#{places.join}</g>\n", DVISVGM_FONTS)
end

symbol = drawn([3, 4, "g0-66"])
check("a symbol keeps its place and takes New Computer Modern's outline at its font's size") do
  symbol.include?("<use x='3' y='4' xlink:href='#g0-66'/>") && symbol.include?("d='M5.77-3.88V-3.9C6.66-4.33")
end
check("it takes MathJax's stroke at that size") do
  symbol.include?(%(style="stroke-width:calc(var(--tikzcd-glyph-stroke, 0px) * 10)"))
end
check("a glyph without such an outline stays Computer Modern's, with a stroke that makes up its weight") do
  drawn([3, 4, "g2-66"]).include?(
    %(<path id='g2-66' style="stroke-width:calc(var(--tikzcd-cm-glyph-stroke, 0px) * 5)" d='M1 1H2Z'/>)
  )
end
words = drawn([0, 5, "g1-65"], [7.5, 5, "g1-38"], [20, 5, "g1-66"], [0, 17, "g1-12"])
check("text is text again, its characters where TeX put them, its words apart, a line to an element") do
  attributes = %(font-size="10" font-style="normal" font-weight="normal" fill="currentColor")
  words.include?(%(<text x="0 7.5 20 20" y="5" #{attributes}>A&amp; B</text>\n<text x="0" y="17" #{attributes}>ﬁ</text>\n))
end
check("the glyphs of the text are gone") { !words.include?("g1-") }
check("text with an accent, which no <text> can place, stays drawn") do
  accented = drawn([0, 5, "g1-19"], [0, 5, "g1-101"])
  accented.include?("<use x='0' y='5' xlink:href='#g1-19'/>") && !accented.include?("<text")
end
check("text and math side by side keep to themselves") do
  mixed = drawn([0, 5, "g1-65"], [10, 5, "g0-66"], [20, 5, "g1-66"])
  mixed.scan("<text").size == 2 && mixed.scan("<use").size == 1
end

puts "glyph data"
data = ExternalTikzcdRenderer.glyphs
check("every outline is a path the renderer can scale") do
  data["glyphs"].values.flat_map(&:values).all? { |outline| outline.match?(/\A(?:[MLHVCSZ](?:-?\d+(?:\.\d+)?(?: |(?=-|[A-Z]|\z)))*)+\z/) }
end
check("the metrics are whole TFM files") do
  data["tfm"].values.all? { |tfm| (bytes = tfm.unpack1("m")).unpack1("n") * 4 == bytes.bytesize }
end
check("the calligraphic capitals and the fonts of a picture's text are there") do
  (65..90).all? { |code| data["glyphs"]["newcmsy10"].key?(code.to_s) } &&
    ExternalTikzcdRenderer::TEXT_STYLES.keys.all? { |font| data["tfm"].key?(font) && data["widths"].key?(font) }
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
