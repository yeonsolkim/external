# frozen_string_literal: true

# Posts are dated in Korea, as their front matter writes (`date: 2026-10-09 00:00:00 +0900`),
# but the site builds in UTC (_config.yml), where that instant falls on October 8. A date shown
# to readers is the day in Korea: `{{ page.date | kst_date }}` → "October 9, 2026".
module Jekyll
  module KstDateFilter
    KST = "+09:00"

    def kst_date(input, format = "%B %-d, %Y")
      time = Liquid::Utils.to_date(input)
      return input unless time

      time = time.to_time unless time.respond_to?(:getlocal)
      time.getlocal(KST).strftime(format)
    end
  end
end

Liquid::Template.register_filter(Jekyll::KstDateFilter)
