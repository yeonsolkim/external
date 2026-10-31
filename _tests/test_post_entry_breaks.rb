#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for the QED spans of the entry-break pass: the environment end it records on each, and
# the space it drops before each, as amsthm's \qed does with \unskip.
#
#   ruby _tests/test_post_entry_breaks.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

require_relative "../_plugins/post_entry_breaks"

B = ExternalPostEntryBreaks
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

# The pass sees inline math as placeholders (inline_math_preprocessor.rb runs first).
QED = %(<span class="qed">@@codex-inline-math-0@@</span>)
MARKED = %(<span data-environment-end="proof" class="qed">@@codex-inline-math-0@@</span>)
SQUARE = ["\\square"].freeze

puts "environment ends"
check("a QED span with \\square ends a proof") do
  B.mark("Hence it is linear.#{QED}\n", SQUARE) == "Hence it is linear.#{MARKED}\n"
end
check("a QED span with \\blacksquare ends a subproof") do
  B.mark("Done.#{QED}\n", ["\\blacksquare"]) ==
    %(Done.<span data-environment-end="subproof" class="qed">@@codex-inline-math-0@@</span>\n)
end

puts "\\unskip"
check("the space before a QED span is dropped") do
  B.mark("Hence it is linear. #{QED}\n", SQUARE) == "Hence it is linear.#{MARKED}\n"
end
check("so are several spaces and tabs") do
  B.mark("Hence it is linear. \t #{QED}\n", SQUARE) == "Hence it is linear.#{MARKED}\n"
end
check("after inline math as after a word") do
  B.mark("on @@codex-inline-math-1@@. #{QED}\n", SQUARE + ["A"]) ==
    "on @@codex-inline-math-1@@.#{MARKED}\n"
end
check("a span already marked is closed up all the same") do
  B.mark("Hence it is linear. #{MARKED}\n", SQUARE) == "Hence it is linear.#{MARKED}\n"
end
check("a span that opens its line keeps the indentation before it") do
  B.mark("   #{QED}\n", SQUARE) == "   #{MARKED}\n"
end
check("the space before any other span stays") do
  B.mark(%(see <span class="name">x</span>\n)) == %(see <span class="name">x</span>\n)
end
check("a fenced code block is left as written") do
  source = "```\nHence it is linear. #{QED}\n```\n"
  B.mark(source, SQUARE) == source
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
