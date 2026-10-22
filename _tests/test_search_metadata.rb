#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for the search metadata: math written out as text (tex_text.rb), and the titles,
# descriptions and section neighbours search_metadata.rb gives the pages.
#
#   ruby _tests/test_search_metadata.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

module Jekyll
  module Hooks
    def self.register(*); end
  end

  def self.logger
    @logger ||= Object.new.tap { |o| def o.warn(*); end }
  end
end

module Liquid
  module Template
    def self.register_filter(*); end
  end
end

require_relative "../_plugins/search_metadata"

T = ExternalTexText
S = ExternalSearchMetadata
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

puts "math as text"
{
  'X\times Y' => "X × Y",
  'f\colon V\to W' => "f: V → W",
  'x_1,\dots,x_k' => "x₁, …, xₖ",
  '\mathbb R^k' => "ℝᵏ",
  '\mathbb Z^{+}' => "ℤ⁺",
  '\mathcal{L}' => "ℒ",
  '(M,d)' => "(M, d)",
  '-\infty' => "−∞",
  '\{x^k: 0\le k\le n\}' => "{xᵏ : 0 ≤ k ≤ n}",
  '\operatorname{span}(S)=V' => "span(S) = V",
  '|A|=n' => "|A| = n",
  '\forall x\in A \ \neg(x<x)' => "∀x ∈ A ¬(x < x)",
  '\frac{1}{2y}' => "1/(2y)",
  'a\equiv b\pmod{n}' => "a ≡ b (mod n)",
  'A,' => "A,"
}.each do |tex, text|
  check("#{tex} reads #{text}") { T.convert(tex) == text }
end
['0_V', '\whitestar', '\lim_{n\to\infty} x_n', 'a & b', '\begin{pmatrix}', '\sqrt[3]{x}', 'x}'].each do |tex|
  check("#{tex} has no text form") { T.convert(tex).nil? }
end

puts "post titles"
check("a numbered post is titled by its textbook") do
  S.post_title_candidates("1. Axioms and Examples",
                          ["1. Mathematics", "2. Algebra", "2. Abstract Algebra", "1. Group Theory", "1. Groups"]).first ==
    "Axioms and Examples — Group Theory"
end
check("a post filed under a second-level category is titled by it") do
  S.post_title_candidates("Conditional", ["3. English", "1. Grammar"]).first == "Conditional — Grammar"
end
check("Others names nothing, so the level above stands in") do
  S.post_title_candidates("Manifolds", ["1. Mathematics", "6. Others"]).first == "Manifolds — Mathematics"
end
check("then the section, then both") do
  S.post_title_candidates("Exercises", ["1. Mathematics", "3. Mathematical Analysis",
                                        "1. Introduction to Analysis", "2. Metric Spaces"]) ==
    ["Exercises — Introduction to Analysis", "Exercises — Metric Spaces",
     "Exercises — Metric Spaces, Introduction to Analysis"]
end
check("a category index is titled by its category and the top level") do
  S.category_title_candidates(["1. Mathematics", "2. Algebra", "1. Linear Algebra"]).first ==
    "Linear Algebra — Mathematics"
end
check("an index under Others is titled by its own name") do
  S.category_title_candidates(["Others", "3. Essays"]).first == "Essays"
end

Page = Struct.new(:data, :url)
analysis = ["1. Mathematics", "3. Mathematical Analysis", "1. Introduction to Analysis"]
first = Page.new({ "title" => "Exercises" })
second = Page.new({ "title" => "Exercises" })
question = Page.new({ "title" => "Linear Algebra" })
index = Page.new({})
shared = S.choose_titles([[first, S.post_title_candidates("Exercises", analysis + ["2. Metric Spaces"]), 0],
                          [second, S.post_title_candidates("Exercises", analysis + ["1. Algebraic and Ordered Structures"]), 0],
                          [question, ["Linear Algebra — Mathematics", "Linear Algebra — Questions"], 0],
                          [index, ["Linear Algebra — Mathematics", "Linear Algebra — Algebra"], 1]],
                         ["About"])
check("two posts that share a title both take their sections") do
  first.data["seo_title"] == "Exercises — Metric Spaces" &&
    second.data["seo_title"] == "Exercises — Algebraic and Ordered Structures"
end
check("a post gives way to a category index of the same title") do
  index.data["seo_title"] == "Linear Algebra — Mathematics" &&
    question.data["seo_title"] == "Linear Algebra — Questions"
end
check("no title is left shared") { shared.empty? }

