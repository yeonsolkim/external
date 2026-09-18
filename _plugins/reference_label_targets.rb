# frozen_string_literal: true

module ExternalReferenceLabelTargets
  LABEL_PATTERN = %r{
    (?:\*\*|<(?:strong|b)\b[^>]*>)\s*
    (Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle)\s+
    (\d+(?:\.\d+)+)\.?
    (?=\s|\*|\)|</(?:strong|b)>)
  }x.freeze

  module_function

  def build(site)
    targets_by_scope = {}
    baseurl = site.baseurl.to_s.sub(%r{/\z}, "")

    site.posts.docs.each do |post|
      scope = reference_scope(post)
      next if scope.empty?

      scope_targets = (targets_by_scope[scope] ||= {})

      post.content.to_s.scan(LABEL_PATTERN) do |kind, number|
        href = "#{baseurl}#{post.url}##{anchor_id(kind, number)}"

        if scope_targets.key?(number) && scope_targets[number] != href
          scope_targets[number] = nil
        else
          scope_targets[number] = href
        end
      end
    end

    targets_by_scope.sort.to_h.transform_values { |targets| targets.sort.to_h }
  end

  def reference_scope(post)
    path = post.data["category_path"] || post.data["categories"] || []
    textbook = Jekyll::CategoryLabels.textbook_category(path)
    label = Jekyll::CategoryLabels.strip_order_prefix(textbook)

    Jekyll::Utils.slugify(label)
  end

  def anchor_id(kind, number)
    "#{kind.downcase}-#{number.tr('.', '-')}"
  end
end

module Jekyll
  class ReferenceLabelTargetsGenerator < Generator
    safe true
    priority :low

    def generate(site)
      site.data["reference_label_targets"] = ExternalReferenceLabelTargets.build(site)
    end
  end
end
