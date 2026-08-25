# frozen_string_literal: true

module ExternalPostEntryBreaks
  MARKER = '<div class="post-explicit-entry-break" aria-hidden="true"></div>'.freeze

  module_function

  def mark(content)
    return content unless content&.include?("\n\n\n")

    output = +""
    blank_lines = []
    fence = nil
    math_block = false

    content.each_line do |line|
      if fence
        output << line
        fence = nil if closing_fence?(line, fence)
        next
      end

      if math_block
        output << line
        math_block = false if closing_math_block?(line)
        next
      end

      if blank_line?(line)
        blank_lines << line
        next
      end

      append_blank_lines(output, blank_lines)
      blank_lines.clear

      fence = opening_fence(line)
      math_block = true if !fence && opening_math_block?(line) && !closing_math_block?(line, 2)
      output << line
    end

    output << blank_lines.join
    output
  end

  def append_blank_lines(output, blank_lines)
    if blank_lines.length >= 2
      output << "\n#{MARKER}\n\n"
    else
      output << blank_lines.join
    end
  end

  def blank_line?(line)
    line.match?(/\A[ \t]*\r?\n\z/)
  end

  def opening_fence(line)
    line[/\A {0,3}(`{3,}|~{3,})/, 1]
  end

  def closing_fence?(line, fence)
    marker = Regexp.escape(fence[0])
    line.match?(/\A {0,3}#{marker}{#{fence.length},}\s*\z/)
  end

  def opening_math_block?(line)
    line.match?(/\A {0,3}\$\$/)
  end

  def closing_math_block?(line, start_index = 0)
    index = line.index("$$", start_index)

    while index
      return true if !escaped?(line, index) && line[(index + 2)..].to_s.match?(/\A\s*\z/)

      index = line.index("$$", index + 2)
    end

    false
  end

  def escaped?(text, index)
    backslashes = 0
    index -= 1

    while index >= 0 && text[index] == "\\"
      backslashes += 1
      index -= 1
    end

    backslashes.odd?
  end

  def post?(item)
    item.respond_to?(:collection) && item.collection&.label == "posts"
  end

  def process(item)
    return unless post?(item)

    item.content = mark(item.content)
  end
end

if defined?(Jekyll)
  Jekyll::Hooks.register :documents, :pre_render do |item|
    ExternalPostEntryBreaks.process(item)
  end
end
