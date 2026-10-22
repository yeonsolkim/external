#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for post URLs and the redirects from old ones (_plugins/permalinks.rb). The cases are
# those of _tests/test_sync_front_matter.py, which freezes the same URLs into front matter.
#
#   ruby _tests/test_permalinks.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

require "jekyll"
require_relative "../_plugins/permalinks"

P = ExternalPermalinks
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

ANALYSIS = ["1. Mathematics", "3. Mathematical Analysis", "1. Introduction to Analysis"].freeze
CASES = [
  ["vector spaces", ["1. Mathematics", "2. Algebra", "1. Linear Algebra", "1. Vector Spaces"],
   "1. Vector Spaces", "/linear-algebra/vector-spaces/"],
  ["zf", ["1. Mathematics", "1. Foundations of Mathematics", "3. Axiomatic Set Theory"],
   "1. Axioms of Zermelo–Fraenkel Theory", "/foundations-of-mathematics/axioms-of-zermelo-fraenkel-theory/"],
  ["putnam", ["1. Mathematics", "6. Others"], "The 62nd Putnam", "/mathematics/the-62nd-putnam/"],
  ["questions", ["1. Mathematics", "6. Others", "Questions"], "Linear Algebra",
   "/mathematics/questions/linear-algebra/"],
  ["conditional", ["3. English", "1. Grammar"], "Conditional", "/grammar/conditional/"],
  ["naive", ["1. Mathematics", "Naïve Set Theory"], "1. Sets", "/naive-set-theory/sets/"],
  ["metric", ANALYSIS + ["2. Metric Spaces"], "Exercises", "/introduction-to-analysis/exercises-metric-spaces/"],
  ["ordered", ANALYSIS + ["1. Algebraic and Ordered Structures"], "Exercises",
   "/introduction-to-analysis/exercises-algebraic-and-ordered-structures/"]
].freeze

puts "derived URLs"
derived = P.derive(CASES.map { |key, path, title, _| [key, path, title, "2026-01-01", nil] })
CASES.each do |key, _, _, url|
  check("#{key}: #{url}") { derived[key] == url }
end

puts "frozen URLs"
check("a frozen permalink keeps its URL; a new post of the same name takes its section") do
  P.derive([["old", ANALYSIS + ["2. Metric Spaces"], "Exercises", "2026-01-01", "/introduction-to-analysis/exercises/"],
            ["new", ANALYSIS + ["3. Sequences"], "Exercises", "2026-01-02", nil]]) ==
    { "new" => "/introduction-to-analysis/exercises-sequences/" }
end
check("without a section the date tells two posts apart") do
  P.derive([["a", ["3. English", "1. Grammar"], "Notes", "2026-01-01", nil],
            ["b", ["3. English", "1. Grammar"], "Notes", "2026-01-02", nil]]) ==
    { "a" => "/grammar/notes-2026-01-01/", "b" => "/grammar/notes-2026-01-02/" }
end

puts "redirect pages"
page = P.redirect_html("https://example.test/linear-algebra/vector-spaces/")
check("an instant refresh, a canonical link and noindex") do
  page.include?('<meta http-equiv="refresh" content="0; url=https://example.test/linear-algebra/vector-spaces/">') &&
    page.include?('<link rel="canonical" href="https://example.test/linear-algebra/vector-spaces/">') &&
    page.include?('<meta name="robots" content="noindex">')
end
check("not a post, so the narration leaves it alone") { !page.include?('<article class="post"') }

site = Jekyll::Site.new(Jekyll.configuration("quiet" => true, "source" => File.expand_path("..", __dir__)))
check("a directory URL writes index.html") do
  redirect = Jekyll::RedirectPage.new(site, "/group-theory/axioms-and-examples/", "/linear-algebra/axioms-and-examples/")
  redirect.destination("") == File.join(site.dest, "group-theory/axioms-and-examples/index.html")
end
check("an HTML URL keeps its filename") do
  redirect = Jekyll::RedirectPage.new(site, "/2026/08/31/1.-Axioms-and-Examples.html", "/linear-algebra/axioms-and-examples/")
  redirect.destination("") == File.join(site.dest, "2026/08/31/1.-Axioms-and-Examples.html")
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
