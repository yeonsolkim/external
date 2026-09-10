# frozen_string_literal: true

module ExternalPostEntryBreaks
  MARKER = '<div class="post-explicit-entry-break" aria-hidden="true"></div>'.freeze
  STRUCTURAL_CONTINUATION_MARKER =
    '<div class="post-structural-continuation" aria-hidden="true"></div>'.freeze
  ENVIRONMENT_END_MARKER = lambda do |kind|
    %(<div class="math-environment-end" data-environment-end="#{kind}" aria-hidden="true"></div>)
  end

  module_function

  def mark(content, inline_math = [])
    return content unless content

    inline_math ||= []
    output = +""
    blank_lines = []
    fence = nil
    math_block = nil

    content.each_line do |line|
      if fence
        output << line
        fence = nil if closing_fence?(line, fence)
        next
      end

      if math_block
        output << line
        math_block << line

        if closing_math_block?(line)
          append_environment_end_marker(output, display_environment_end_kind(math_block))
          math_block = nil
        end

        next
      end

      if blank_line?(line)
        blank_lines << line
        next
      end

      append_blank_lines(output, blank_lines)
      blank_lines.clear

      fence = opening_fence(line)

      if !fence && opening_math_block?(line)
        output << line

        if closing_math_block?(line, 2)
          append_environment_end_marker(output, display_environment_end_kind(line))
        else
          math_block = line.dup
        end

        next
      end

      output << annotate_inline_environment_end(line, inline_math)
    end

    output << blank_lines.join
    output
  end

  def environment_end_kind(source)
    return 'subproof' if source.include?('\\blacksquare')
    return 'proof' if source.match?(/\\square\b/)

    nil
  end

  def display_environment_end_kind(source)
    return nil unless source.include?('\\tag*')

    environment_end_kind(source)
  end

  def append_environment_end_marker(output, kind)
    return unless kind

    output << "\n#{ENVIRONMENT_END_MARKER.call(kind)}\n"
  end

  def annotate_inline_environment_end(line, inline_math = [])
    line.gsub(/<span\b[^>]*>.*?<\/span>/i) do |span|
      next span unless span.match?(/\bclass=(['"])[^'"]*\bqed\b[^'"]*\1/i)
      next span if span.match?(/\bdata-environment-end=/i)

      source = span.gsub(/@@codex-inline-math-(\d+)@@/) do |placeholder|
        inline_math.fetch(Regexp.last_match(1).to_i, placeholder)
      end
      kind = environment_end_kind(source)
      next span unless kind

      span.sub(/\A<span\b/i, %(<span data-environment-end="#{kind}"))
    end
  end

  def append_blank_lines(output, blank_lines)
    if blank_lines.length >= 3
      output << "\n#{MARKER}\n\n"
    elsif blank_lines.length == 2
      output << "\n#{STRUCTURAL_CONTINUATION_MARKER}\n\n"
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

    item.content = mark(item.content, item.data['inline_math_placeholders'])
  end
end

if defined?(Jekyll)
  Jekyll::Hooks.register :documents, :pre_render do |item|
    ExternalPostEntryBreaks.process(item)
  end
end