puts "descriptions"
body = <<~HTML
  <section class="doc-section doc-section--run-in" data-doc="paragraph">
  <p><strong class="math-label-anchor doc-heading" role="heading">Bases.</strong> The concepts of generating sets were introduced before. We now seek @@codex-inline-math-0@@ of it.</p>
  <section class="math-environment" data-doc="definition">
  <p><strong class="math-label-anchor">Definition 1.6.1.</strong> Let @@codex-inline-math-1@@ be a vector space. A subset @@codex-inline-math-2@@ of @@codex-inline-math-1@@ is a basis if @@codex-inline-math-3@@ holds.<sup id="fnref:1"><a href="#fn:1">1</a></sup></p>
  </section>
  <section class="math-environment math-environment--proof" data-doc="proof">
  <p><em class="math-proof-marker">Proof.</em> This proof is never quoted in a description.</p>
  </section>
  </section>
HTML
blocks = S.prose_blocks(body)
check("labels, proofs and footnote marks are not prose") do
  blocks.map(&:first) == %w[p p] && blocks.none? { |_, text| text.match?(/Bases\.|Definition|Proof|never|>1</) }
end
description = S.description_from_html(body, ["\\whitestar", "V", "S", "\\operatorname{span}(S)=V"])
check("whole sentences, math as text, none with math that has no text form") do
  description == "The concepts of generating sets were introduced before. A subset S of V is a basis if span(S) = V holds."
end
continued = %(<p>If @@codex-inline-math-0@@ is a member of @@codex-inline-math-1@@, we write</p>\n\\[a\\in A.\\]\n<p>for short. ) +
            %(An empty set is a set with no members at all.</p>)
check("a sentence broken by display math is left out, before and after it") do
  S.description_from_html(continued, ["a", "A"]) == "An empty set is a set with no members at all."
end
items = %(<p>An order on a set satisfies the following conditions:</p><ol><li>@@codex-inline-math-0@@ (irreflexivity);</li>) +
        %(<li>@@codex-inline-math-1@@ (transitivity).</li></ol><p>Such a set is called an ordered set here.</p>)
check("a list item that starts with math is not a sentence") do
  S.description_from_html(items, ["\\neg(x<x)", "x<z"]) == "Such a set is called an ordered set here."
end
check("a period typed inside the math still ends the sentence") do
  S.description_from_html(%(<p>The set of rationals is dense in @@codex-inline-math-0@@ It is also countable, as a set.</p>), ["\\mathbb R."]) ==
    "The set of rationals is dense in ℝ. It is also countable, as a set."
end
long = "<p>Every #{(['word'] * 60).join(' ')}.</p>"
check("a sentence too long is cut at a word") do
  text = S.description_from_html(long, [])
  text.length <= S::DESCRIPTION_LIMIT + 1 && text.end_with?("word…")
end
check("a series takes semicolons when an item holds a comma") do
  S.series(["Vector Spaces", "Linear Maps, Kernels, and Images"]) == "Vector Spaces; and Linear Maps, Kernels, and Images" &&
    S.series(%w[A B C]) == "A, B, and C" && S.series(%w[A B]) == "A and B"
end

Post = Struct.new(:data, :url)
algebra = ["1. Mathematics", "2. Algebra", "1. Linear Algebra"]
posts = [
  Post.new({ "title" => "2. Subspaces", "category_path" => algebra + ["1. Vector Spaces"] }, "/subspaces/"),
  Post.new({ "title" => "1. Vector Spaces", "category_path" => algebra + ["1. Vector Spaces"] }, "/vector-spaces/"),
  Post.new({ "title" => "1. Linear Maps", "category_path" => algebra + ["2. Linear Maps"] }, "/linear-maps/")
]
check("a textbook index lists its posts in contents order") do
  S.category_description(algebra, posts, textbook: true) == "Linear Algebra: Vector Spaces, Subspaces, and Linear Maps."
end
check("any other index lists what is directly under it") do
  S.category_description(algebra.first(2), posts) == "Algebra: Linear Algebra."
end

puts "neighbours"
S.link_neighbours(posts)
check("posts in one section link to each other in title order") do
  posts[1].data["section_next"]["url"] == "/subspaces/" && posts[0].data["section_previous"]["url"] == "/vector-spaces/" &&
    !posts[1].data.key?("section_previous") && !posts[0].data.key?("section_next")
end
check("a post alone in its section has no neighbours") do
  !posts[2].data.key?("section_previous") && !posts[2].data.key?("section_next")
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
