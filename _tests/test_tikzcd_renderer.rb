#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for where the tikzcd renderer puts a diagram in the Markdown around it, checked on
# kramdown's HTML. LaTeX is not run: a stand-in SVG takes the place of the compiled one.
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

def title(markdown)
  html(markdown)[%r{<title[^>]*>(.*?)</title>}, 1]
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

puts "titles"
check("a tikzcd diagram is a commutative diagram") { title(DIAGRAM) == "Commutative diagram" }
check("a tikzpicture is a diagram") { title(PICTURE) == "Diagram" }
check("the hasse style makes it a Hasse diagram") { title(HASSE_DIAGRAM) == "Hasse diagram" }
check("the hasse style may sit among other options") do
  title(PICTURE.sub("{tikzpicture}", "{tikzpicture}[scale=.7, hasse]")) == "Hasse diagram"
end
check("pictures among other math keep the style's title") { title(PICTURES_AMONG_MATH) == "Hasse diagram" }

puts "math in node text"
[0, 3, 4, 5].each do |spaces|
  check("it reaches LaTeX from a block indented #{spaces} spaces") do
    markdown = "1. item\n\n#{indent(PICTURE, spaces)}\nAfter $b$.\n"
    environments_after_inline_math(markdown).first&.include?("{$a$}")
  end
end

puts "documents"
check("a lone tikzpicture is typeset as its own picture") do
  processor.send(:latex_document, "\\begin{tikzpicture}\n\\end{tikzpicture}").include?("[tikz,border=0pt]")
end
check("two pictures in a formula stay on one page") do
  renderer = processor
  renderer.render(PICTURES_AMONG_MATH)
  !renderer.send(:latex_document, renderer.environments.first).include?("[tikz,")
end
check("the Obsidian plugin adds to TikZ what the site's documents add") do
  File.read(File.expand_path("../_posts/.obsidian/plugins/tikzcd-preview/main.js", __dir__))
      .include?("String.raw`\n#{ExternalTikzcdRenderer::TIKZ_PREAMBLE}\n`")
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
