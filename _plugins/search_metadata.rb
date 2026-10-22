# frozen_string_literal: true

require "cgi"
require "strscan"
require_relative "category_labels"
require_relative "inline_math_preprocessor"
require_relative "tex_text"

# Search metadata: what jekyll-seo-tag writes into each page's <head>. Nothing here changes
# the <h1> or the .post-body, which is all the narration reads (_narrator/skeleton.py).
#
# Titles. A post's <title> is its title without the number, then its subject: the textbook
# it belongs to (the folder above its section), or, for a post filed directly under a
# second-level category, that category. "Others" names no subject, so the level above it
# stands in: "Axioms and Examples — Group Theory". When two pages would still share a title,
# the section takes the subject's place ("Exercises — Metric Spaces"), and failing that joins
# it. A generated category index is titled by its category and the top-level category above
# it: "Linear Algebra — Mathematics". The result is stored as `seo_title`, which the seo tag
# is taught below to prefer to `title`, so `title` itself (the <h1>) is untouched. No page's
# <title> carries the site name, which jekyll-seo-tag would append; og:site_name gives it.
#
# Descriptions. A post without a `description:` of its own gets its first sentences of prose,
# its inline math written out as text by tex_text.rb; a sentence whose math has no faithful
# text form, or that starts with math (an item of a definition's list, say), is left out.
# (jekyll-seo-tag would otherwise use the excerpt, raw TeX and all.) A category index lists
# what it contains. The text goes to `description`, which the feed reads, and to
# `seo_description`, which the seo tag is taught to take as it is: it would otherwise run it
# through Markdown, and `|A| = n` would come out as a table.
module ExternalSearchMetadata
  SEPARATOR = " — "
  GENERIC_LABEL = /\Aothers?\z/i.freeze

  # A description gathers sentences until it is this long, never adding one that would take
  # it past the limit; a first sentence longer than that is kept whole up to the hard limit
  # and cut at a word beyond it. Search results show about 155 characters.
  DESCRIPTION_TARGET = 110
  DESCRIPTION_LIMIT = 160
  DESCRIPTION_HARD_LIMIT = 220
  CATEGORY_DESCRIPTION_LIMIT = 250

  UNWRITABLE = "@@unwritable-math@@"
  # Around math written out as text, until the sentences are chosen: a sentence must begin
  # with a capital letter of prose, not with a formula.
  MATH_OPEN = [0xE000].pack("U").freeze
  MATH_CLOSE = [0xE001].pack("U").freeze
  # What may follow a sentence's full stop: a closing quote or bracket, or the end of the
  # math the stop was typed in (`$\mathbb R.$`).
  SENTENCE_END = /[.!?][#{MATH_CLOSE}"”’)\]]*/.freeze
  MIN_SENTENCE_WORDS = 5
  # "Let X and Y be sets." sets a scene and "Then …" finishes one; neither says what the
  # post is about.
  SETUP_SENTENCE = /\A(?:Let|Fix|Then|Thus|Hence|Therefore)\b/.freeze
  TAG = /<(\/?)([a-zA-Z][\w:-]*)((?:"[^"]*"|'[^']*'|[^>"'])*)>/.freeze
  VOID_TAGS = %w[area base br col embed hr img input link meta param source track wbr].freeze
  PROSE_TAGS = %w[p li].freeze
  # Figures, tables, code and footnote marks are not prose; neither are the labels
  # ("Definition 1.1.1.", "Proof."), the proofs, the footnotes, the source note or the
  # bibliography.
  SKIPPED_TAGS = %w[table figure pre svg sup script style math].freeze
  SKIPPED_CLASSES = %w[
    footnotes post-source-note reference math-label-anchor math-proof-marker qed
  ].freeze
  ABBREVIATIONS = %w[e.g i.e etc cf vs viz ed eds vol no pp ch sec fig resp approx].freeze

  module_function

  # -- titles ---------------------------------------------------------------------------
  def labels(category_path)
    Array(category_path).map { |part| Jekyll::CategoryLabels.strip_order_prefix(part) }
                        .reject(&:empty?)
  end

  def bare_title(title)
    Jekyll::CategoryLabels.numbered_label_parts(title)[1]
  end

  # The nearest of these labels, going up, that names something.
  def named(labels)
    labels.reverse.find { |label| !label.match?(GENERIC_LABEL) }
  end

  # What a post is about: its textbook, the folder above its section, or for a post filed
  # directly under a second-level category, that category.
  def post_subject(category_path)
    path = labels(category_path)
    named(path.length >= 3 ? path[0...-1] : path)
  end

  # Titles for a post, the plainest first.
  def post_title_candidates(title, category_path)
    name = bare_title(title)
    path = labels(category_path)
    subject = post_subject(category_path)
    subject = nil if subject == name
    section = path.length >= 3 ? path.last : nil
    section = nil if section == name

    candidates = [subject ? "#{name}#{SEPARATOR}#{subject}" : name]
    candidates << "#{name}#{SEPARATOR}#{section}" if section
    candidates << "#{name}#{SEPARATOR}#{section}, #{subject}" if section && subject && section != subject
    candidates.uniq
  end

  # Titles for a generated category index, the plainest first.
  def category_title_candidates(category_path)
    path = labels(category_path)
    name = path.last.to_s
    top = named(path.first(1)) if path.length > 1
    parent = named(path[0...-1])

    candidates = [top && top != name ? "#{name}#{SEPARATOR}#{top}" : name]
    candidates << "#{name}#{SEPARATOR}#{parent}" if parent && parent != top && parent != name
    candidates.uniq
  end

  # Gives each entry its plainest title that no other page has. `entries` are
  # [item, candidates, rank]; `taken` are the titles of pages this plugin does not title.
  # Of the pages that share a title, those of the lowest rank move on to their next
  # candidate, so a category index keeps "Linear Algebra — Mathematics" and a post of the
  # same name moves aside; pages of one rank move together, so neither "Exercises" post is
  # the plain one. Returns the titles still shared.
  def choose_titles(entries, taken)
    choice = Array.new(entries.length, 0)
    title = ->(i) { entries[i][1][choice[i]] }

    loop do
      groups = Hash.new { |hash, key| hash[key] = [] }
      entries.each_index { |i| groups[title.(i).downcase] << i }
      taken.each { |fixed| groups[fixed.downcase] << nil }

      moved = false
      groups.each_value do |members|
        next if members.length < 2

        movable = members.compact.select { |i| choice[i] + 1 < entries[i][1].length }
        next if movable.empty?

        lowest = movable.map { |i| entries[i][2] }.min
        movable.select { |i| entries[i][2] == lowest }.each { |i| choice[i] += 1 }
        moved = true
      end

      next if moved

      entries.each_index { |i| entries[i][0].data["seo_title"] = title.(i) }
      return groups.select { |_, members| members.length > 1 }.keys
    end
  end

  # -- descriptions -----------------------------------------------------------------------
  # Each paragraph and list item outside the skipped parts, in order, as [tag name, text]:
  # its HTML text (entities, inline-math placeholders) without the tags.
  def prose_blocks(html)
    blocks = []
    stack = []
    buffer = nil
    buffer_tag = nil
    scanner = StringScanner.new(html.to_s)

    until scanner.eos?
      if scanner.scan(/<!--.*?-->/m)
        next
      elsif scanner.scan(TAG)
        name = scanner[2].downcase
        attributes = scanner[3]

        if scanner[1] == "/"
          index = stack.rindex { |entry| entry[:name] == name }
          next unless index

          closed = stack.slice!(index..)
          next unless closed.any? { |entry| entry[:prose] }

          blocks << [buffer_tag, buffer] if buffer && !buffer.strip.empty?
          # A list item that holds a list may go on after it.
          open_prose = stack.reverse.find { |entry| entry[:prose] }
          buffer = open_prose ? +"" : nil
          buffer_tag = open_prose && open_prose[:name]
        elsif VOID_TAGS.include?(name) || attributes.end_with?("/")
          buffer << " " if buffer
        else
          skipped = stack.any? { |entry| entry[:skip] } || skipped?(name, attributes)
          prose = !skipped && PROSE_TAGS.include?(name)
          if prose
            blocks << [buffer_tag, buffer] if buffer && !buffer.strip.empty?
            buffer = +""
            buffer_tag = name
          end
          stack << { name: name, skip: skipped, prose: prose }
        end
      else
        text = scanner.scan(/[^<]+/) || scanner.getch
        buffer << text if buffer && stack.none? { |entry| entry[:skip] }
      end
    end

    blocks
  end

  def skipped?(name, attributes)
    return true if SKIPPED_TAGS.include?(name)
    return true if attributes.match?(/\bdata-doc="proof"/) || attributes.match?(/\baria-hidden="true"/)

    classes = attributes[/\bclass="([^"]*)"/, 1].to_s.split
    classes.intersect?(SKIPPED_CLASSES)
  end

  # A block as plain text, math written out; math with no text form becomes UNWRITABLE.
  def plain_text(block, placeholders)
    text = block.gsub(/\\\[.*?\\\]|\$\$.*?\$\$/m, " #{UNWRITABLE} ")
    text = text.gsub(ExternalInlineMathPreprocessor::PLACEHOLDER_PATTERN) do
      math_text(placeholders[Regexp.last_match(1).to_i].to_s)
    end
    text = text.gsub(/\\\((.*?)\\\)/m) { math_text(CGI.unescapeHTML(Regexp.last_match(1))) }
    CGI.unescapeHTML(text).gsub(/\s+/, " ").strip
  end

  def math_text(tex)
    text = ExternalTexText.convert(tex)
    text ? "#{MATH_OPEN}#{text}#{MATH_CLOSE}" : UNWRITABLE
  end

  def split_sentences(text)
    sentences = []
    start = 0

    text.to_enum(:scan, /#{SENTENCE_END}(?=\s+[^\sa-z])/).each do
      finish = Regexp.last_match.end(0)
      word = text[start...finish][/(\S+?)#{SENTENCE_END}\z/, 1].to_s.delete(MATH_OPEN + MATH_CLOSE)
      next if ABBREVIATIONS.include?(word.downcase)

      sentences << text[start...finish].strip
      start = finish
    end

    rest = text[start..].to_s.strip
    sentences << rest unless rest.empty?
    sentences
  end

  # Whole sentences of prose from the start of a post, at most about DESCRIPTION_LIMIT
  # characters; "" when the post has none that can be written as text.
  def description_from_html(html, placeholders)
    sentences = []

    prose_blocks(html).each do |tag, block|
      found = split_sentences(plain_text(block, placeholders))
      # A paragraph that opens in lower case finishes a sentence a display equation broke.
      found.shift if tag == "p" && block.lstrip.match?(/\A[a-z]/)
      found.each do |sentence|
        next unless sentence?(sentence)

        sentences << sentence.delete(MATH_OPEN + MATH_CLOSE)
      end
      break if sentences.join(" ").length >= DESCRIPTION_TARGET
    end

    compose(sentences)
  end

  # A whole sentence of prose that says something: it starts with a capital letter, not with
  # a formula or in the middle of a list, ends with a full stop, has no math without a text
  # form, and is neither a setup ("Let A ⊆ ℝ.") nor a scrap.
  def sentence?(sentence)
    sentence.match?(/\A["“(]?[[:upper:]]/) &&
      sentence.match?(/#{SENTENCE_END}\z/) &&
      !sentence.include?(UNWRITABLE) &&
      !sentence.match?(SETUP_SENTENCE) &&
      sentence.split.length >= MIN_SENTENCE_WORDS
  end

  def compose(sentences)
    description = +""

    sentences.each do |sentence|
      candidate = description.empty? ? sentence : "#{description} #{sentence}"
      if candidate.length <= DESCRIPTION_LIMIT || description.empty?
        description = candidate
        break if description.length >= DESCRIPTION_TARGET
      else
        break
      end
    end

    description.length > DESCRIPTION_HARD_LIMIT ? truncate(description, DESCRIPTION_LIMIT) : description
  end

  def truncate(text, limit)
    cut = text[0, limit]
    cut = cut[0, cut.rindex(" ")] if text.length > limit && cut.include?(" ")
    "#{cut.sub(/[\s,;:—–-]+\z/, '')}…"
  end

  def describe_post(document)
    return unless document.respond_to?(:collection) && document.collection&.label == "posts"

    # A description of the post's own is plain text too, taken as written.
    given = document.data["description"].to_s.strip
    return document.data["seo_description"] = given unless given.empty?

    placeholders = document.data[ExternalInlineMathPreprocessor::DATA_KEY] || []
    description = description_from_html(document.content, placeholders)
    description = fallback_description(document) if description.empty?
    document.data["description"] = description
    document.data["seo_description"] = description
  end

  # For a post with no sentence to quote: what it is and where it belongs.
  def fallback_description(document)
    name = bare_title(document.data["title"])
    subject = post_subject(document.data["category_path"])
    author = document.site.config["author"].to_s.strip
    notes = author.empty? ? "the notes" : "#{author}'s notes"
    subject && subject != name ? "#{name}, from #{notes} on #{subject}." : "#{name}, from #{notes}."
  end

  # "A", "A and B", "A, B, and C"; semicolons between items that hold commas.
  def series(items)
    return items.first.to_s if items.length < 2

    separator = items.any? { |item| item.include?(",") } ? "; " : ", "
    return "#{items[0]} and #{items[1]}" if items.length == 2 && separator == ", "

    "#{items[0...-1].join(separator)}#{separator}and #{items[-1]}"
  end

  def post_path(post)
    Array(post.data["category_path"]).map { |part| part.to_s.strip }.reject(&:empty?)
  end

  # Posts in the order a contents list shows them: the ones filed directly under `prefix`
  # by title, then each folder below it in name order.
  def contents_order(posts, prefix)
    direct, nested = posts.partition { |post| post_path(post).length == prefix.length }
    folders = nested.group_by { |post| post_path(post)[prefix.length] }.sort_by(&:first)

    direct.sort_by { |post| post.data["title"].to_s } +
      folders.flat_map { |folder, members| contents_order(members, prefix + [folder]) }
  end

  # A textbook's index lists its posts (or, when they are too many, its sections); any other
  # index lists the categories and posts directly under it.
  def category_description(category_path, posts, textbook: false)
    path = labels(category_path)
    name = path.last.to_s
    lead = if name.match?(GENERIC_LABEL)
             parent = named(path[0...-1])
             parent ? "Other #{parent} notes" : "Notes"
           else
             name
           end

    inside = posts.select { |post| post_path(post).first(category_path.length) == category_path }
    ordered = contents_order(inside, category_path)
    titles = ordered.map { |post| bare_title(post.data["title"]) }
    direct = ordered.select { |post| post_path(post).length == category_path.length }
    children = direct.map { |post| bare_title(post.data["title"]) } +
               ordered.map { |post| post_path(post)[category_path.length] }.compact.uniq
                      .map { |folder| Jekyll::CategoryLabels.strip_order_prefix(folder) }

    (textbook ? [titles, children] : [children]).each do |items|
      text = "#{lead}: #{series(items)}."
      return text if text.length <= CATEGORY_DESCRIPTION_LIMIT
    end

    truncate("#{lead}: #{children.join(', ')}", CATEGORY_DESCRIPTION_LIMIT)
  end

  # -- the site ---------------------------------------------------------------------------
  def generate(site)
    posts = site.posts.docs
    categories = site.pages.select { |page| page.data["generated_subcategory"] }
    others = site.pages.reject { |page| page.data["generated_subcategory"] }
                       .select { |page| page.output_ext == ".html" && !page.data["title"].to_s.empty? }

    categories.each do |page|
      next unless page.data["description"].to_s.strip.empty?

      description = category_description(page.data["category_path"], posts,
                                         textbook: page.data["textbook_index"])
      page.data["description"] = description
      page.data["seo_description"] = description
    end

    entries = posts.map { |post| [post, post_title_candidates(post.data["title"], post.data["category_path"]), 0] } +
              categories.map { |page| [page, category_title_candidates(page.data["category_path"]), 1] }
    shared = choose_titles(entries, others.map { |page| page.data["title"].to_s })
    shared.each do |title|
      Jekyll.logger.warn "Search metadata:", "more than one page is titled #{title.inspect}"
    end
  end

  # jekyll-seo-tag takes a page's title from `title` and its description from `description`
  # (or the excerpt), each run through Markdown; this makes it take `seo_title` and
  # `seo_description` first, as plain text. Its <title> is that title alone, like og:title
  # and the JSON-LD headline, without the site name it would append.
  module SeoTagInput
    def title
      page_title || super
    end

    def page_title
      @page_title ||= plain_text(page["seo_title"]) || super
    end

    def description
      @description ||= plain_text(page["seo_description"]) || super
    end

    private

    def plain_text(text)
      text = text.to_s.gsub(/\s+/, " ").strip
      text.empty? ? nil : filters.escape_once(text)
    end
  end

  def teach_seo_tag
    return unless defined?(Jekyll::SeoTag::Drop)
    return if Jekyll::SeoTag::Drop.ancestors.include?(SeoTagInput)

    Jekyll::SeoTag::Drop.prepend(SeoTagInput)
  end
end

if defined?(Jekyll::Generator)
  module Jekyll
    class SearchMetadataGenerator < Generator
      safe true
      # After SubcategoryPagesGenerator (:high) has added the category indexes.
      priority :low

      def generate(site)
        ExternalSearchMetadata.generate(site)
      end
    end
  end

  Jekyll::Hooks.register :site, :after_init do |_site|
    ExternalSearchMetadata.teach_seo_tag
  end

  # After document_structure.rb (:normal) has marked the labels, proofs and source note.
  Jekyll::Hooks.register :documents, :post_convert, priority: :low do |document|
    ExternalSearchMetadata.describe_post(document)
  end
end
