#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for the posts' Markdown sources (_plugins/markdown_sources.rb), down to a small site
# built for real: the risk there is Jekyll treating a .md file as a page and writing HTML.
#
#   ruby _tests/test_markdown_sources.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

require "jekyll"
require "tmpdir"
require_relative "../_plugins/markdown_sources"

S = ExternalMarkdownSources
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

BODY = "\n**Definition 1.** A *set* $\\{x\\}$, {% not liquid %} and {{ this }}.  \n\n$$ x $$\n"
POST = <<~MARKDOWN + BODY
  ---
  layout: post
  category_path:
    - 1. Mathematics
    - 2. Linear Algebra
  title: 3. Lattices
  permalink: /linear-algebra/lattices/
  date: 2026-11-04 00:00:00 +0900
  created_at: 2026-11-04 15:06:53 +0900
  narration: false
  published: true
  source_note: "Draws on Aluffi, *Algebra: Chapter 0* (2009)."
  ---
MARKDOWN

puts "URLs"
check("the page's URL with .md") { S.url_for("/linear-algebra/lattices/") == "/linear-algebra/lattices.md" }

puts "the document"
document = S.document(POST, "https://example.com/linear-algebra/lattices/", "A. Author")
head, rest = document.split("\n---\n", 2)
check("opens as front matter") { document.start_with?("---\ncanonical_url: ") }
check("says where it comes from") do
  YAML.safe_load(head, permitted_classes: [Time]).values_at("canonical_url", "author") ==
    ["https://example.com/linear-algebra/lattices/", "A. Author"]
end
check("keeps the kept entries as written") do
  head.include?("title: 3. Lattices\n") && head.include?("date: 2026-11-04 00:00:00 +0900\n") &&
    head.include?(%(source_note: "Draws on Aluffi, *Algebra: Chapter 0* (2009)."))
end
check("leaves out what steers the build") do
  %w[layout category_path Mathematics permalink created_at narration published].none? { |word| head.include?(word) }
end
check("leaves out a key nobody has kept") do
  S.kept_entries("---\ntitle: T\nprivate_note: not for readers\n---\n") == "title: T\n"
end
check("takes the lines under a key with it") do
  S.kept_entries("---\ndescription: >\n  two\n  lines\nlayout: post\n---\n") == "description: >\n  two\n  lines\n"
end
check("leaves out no author it was not given") do
  !S.document(POST, "https://example.com/", nil).include?("author")
end
check("the text is the file's, byte for byte") { rest == BODY }

puts "a site"
Dir.mktmpdir do |dir|
  FileUtils.mkdir_p(File.join(dir, "_posts"))
  File.write(File.join(dir, "_posts", "2026-11-04-Lattices.md"), POST.sub("{% not liquid %}", "").sub("{{ this }}", ""))
  File.write(File.join(dir, "_posts", "2026-11-04-Draft.md"), "---\ntitle: Draft\npermalink: /draft/\npublished: false\n---\n\nText\n")
  destination = File.join(dir, "_site")
  site = Jekyll::Site.new(Jekyll.configuration(
                            "source" => dir, "destination" => destination, "quiet" => true,
                            "url" => "https://example.com", "author" => "A. Author"
                          ))
  site.process
  source = File.join(destination, "linear-algebra", "lattices.md")

  check("the page is still there") { File.exist?(File.join(destination, "linear-algebra", "lattices", "index.html")) }
  check("the source is written as Markdown, not HTML") do
    File.read(source).end_with?("$$ x $$\n") && !File.read(source).include?("<p>")
  end
  check("the source names the page") { File.read(source).include?("canonical_url: https://example.com/linear-algebra/lattices/\n") }
  check("the page is told its source") { site.posts.docs.first.data["markdown_source"] == "/linear-algebra/lattices.md" }
  check("an unpublished post has none") { !File.exist?(File.join(destination, "draft.md")) }
end

puts
puts($failures.zero? ? "all passed" : "#{$failures} failed")
exit($failures.zero? ? 0 : 1)
