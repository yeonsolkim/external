#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for what a reference in prose links to (_plugins/reference_label_targets.rb).
#
#   ruby _tests/test_reference_label_targets.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

require "jekyll"
require_relative "../_plugins/category_labels"
require_relative "../_plugins/reference_label_targets"

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

Post = Struct.new(:content, :url, :data)
Posts = Struct.new(:docs)
Site = Struct.new(:posts, :baseurl)

def targets(*contents)
  posts = contents.each_with_index.map do |content, index|
    Post.new(content, "/topology/post-#{index + 1}/",
             { "category_path" => ["1. Mathematics", "5. Topology", "1. Topological Spaces"] })
  end
  ExternalReferenceLabelTargets.build(Site.new(Posts.new(posts), ""))["topology"]
end

puts "statements"
check("a label is a target with its kind and by its number alone") do
  targets("**Theorem 1.1.10.** T.") == {
    "Theorem 1.1.10" => "/topology/post-1/#theorem-1-1-10", "1.1.10" => "/topology/post-1/#theorem-1-1-10"
  }
end
check("a number two statements share links nowhere") do
  found = targets("**Definition 1.1.1.** D.", "**Exercise 1.1.1.** E.")
  found["1.1.1"].nil? && found["Definition 1.1.1"] == "/topology/post-1/#definition-1-1-1"
end

puts "figures"
check("a figure is a target by its kind only: a bare number is always a statement's") do
  targets("**Definition 1.1.1.** D.\n\n**Figure 1.1.1.** A caption") == {
    "1.1.1" => "/topology/post-1/#definition-1-1-1",
    "Definition 1.1.1" => "/topology/post-1/#definition-1-1-1",
    "Figure 1.1.1" => "/topology/post-1/#figure-1-1-1"
  }
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
