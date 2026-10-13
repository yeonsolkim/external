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
  private

  def cached_svg(environment)
    svg = %(<svg width="20pt" height="10pt" viewBox="0 0 20 10">\n<path d="M0 5H20"/>\n</svg>)
    [svg, Digest::SHA256.hexdigest(environment)]
  end
end

Site = Struct.new(:config, :source)
Item = Struct.new(:relative_path)

# Jekyll's kramdown settings: GFM input, its default, and the site's math engine.
def html(markdown)
  rendered = StubProcessor.new(Site.new({}, Dir.pwd), Item.new("test.md")).render(markdown)
  Kramdown::Document.new(rendered, input: "GFM", hard_wrap: false, math_engine: "mathjax").to_html
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

puts "list items"
{ "a display formula" => DIAGRAM,
  "a fenced block" => FENCED_DIAGRAM,
  "a formula with diagrams among other math" => DIAGRAMS_AMONG_MATH }.each do |form, block|
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

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
