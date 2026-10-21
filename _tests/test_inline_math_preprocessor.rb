#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for where the inline-math preprocessor puts the math back, checked on the HTML the
# structure pass leaves: a placeholder in the text becomes a span, one in an attribute TeX.
#
#   ruby _tests/test_inline_math_preprocessor.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

module Jekyll
  module Hooks
    def self.register(*); end
  end

  def self.logger
    @logger ||= Object.new.tap { |o| def o.warn(*); end }
  end

  module Converters
    class Markdown; end
  end
end

require_relative "../_plugins/inline_math_preprocessor"
require_relative "../_plugins/document_structure"

M = ExternalInlineMathPreprocessor
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

# Restored the way a build restores it: after the structure pass has copied the label.
def build(html, placeholders)
  M.restore(ExternalDocumentStructure.transform(html, []), placeholders)
end

puts "text"
check("math in the text becomes a span, keeping the punctuation after it") do
  M.restore(%(<p>Let @@codex-inline-math-0@@.</p>), ["x"]) ==
    %(<p>Let <span class="math-inline math-inline-punctuated">\\(x\\).</span></p>)
end

puts "attributes"
named = build(%(<p><strong>Theorem 1.1.9 (Archimedean property of @@codex-inline-math-0@@).</strong> ) +
              %(For all @@codex-inline-math-1@@ there is n.</p>), ["\\mathbb R", "x\\in \\mathbb R"])
check("math in a statement's name stays inside data-name, and the tag stays whole") do
  named.include?(%(data-name="Archimedean property of \\(\\mathbb R\\)" ) +
                 %(id="unit-theorem-1-1-9" aria-labelledby="theorem-1-1-9">))
end
check("the label and the statement still get spans") do
  named.include?('<span class="math-statement-name">(Archimedean property of <span class="math-inline') &&
    named.include?(%(<span class="math-inline">\\(x\\in \\mathbb R\\)</span>))
end
check("no attribute is left holding markup") do
  named.scan(/="([^"]*)"/).flatten.none? { |value| value.include?("<") }
end

titled = build(%(<p><strong>Span of @@codex-inline-math-0@@.</strong> Text.</p>), ["S"])
check("math in a run-in title stays inside data-title") do
  titled.include?(%(data-title="Span of \\(S\\)"))
end

check("an attribute gets the TeX escaped for it") do
  M.restore(%(<section data-name="@@codex-inline-math-0@@">x</section>), [%(a<b \\text{"c"} & d)]) ==
    %(<section data-name="\\(a&lt;b \\text{&quot;c&quot;} &amp; d\\)">x</section>)
end
check("a value may hold > before the math") do
  M.restore(%(<section data-name="x > 0, @@codex-inline-math-0@@">@@codex-inline-math-0@@</section>), ["y"]) ==
    %(<section data-name="x > 0, \\(y\\)"><span class="math-inline">\\(y\\)</span></section>)
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
