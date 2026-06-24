# frozen_string_literal: true

module ExternalInlineMathPreprocessor
  DATA_KEY = "inline_math_placeholders"
  MARKDOWN_EXTENSIONS = [".md", ".markdown"].freeze

  module_function

  def protect(content)
    return content unless content&.include?("$")

    output = +""
    fence = nil
    math_block = false
    placeholders = []

    content.each_line do |line|
      if math_block
        output << line
        math_block = false if closing_math_block?(line)
        next
      end

      if fence
        output << line
        fence = nil if closing_fence?(line, fence)
        next
      end

      fence = opening_fence(line)
      if fence
        output << line
      elsif opening_math_block?(line)
        output << line
        math_block = true unless closing_math_block?(line, 2)
      else
        output << protect_inline_code_segments(line, placeholders)
      end
    end

    [output, placeholders]
  end

  def protect_inline_code_segments(line, placeholders)
    output = +""
    index = 0

    while index < line.length
      if line[index] == "`"
        close_index = closing_backtick_index(line, index)

        if close_index
          output << line[index...close_index]
          index = close_index
        else
          output << line[index..]
          break
        end
      else
        next_code_index = line.index("`", index) || line.length
        output << protect_dollar_segment(line[index...next_code_index], placeholders)
        index = next_code_index
      end
    end

    output
  end

  def protect_dollar_segment(text, placeholders)
    output = +""
    index = 0

    while index < text.length
      if double_dollar?(text, index)
        close_index = closing_double_dollar_index(text, index + 2)

        if close_index
          output << text[index...(close_index + 2)]
          index = close_index + 2
          next
        end

        output << text[index..]
        break
      elsif opening_dollar?(text, index)
        close_index = closing_dollar_index(text, index + 1)

        if close_index
          output << placeholder_for(text[(index + 1)...close_index], placeholders)
          index = close_index + 1
          next
        end
      end

      output << text[index]
      index += 1
    end

    output
  end

  def placeholder_for(math, placeholders)
    index = placeholders.length
    placeholders << math
    "@@codex-inline-math-#{index}@@"
  end

  def restore(output, placeholders)
    return output if placeholders.nil? || placeholders.empty?

    placeholders.each_with_index do |math, index|
      output = output.gsub(
        "@@codex-inline-math-#{index}@@",
        inline_math_html(math)
      )
    end

    output
  end

  def inline_math_html(math)
    '<span class="math-inline">\(' + escape_html(math) + '\)</span>'
  end

  def escape_html(text)
    text
      .gsub("&", "&amp;")
      .gsub("<", "&lt;")
      .gsub(">", "&gt;")
  end

  def opening_fence(line)
    match = line.match(/\A {0,3}(`{3,}|~{3,})/)
    return unless match

    match[1]
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

  def closing_backtick_index(line, index)
    tick_count = 0
    tick_count += 1 while line[index + tick_count] == "`"

    delimiter = "`" * tick_count
    close_index = line.index(delimiter, index + tick_count)
    close_index && close_index + tick_count
  end

  def opening_dollar?(text, index)
    return false unless text[index] == "$"
    return false if escaped?(text, index)
    return false if text[index - 1] == "$" || text[index + 1] == "$"

    next_char = text[index + 1]
    next_char && !next_char.match?(/\s/)
  end

  def double_dollar?(text, index)
    text[index] == "$" && text[index + 1] == "$" && !escaped?(text, index)
  end

  def closing_dollar?(text, index)
    return false unless text[index] == "$"
    return false if escaped?(text, index)
    return false if text[index - 1] == "$" || text[index + 1] == "$"

    previous_char = text[index - 1]
    next_char = text[index + 1]

    previous_char && !previous_char.match?(/\s/) &&
      !(next_char && next_char.match?(/\d/))
  end

  def closing_dollar_index(text, index)
    while index < text.length
      return index if closing_dollar?(text, index)

      index += 1
    end

    nil
  end

  def closing_double_dollar_index(text, index)
    while index < text.length
      return index if double_dollar?(text, index)

      index += 1
    end

    nil
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

  def markdown_item?(item)
    path =
      if item.respond_to?(:relative_path)
        item.relative_path
      elsif item.respond_to?(:path)
        item.path
      end

    MARKDOWN_EXTENSIONS.include?(File.extname(path.to_s).downcase)
  end

  def enabled?(site)
    options = site.config["inline_math_preprocessor"] || {}
    options["enabled"] != false
  end

  def protect_item(item, site)
    return unless enabled?(site)
    return unless markdown_item?(item)

    protected_content, placeholders = protect(item.content)
    item.content = protected_content
    item.data[DATA_KEY] = placeholders
  end

  def restore_item(item, site)
    return unless enabled?(site)
    return unless markdown_item?(item)

    item.output = restore(item.output, item.data[DATA_KEY])
    item.data.delete(DATA_KEY)
  end
end

if defined?(Jekyll)
  Jekyll::Hooks.register [:pages, :documents], :pre_render do |item|
    site = item.respond_to?(:site) ? item.site : nil
    ExternalInlineMathPreprocessor.protect_item(item, site) if site
  end

  Jekyll::Hooks.register [:pages, :documents], :post_render do |item|
    site = item.respond_to?(:site) ? item.site : nil
    ExternalInlineMathPreprocessor.restore_item(item, site) if site
  end
end
