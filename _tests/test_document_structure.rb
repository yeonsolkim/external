#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for the document-structure pass. The whole site's markup now depends on it, so the
# rules in _docs/STRUCTURE.md are pinned here rather than checked by eye.
#
#   ruby _tests/test_document_structure.rb
#
# It lives outside _plugins/ on purpose: Jekyll loads every .rb file in there, so a test
# file placed beside the plugin runs — and exits — in the middle of a site build.

module Jekyll
  module Hooks
    def self.register(*); end
  end

  def self.logger
    @logger ||= Object.new.tap { |o| def o.warn(*); end }
  end
end

require_relative "../_plugins/document_structure"

D = ExternalDocumentStructure
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

def build(html)
  D.transform(html, [])
end

def text(html)
  html.gsub(/<[^>]*>/, " ").gsub(/\s+/, " ").strip
end

# The <section> tree, as "kind:number" paths.
def tree(html)
  out = []
  depth = 0
  html.scan(%r{<section\b([^>]*)>|</section>}) do
    attrs = Regexp.last_match(1)
    if attrs
      kind = attrs[/data-doc="([^"]*)"/, 1]
      number = attrs[/data-number="([^"]*)"/, 1]
      out << ("  " * depth) + [kind, number].compact.join(" ")
      depth += 1
    else
      depth -= 1
    end
  end
  out
end

puts "sectioning"
nested = build(<<~HTML)
  <p><strong>1. First.</strong> Body.</p>
  <p><strong>1.1. Inner.</strong> More.</p>
  <p><strong>2. Second.</strong> Body.</p>
HTML
check("a deeper number nests, a shallower one closes") do
  tree(nested) == ["subsection 1", "  subsubsection 1.1", "subsection 2"]
end
check("the label becomes a heading") do
  nested.include?('role="heading"') && nested.include?('aria-level="3"') && nested.include?('id="sec-1-1"')
end

heading = build(%(<p>Intro.</p><h2 id="references">References</h2><ol class="reference"><li>x</li></ol>))
check("a heading opens its own section and the intro stays outside") do
  tree(heading) == ["section"] && heading.index("<p>Intro.</p>") < heading.index("<section")
end

puts "environments"
statement = build(<<~HTML)
  <p><strong>Theorem 2.2.3.</strong> A statement.</p>
  <p><em>Proof.</em> An argument.<span class="qed" data-environment-end="proof">x</span></p>
  <p>Prose after the proof.</p>
HTML
check("a proof is a sibling that points at what it proves") do
  tree(statement) == ["theorem 2.2.3", "proof"] &&
    statement.include?('data-proves="theorem-2-2-3"') &&
    statement.include?('id="proof-theorem-2-2-3"')
end
check("prose after a closed proof is outside both") do
  statement.rindex("Prose after the proof.") > statement.rindex("</section>")
end
check("the statement keeps the id every existing link uses") do
  statement.include?('id="theorem-2-2-3"') && statement.include?('aria-labelledby="theorem-2-2-3"')
end

tight = build(%(<p><strong>Definition 1.</strong> A definition.</p><p>Ordinary prose.</p>))
check("a plain paragraph closes a statement") do
  tight.index("Ordinary prose.") > tight.index("</section>")
end

bridged = build(%(<p><strong>Definition 1.</strong> Text.</p><figure>d</figure><p>Still the definition.</p>))
check("a figure bridges to the paragraph after it") do
  bridged.index("Still the definition.") < bridged.index("</section>")
end

named = build(%(<p><strong>Theorem 2.2.20</strong> (Heine–Borel theorem). Statement.</p>))
check("a parenthesised name is captured") { named.include?('data-name="Heine–Borel theorem"') }

unnumbered = build(%(<p><strong>Remark.</strong> Something.</p>))
check("an unnumbered kind still makes a unit") do
  unnumbered.include?('data-doc="remark"') && unnumbered.include?('id="math-remark-1"')
end

in_part = build(<<~HTML)
  <p><strong>7. Pascal's identity.</strong> A claim.</p>
  <p><em>Proof.</em> An argument.<span data-environment-end="proof">x</span></p>
HTML
check("a proof with no statement before it proves the part it is in") do
  in_part.include?('data-proves="sec-7"') && in_part.include?('id="proof-sec-7"')
end

puts "what must not change"
source = <<~HTML
  <p><strong>1. Part.</strong> Body with <span class="math-inline">\\(x\\)</span>.</p>
  <p><strong>Theorem 1.1.</strong> A statement.</p>
  <p><em>Proof.</em> Done.<span data-environment-end="proof">x</span></p>
  <h2 id="references">References</h2>
HTML
check("no text is added, removed or reordered") { text(build(source)) == text(source) }
check("every section opened is closed") do
  built = build(source)
  built.scan(/<section\b/).length == built.scan(%r{</section>}).length
end

puts "numbering is read, not generated"
warnings = []
D.transform(<<~HTML, warnings)
  <p><strong>Definition 2.2.1.</strong> a</p>
  <p><strong>Theorem 2.2.2.</strong> b</p>
  <p><strong>Exercise 2.2.1.</strong> c</p>
HTML
check("statements share a counter, exercises keep their own") { warnings.empty? }

warnings = []
D.transform(%(<p><strong>Theorem 3.</strong> a</p><p><strong>Definition 2.</strong> b</p>), warnings)
check("a number that goes backwards is reported") { warnings.length == 1 }

puts "domain"
document = Struct.new(:data, :content, :collection, :relative_path).new(
  { "category_path" => ["3. English", "2. Dictionary"] }, "<p><strong>1. Word.</strong> x</p>",
  Struct.new(:label).new("posts"), "x.md"
)
D.process(document)
check("outside mathematics and physics nothing is wrapped") do
  !document.content.include?("<section") && document.data["document_structure"].nil?
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
