# frozen_string_literal: true

module Jekyll
  module CategoryLabels
    ORDER_PREFIX = /\A(?:(?:[IVXLCDM]+)|(?:\d+))[.)]\s*/i
    NUMBERED_LABEL = /\A((?:[IVXLCDM]+)|(?:\d+(?:\.\d+)*))[.)]\s*/i

    module_function

    def strip_order_prefix(label)
      label.to_s.strip.sub(ORDER_PREFIX, "")
    end

    def hierarchical_post_title(title, category_path)
      clean_title = title.to_s.strip
      title_match = clean_title.match(NUMBERED_LABEL)
      return clean_title unless title_match

      title_number = title_match[1]
      visible_title = clean_title.sub(NUMBERED_LABEL, "")
      title_gap = "\u00A0\u00A0"
      return "#{title_number}.#{title_gap}#{visible_title}" if title_number.include?(".")

      path = category_path.is_a?(Array) ? category_path : [category_path]
      ancestor_numbers = path.drop(2).filter_map do |category|
        category.to_s.strip.match(NUMBERED_LABEL)&.[](1)
      end

      visible_number = ancestor_numbers.empty? ? title_number : (ancestor_numbers + [title_number]).join(".")

      "#{visible_number}.#{title_gap}#{visible_title}"
    end
  end

  module CategoryLabelFilters
    def strip_category_order_prefix(label)
      CategoryLabels.strip_order_prefix(label)
    end

    def hierarchical_post_title(title, category_path)
      CategoryLabels.hierarchical_post_title(title, category_path)
    end
  end
end

Liquid::Template.register_filter(Jekyll::CategoryLabelFilters)
