# frozen_string_literal: true

# Document structure, built at build time — see _docs/STRUCTURE.md for the contract.
#
# A post's converted HTML is a flat run of <p>, <figure>, <ol>, display math and the
# blank-line markers from post_entry_breaks.rb. This pass gives it the shape of a LaTeX
# document: sectioning commands nest, theorem-like environments are numbered units inside
# a section, and a proof is a sibling of the statement it proves, pointing back at it.
#
# Until now the same grouping happened in assets/js/main.js, after the page had loaded, so
# nothing but the browser ever saw it — not the narration pipeline, not a reader without
# JavaScript, not a screen reader before MathJax finished. main.js keeps every
# presentational pass and skips the grouping when this one has run (`data-semantic-units`).
#
# Numbers are READ, never generated: the id and the narration take the number you typed,
# so a cross-reference in prose can never drift from the label it points at. A number that
# does not continue its neighbours is reported as a build warning.
module ExternalDocumentStructure
  DOMAINS = %w[mathematics physics].freeze

  ENTRY_KINDS = %w[
    Definition Theorem Lemma Corollary Proposition Remark Example
    Principle Notation Axiom Exercise Rule Claim Convention Observation Fact
  ].freeze
  ITALIC_KINDS = %w[Theorem Lemma Proposition Corollary].freeze
  # Statements share one counter (\newtheorem{...}[shared]); exercises keep their own, which
  # is what the posts actually do — Definition 1.1.9 is followed by Exercise 1.1.2.
  OWN_COUNTER = %w[Exercise].freeze

  ENTRY_RE = /\A(#{ENTRY_KINDS.join("|")})(?:\s+(\d+(?:\.\d+)*))?\.?\z/.freeze
  PROOF_RE = /\A(Proof|Subproof|Solution)(?:\s+\d+)?\.?\z/i.freeze
  NUMBERED_RE = /\A(\d+(?:\.\d+)*)\.(?:\s+(\S.*?))?\z/.freeze
  ORDER_PREFIX = /\A\d+(?:\.\d+)*\.\s*/.freeze

  VOID_TAGS = %w[area base br col embed hr img input link meta param source track wbr].freeze
  LABEL_TAGS = %w[strong b em i].freeze

  module_function

  # -- html scanning ---------------------------------------------------------------
  # The body is a flat sequence; we only need its top level, so a depth count on one tag
  # name is enough (no <p> inside <p>, no <figure> inside <figure>).
  def split_blocks(html)
    blocks = []
    index = 0
    length = html.length

    while index < length
      open_index = html.index("<", index)

      unless open_index
        blocks << { type: :text, raw: html[index..] }
        break
      end

      if open_index > index
        blocks << { type: :text, raw: html[index...open_index] }
      end

      if html[open_index, 4] == "<!--"
        close = html.index("-->", open_index)
        close = close ? close + 3 : length
        blocks << { type: :comment, raw: html[open_index...close] }
        index = close
        next
      end

      match = html[open_index..].match(/\A<([a-zA-Z][\w:-]*)((?:"[^"]*"|'[^']*'|[^>"'])*)>/m)
      unless match
        blocks << { type: :text, raw: html[open_index] }
        index = open_index + 1
        next
      end

      tag = match[1].downcase
      open_tag = match[0]
      after_open = open_index + open_tag.length

      if VOID_TAGS.include?(tag) || open_tag.end_with?("/>")
        blocks << block_for(tag, open_tag, html[open_index...after_open])
        index = after_open
        next
      end

      close_index = matching_close(html, tag, after_open)
      unless close_index
        blocks << { type: :text, raw: html[open_index...after_open] }
        index = after_open
        next
      end

      blocks << block_for(tag, open_tag, html[open_index...close_index])
      index = close_index
    end

    blocks
  end

  def matching_close(html, tag, from)
    depth = 1
    scanner = /<(\/?)#{Regexp.escape(tag)}\b((?:"[^"]*"|'[^']*'|[^>"'])*)>/im
    position = from

    while (match = html.match(scanner, position))
      if match[1] == "/"
        depth -= 1
        return match.end(0) if depth.zero?
      elsif !match[2].to_s.strip.end_with?("/")
        depth += 1
      end

      position = match.end(0)
    end

    nil
  end

  def block_for(tag, open_tag, raw)
    { type: :element, tag: tag, open_tag: open_tag, raw: raw, classes: classes_of(open_tag) }
  end

  def classes_of(open_tag)
    (open_tag[/\sclass\s*=\s*"([^"]*)"/i, 1] || open_tag[/\sclass\s*=\s*'([^']*)'/i, 1] || "").split
  end

  def attribute_of(open_tag, name)
    open_tag[/\s#{name}\s*=\s*"([^"]*)"/i, 1] || open_tag[/\s#{name}\s*=\s*'([^']*)'/i, 1]
  end

  def text_of(html)
    html.gsub(/<[^>]*>/, " ")
        .gsub("&nbsp;", " ").gsub("&amp;", "&").gsub("&lt;", "<").gsub("&gt;", ">")
        .gsub(/\s+/, " ").strip
  end

  # -- classification --------------------------------------------------------------
  # A label is the first element of a paragraph, with nothing but space before it —
  # the same rule assets/js/main.js applies.
  def label_of(block)
    return nil unless block[:type] == :element && block[:tag] == "p"

    inner = block[:raw].sub(/\A<p\b(?:"[^"]*"|'[^']*'|[^>"'])*>/m, "").sub(%r{</p>\z}m, "")
    match = inner.match(%r{\A\s*<(#{LABEL_TAGS.join("|")})\b((?:"[^"]*"|'[^']*'|[^>"'])*)>(.*?)</\1>}m)
    return nil unless match

    { tag: match[1].downcase, attrs: match[2], html: match[3], text: text_of(match[3]),
      open_tag: "<#{match[1]}#{match[2]}>", rest: match.post_match }
  end

  def descriptor_of(block)
    label = label_of(block)
    return nil unless label

    if (entry = label[:text].match(ENTRY_RE))
      return { role: :environment, kind: entry[1], number: entry[2], label: label,
               name: statement_name(label[:rest]) }
    end

    if (numbered = label[:text].match(NUMBERED_RE))
      return { role: :section, number: numbered[1], title: numbered[2].to_s.sub(/\.\z/, ""), label: label }
    end

    if (proof = label[:text].match(PROOF_RE))
      return { role: :proof, kind: proof[1].capitalize, label: label }
    end

    nil
  end

  # `**Theorem 2.2.20** (Heine–Borel theorem).`
  def statement_name(rest)
    text_of(rest.to_s)[/\A\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)/, 1]
  end

  def marker_terminated?(kind)
    kind == "Proof" || kind == "Subproof"
  end

  def ends_environment?(block, kind)
    environment_ends(block).include?(kind.downcase)
  end

  # The QED markers in a block, in order: "proof" for □, "subproof" for ■.
  def environment_ends(block)
    return [] unless block[:type] == :element

    block[:raw].scan(/data-environment-end\s*=\s*"([^"]*)"/i).flatten
  end

  # A proof ends at its QED, so a lemma or a subproof met before that is part of the proof,
  # as `\begin{lemma}` inside `\begin{proof}` is in LaTeX. Another proof of the same rank
  # cannot be: `Proof.` competes with `Proof.`, `Subproof.` with either.
  def competing_proof?(descriptor, kind)
    return false unless descriptor && descriptor[:role] == :proof

    kind == "Proof" ? descriptor[:kind] == "Proof" : %w[Proof Subproof].include?(descriptor[:kind])
  end

  # Whether the proof opened at blocks[from] reaches its own QED before anything that would
  # end it first — the rule assets/js/main.js used (hasMatchingEnvironmentEnd). Only then may
  # it hold units; a proof without a QED ends at the next opener, as before.
  def end_ahead?(blocks, from, kind)
    blocks[from..].each_with_index do |block, offset|
      if offset.positive?
        descriptor = descriptor_of(block)
        return false if descriptor && descriptor[:role] == :section
        return false if competing_proof?(descriptor, kind) || semantic_boundary?(block)
      end
      return true if ends_environment?(block, kind)
    end
    false
  end

  def hosts?(unit, descriptor)
    unit.attrs[:hosts] && !competing_proof?(descriptor, unit.attrs[:kind])
  end

  def semantic_boundary?(block)
    return false unless block[:type] == :element

    block[:classes].include?("post-explicit-entry-break") || block[:tag].match?(/\Ah[1-6]\z/) || block[:tag] == "hr"
  end

  def continuation_marker?(block)
    block[:type] == :element && block[:classes].include?("post-structural-continuation")
  end

  # kramdown leaves display math as bare text between paragraphs (`\[…\]`), not an element,
  # so it has to be recognised here to bridge to the paragraph that continues its sentence.
  def display_math?(block)
    block[:type] == :text && block[:raw].match?(/\\\[|\$\$|\\begin\{/)
  end

  # Paragraphs in an environment, a proof or a numbered section are flush by default, so
  # only there does a structural continuation need marking; in the body and under an `##`
  # heading every paragraph is indented already.
  def indenting_unit?(unit)
    %i[environment proof].include?(unit.role) || (unit.role == :section && unit.depth.positive?)
  end

  def blank?(block)
    block[:type] != :element ? block[:raw].strip.empty? : false
  end

  # -- ids ---------------------------------------------------------------------------
  def kind_class(kind)
    kind.downcase.gsub(/[^a-z0-9]+/, "-").gsub(/\A-+|-+\z/, "")
  end

  def entry_id(kind, number, counter)
    number ? "#{kind.downcase}-#{number.tr(".", "-")}" : "math-#{kind_class(kind)}-#{counter}"
  end

  # -- the pass ----------------------------------------------------------------------
  class Unit
    attr_reader :role, :attrs, :children
    attr_accessor :depth, :open

    def initialize(role, attrs = {}, depth = 0)
      @role = role
      @attrs = attrs
      @depth = depth
      @children = []
      @open = true
    end

    def <<(node)
      @children << node
      self
    end

    def render
      return @children.join if @role == :root

      "<section#{ExternalDocumentStructure.attrs_to_s(@attrs)}>\n#{@children.join}\n</section>\n"
    end
  end

  def attrs_to_s(attrs)
    # Symbol keys (:kind) are the pass's own bookkeeping, not HTML attributes.
    attrs.reject { |name, value| name.is_a?(Symbol) || value.nil? || value.to_s.empty? }
         .map { |name, value| %( #{name}="#{value.to_s.gsub('"', "&quot;")}") }.join
  end

  def transform(html, warnings)
    blocks = split_blocks(html)
    root = Unit.new(:root)
    stack = [root]
    environment_counter = 0
    last_statement = nil
    seen_numbers = {}
    bridge = false
    structural = false

    close_to = lambda do |predicate|
      while stack.length > 1 && predicate.call(stack.last)
        finished = stack.pop
        stack.last << finished.render
      end
    end

    close_units = lambda { close_to.call(->(unit) { %i[environment proof].include?(unit.role) }) }

    blocks.each_with_index do |block, index|
      if blank?(block) || block[:type] == :comment
        stack.last << block[:raw]
        next
      end

      descriptor = descriptor_of(block)

      # --- close whatever this block ends -----------------------------------------
      if descriptor
        case descriptor[:role]
        when :section
          depth = descriptor[:number].count(".") + 1
          close_units.call
          close_to.call(->(unit) { unit.role == :section && unit.depth >= depth })
        when :environment, :proof
          close_to.call(->(unit) { %i[environment proof].include?(unit.role) && !hosts?(unit, descriptor) })
        end
      elsif block[:type] == :element && block[:tag].match?(/\Ah[1-6]\z/)
        close_units.call
        close_to.call(->(unit) { unit.role == :section })
        heading_level = block[:tag][1].to_i
        heading_id = attribute_of(block[:open_tag], "id")
        stack.push(Unit.new(:section, {
          "class" => "doc-section doc-section--heading semantic-unit",
          "data-doc" => heading_level <= 2 ? "section" : "subsection",
          "data-title" => text_of(block[:raw]),
          "id" => heading_id ? "unit-#{heading_id}" : nil
        }, 0))
      elsif semantic_boundary?(block)
        close_units.call
      elsif block[:type] == :element && block[:tag] == "p" && !bridge && !continuation_marker?(block)
        # A plain paragraph ends a statement, unless a figure, list or display equation
        # bridged to it — the rule assets/js/main.js has always used.
        close_to.call(->(unit) { unit.role == :environment && !marker_terminated?(unit.attrs[:kind]) })
      end

      # --- open what this block starts ----------------------------------------------
      case descriptor && descriptor[:role]
      when :section
        number = descriptor[:number]
        depth = number.count(".") + 1
        check_sequence(seen_numbers, :section, number, warnings)
        id = "sec-#{number.tr('.', '-')}"
        unit = Unit.new(:section, {
          "class" => "doc-section doc-section--numbered semantic-unit",
          "data-doc" => depth == 1 ? "subsection" : "subsubsection",
          "data-number" => number,
          "data-title" => descriptor[:title],
          "id" => "unit-#{id}"
        }, depth)
        last_statement = nil            # a proof in this part proves the part, until a statement opens
        stack.push(unit)
        block = with_label_attrs(block, descriptor[:label],
                                 "id" => id,
                                 "class" => "math-label-anchor doc-heading",
                                 "role" => "heading",
                                 "aria-level" => (depth + 2).clamp(2, 6).to_s)
      when :environment
        environment_counter += 1
        kind = descriptor[:kind]
        scope = OWN_COUNTER.include?(kind) ? kind : :environment
        check_sequence(seen_numbers, scope, descriptor[:number], warnings) if descriptor[:number]
        id = entry_id(kind, descriptor[:number], environment_counter)
        last_statement = id
        classes = ["semantic-unit", "math-environment", "math-environment--#{kind_class(kind)}"]
        classes << "math-statement-italic" if ITALIC_KINDS.include?(kind)
        unit = Unit.new(:environment, {
          "class" => classes.join(" "),
          "data-doc" => kind.downcase,
          "data-environment-kind" => kind,
          "data-number" => descriptor[:number],
          "data-name" => descriptor[:name],
          "id" => "unit-#{id}",
          "aria-labelledby" => id
        })
        unit.attrs[:kind] = kind
        stack.push(unit)
        block = with_label_attrs(block, descriptor[:label], "id" => id, "class" => "math-label-anchor")
      when :proof
        environment_counter += 1
        kind = descriptor[:kind]
        enclosing = stack.last.role == :section ? stack.last.attrs["id"].to_s.sub(/\Aunit-/, "") : nil
        proves = last_statement || enclosing
        id = proves ? "proof-#{proves}" : "math-#{kind_class(kind)}-#{environment_counter}"
        unit = Unit.new(:proof, {
          "class" => "semantic-unit math-environment math-environment--#{kind_class(kind)}",
          "data-doc" => "proof",
          "data-environment-kind" => kind,
          "data-proves" => proves,
          "id" => "unit-#{id}"
        })
        unit.attrs[:kind] = kind
        unit.attrs[:hosts] = marker_terminated?(kind) && end_ahead?(blocks, index, kind)
        stack.push(unit)
        block = with_label_attrs(block, descriptor[:label], "id" => id, "class" => "math-proof-marker")
      end

      # Two blank lines after a figure, list or display equation start a new paragraph of the
      # same unit, which is indented (post.css); one blank line continues the sentence.
      if structural && descriptor.nil? && block[:type] == :element && block[:tag] == "p" &&
         indenting_unit?(stack.last)
        block = block.merge(raw: block[:raw].sub(/\A<p\b/, '<p data-paragraph-continuation="structural"'))
      end

      stack.last << block[:raw]

      # --- close what this block finished --------------------------------------------
      # Each QED closes the innermost open proof of its kind, and whatever is still open
      # inside that proof (a lemma bridged to the closing paragraph).
      environment_ends(block).each do |ended|
        finished = stack.reverse.find do |unit|
          %i[environment proof].include?(unit.role) && marker_terminated?(unit.attrs[:kind]) &&
            unit.attrs[:kind].downcase == ended
        end
        close_to.call(->(_unit) { stack.include?(finished) }) if finished
      end

      structural = if continuation_marker?(block)
                     bridge
                   elsif display_math?(block) || block[:type] == :element
                     false
                   else
                     structural
                   end

      bridge = if display_math?(block)
                 true
               elsif block[:type] != :element || continuation_marker?(block)
                 bridge
               else
                 block[:tag] != "p"
               end
    end

    close_to.call(->(_unit) { true })
    root.render
  end

  # Numbers are read, not generated; a break in the sequence is worth a warning, not a fix.
  # Environments in these posts share one counter per prefix — Definition 2.2.1, Definition
  # 2.2.2, Theorem 2.2.3 — which is LaTeX's \newtheorem{...}[shared]{...}[subsection]. So the
  # sequence is tracked per prefix, across kinds, and only a repeat or a step backwards is
  # reported: a gap can be deliberate (a result stated in another post).
  def check_sequence(seen, scope, number, warnings)
    return if number.nil?

    parts = number.split(".")
    key = [scope, parts[0..-2]]
    previous = seen[key]
    seen[key] = number
    return if previous.nil?

    last = previous.split(".").last.to_i
    current = parts.last.to_i
    return if current > last

    warnings << "#{number} follows #{previous}"
  end

  def with_label_attrs(block, label, attrs)
    open_tag = label[:open_tag]
    existing = classes_of(open_tag)
    merged = attrs.dup
    if merged["class"]
      merged["class"] = (existing + merged["class"].split).uniq.join(" ")
    end

    rebuilt = "<#{label[:tag]}"
    kept = label[:attrs].to_s.gsub(/\s(?:id|class|role|aria-level)\s*=\s*(?:"[^"]*"|'[^']*')/i, "")
    rebuilt += kept
    rebuilt += attrs_to_s(merged)
    rebuilt += ">"

    block.merge(raw: block[:raw].sub(open_tag, rebuilt))
  end

  # -- entry point ---------------------------------------------------------------------
  def domain_of(document)
    path = document.data["category_path"]
    return nil unless path.is_a?(Array) && path.first

    path.first.to_s.strip.sub(ORDER_PREFIX, "").downcase.gsub(/[^a-z0-9]+/, "-").gsub(/\A-+|-+\z/, "")
  end

  def process(document)
    return unless document.respond_to?(:collection) && document.collection&.label == "posts"
    return unless DOMAINS.include?(domain_of(document))
    return if document.content.to_s.strip.empty?

    warnings = []
    document.content = transform(document.content, warnings)
    document.data["document_structure"] = true
    warnings.each do |warning|
      Jekyll.logger.warn "Structure:", "#{document.relative_path}: #{warning}"
    end
  end
end

Jekyll::Hooks.register :documents, :post_convert do |document|
  ExternalDocumentStructure.process(document)
end
