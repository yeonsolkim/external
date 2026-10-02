#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for the English annotation pass, which mutes usage labels and examples.
#
#   ruby _tests/test_english_annotations.rb
#
# Like test_document_structure.rb, it lives outside _plugins/ so a site build never runs it.

require_relative "../_plugins/english_annotations"

A = ExternalEnglishAnnotations
IAL = "{: .english-annotation}"
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

Post = Struct.new(:collection, :data, :content)
Collection = Struct.new(:label)

def post(category_path, content = "")
  Post.new(Collection.new("posts"), { "category_path" => category_path }, content)
end

puts "scope"
check("numbered English top-level category is in scope") { A.english_post?(post(["3. English", "2. Dictionary"])) }
check("unnumbered English top-level category is in scope") { A.english_post?(post(["English", "I. Grammar", "4. Subordinates"])) }
check("English below the top level is out of scope") { !A.english_post?(post(["1. Mathematics", "English"])) }
check("Dictionary outside English is out of scope") { !A.english_post?(post(["1. Mathematics", "Dictionary"])) }
check("non-post documents are out of scope") do
  !A.english_post?(Post.new(Collection.new("pages"), { "category_path" => ["English"] }, ""))
end

puts "examples"
check("headword line: example after the definition") do
  A.annotate_line("**charm**: the quality of giving delight: *his charm has captivated the media.*\n") ==
    "**charm**: the quality of giving delight: *his charm has captivated the media.*#{IAL}\n"
end
check("numbered sense line without a headword") do
  A.annotate_line("1. ability: *he can lift 500N.*\n") == "1. ability: *he can lift 500N.*#{IAL}\n"
end
check("prose line with trailing whitespace") do
  A.annotate_line("is satisfied: *if he loves her, he will change\\| if he loved her, he changed.* \n") ==
    "is satisfied: *if he loves her, he will change\\| if he loved her, he changed.*#{IAL} \n"
end
check("bold paragraph label with a single colon") do
  A.annotate_line("**2.3. Degree.** It may vary: *if you wanted, we could leave now.*\n") ==
    "**2.3. Degree.** It may vary: *if you wanted, we could leave now.*#{IAL}\n"
end
check("bold inside the example stays part of it") do
  A.annotate_line("**hostile**: unfriendly: *he was **hostile to** the reforms.*\n") ==
    "**hostile**: unfriendly: *he was **hostile to** the reforms.*#{IAL}\n"
end
check("punctuation after the closing asterisk") do
  A.annotate_line("2. permission: *you can go home now*.\n") == "2. permission: *you can go home now*#{IAL}.\n"
end
check("<em> example gets the class attribute") do
  A.annotate_line("**w**: def: <em>an example.</em>\n") == "**w**: def: <em class=\"english-annotation\">an example.</em>\n"
end

puts "not examples"
check("italic that does not follow a colon") do
  line = "1. Huddleston, R. (2021). *A student’s introduction to English grammar* (2nd ed.).\n"
  A.annotate_line(line) == line
end
check("italic not running to the end of the line") do
  line = "manner: *in English* is common here.\n"
  A.annotate_line(line) == line
end
check("two italic spans after a colon") do
  line = "term: *a* means b and *c*\n"
  A.annotate_line(line) == line
end
check("kramdown definition-list line") do
  line = ": *definition*\n"
  A.annotate_line(line) == line
end
check("fenced code is left alone") do
  text = "```\nx: *y*\n```\n"
  A.annotate(text) == text
end

puts "usage labels"
check("leading label and trailing example on one headword line") do
  A.annotate_line("**w**: *[informal]* a meaning: *an example.*\n") ==
    "**w**: *[informal]*#{IAL} a meaning: *an example.*#{IAL}\n"
end
check("label with no example") do
  A.annotate_line("**w**: *Computing* a meaning.\n") == "**w**: *Computing*#{IAL} a meaning.\n"
end
check("lexical category is not a label") do
  line = "**w**: *noun* a meaning.\n"
  A.annotate_line(line) == line
end

puts "process"
check("out-of-scope posts are untouched") do
  document = post(["1. Mathematics", "2. Calculus"], "x: *y*\n")
  A.process(document)
  document.content == "x: *y*\n"
end
check("in-scope posts are annotated") do
  document = post(["English", "I. Grammar"], "x: *y*\n")
  A.process(document)
  document.content == "x: *y*#{IAL}\n"
end

puts(($failures.zero? ? "\nall checks passed" : "\n#{$failures} failed"))
exit($failures.zero? ? 0 : 1)
