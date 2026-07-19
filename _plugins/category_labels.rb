# frozen_string_literal: true

module Jekyll
  module CategoryLabels
    ORDER_PREFIX = /\A(?:(?:[IVXLCDM]+)|(?:\d+))[.)]\s*/i

    module_function

    def strip_order_prefix(label)
      label.to_s.strip.sub(ORDER_PREFIX, "")
    end
  end

  module CategoryLabelFilters
    def strip_category_order_prefix(label)
      CategoryLabels.strip_order_prefix(label)
    end
  end
end

Liquid::Template.register_filter(Jekyll::CategoryLabelFilters)
