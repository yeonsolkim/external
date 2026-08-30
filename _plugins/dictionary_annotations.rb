# frozen_string_literal: true

module ExternalDictionaryAnnotations
  ANNOTATION_CLASS = "dictionary-annotation"
  HEADWORD_PATTERN = /\A(?<headword>(?:<b>.*?<\/b>|\*\*.*?\*\*)(?:<sup>.*?<\/sup>)?)(?<tail>.*)\z/m
  LEADING_USAGE_LABEL_PATTERN = /\A(?<separator>:[ \t\u00A0]*)(?<label>\*(?:\[[^\]\r\n]+\]|Computing|Linguistics)\*)(?!\{:)/
  TRAILING_EXAMPLE_PATTERN = /\A(?<before>.*?:.*?)(?<separator>:[ \t\u00A0]*)(?<example>\*.*\*|<(?:em|i)(?:\s[^>]*)?>.*?<\/(?:em|i)>)(?<punctuation>[.!?]?)(?<trailing>[ \t\u00A0]*\r?\n?)\z/m
  ORDER_PREFIX_PATTERN = /\A(?:(?:[IVXLCDM]+)|(?:\d+))[.)]\s*/i

  module_function

  def annotate(content)
    return content unless content

    output = +""
    fence = nil

    content.each_line do |line|
      if fence
        output << line
        fence = nil if closing_fence?(line, fence)
        next
      end

      fence = opening_fence(line)
      output << (fence ? line : annotate_line(line))
    end

    output
  end

  def annotate_line(line)
    match = line.match(HEADWORD_PATTERN)
    return line unless match

    tail = mark_leading_usage_label(match[:tail])
    tail = mark_trailing_example(tail)

    match[:headword] + tail
  end

  def mark_leading_usage_label(tail)
    tail.sub(LEADING_USAGE_LABEL_PATTERN) do
      "#{Regexp.last_match[:separator]}#{Regexp.last_match[:label]}{: .#{ANNOTATION_CLASS}}"
    end
  end

  def mark_trailing_example(tail)
    tail.sub(TRAILING_EXAMPLE_PATTERN) do
      example = annotate_example(Regexp.last_match[:example])

      Regexp.last_match[:before] +
        Regexp.last_match[:separator] +
        example +
        Regexp.last_match[:punctuation] +
        Regexp.last_match[:trailing]
    end
  end

  def annotate_example(example)
    return "#{example}{: .#{ANNOTATION_CLASS}}" if example.start_with?("*")
    return example if example.match?(/\bclass=(['"])[^'"]*\b#{ANNOTATION_CLASS}\b[^'"]*\1/)

    example.sub(/\A<(em|i)(\s[^>]*)?>/) do
      tag = Regexp.last_match(1)
      attributes = Regexp.last_match(2).to_s

      if attributes.match?(/\bclass\s*=/)
        attributes = attributes.sub(/\bclass=(['"])(.*?)\1/) do
          %(class=#{Regexp.last_match(1)}#{Regexp.last_match(2)} #{ANNOTATION_CLASS}#{Regexp.last_match(1)})
        end
      else
        attributes += %( class="#{ANNOTATION_CLASS}")
      end

      "<#{tag}#{attributes}>"
    end
  end

  def dictionary_post?(item)
    return false unless item.respond_to?(:collection) && item.collection&.label == "posts"

    category_path = item.data["category_path"] || item.data["categories"] || []
    category_path = [category_path] unless category_path.is_a?(Array)

    category_path.any? do |category|
      category.to_s.strip.sub(ORDER_PREFIX_PATTERN, "").casecmp?("Dictionary")
    end
  end

  def opening_fence(line)
    line[/\A {0,3}(`{3,}|~{3,})/, 1]
  end

  def closing_fence?(line, fence)
    marker = Regexp.escape(fence[0])
    line.match?(/\A {0,3}#{marker}{#{fence.length},}\s*\z/)
  end

  def process(item)
    return unless dictionary_post?(item)

    item.content = annotate(item.content)
  end
end

if defined?(Jekyll)
  Jekyll::Hooks.register :documents, :pre_render do |item|
    ExternalDictionaryAnnotations.process(item)
  end
end
