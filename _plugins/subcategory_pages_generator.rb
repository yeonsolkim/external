# frozen_string_literal: true

module Jekyll
  class SubcategoryIndexPage < PageWithoutAFile
    def initialize(site, dir, parent_category, subcategory)
      super(site, site.source, dir, "index.html")

      self.content = ""
      self.data = {
        "layout" => "subcategory",
        "title" => subcategory,
        "index_page" => true,
        "generated_subcategory" => true,
        "parent_category" => parent_category,
        "subcategory" => subcategory
      }
    end
  end

  class SubcategoryPagesGenerator < Generator
    safe true
    priority :high

    ORDER_PREFIX = /\A(?:(?:[IVXLCDM]+)|(?:\d+))[.)]\s*/i

    def generate(site)
      pairs = site.posts.docs.filter_map do |post|
        path = normalized_category_path(post)
        path.first(2) if path.length >= 2
      end

      pages = pairs.uniq.sort_by { |parent, subcategory| [parent, subcategory] }.map do |parent, subcategory|
        build_page_spec(parent, subcategory)
      end

      ensure_unique_urls!(pages)
      site.data["generated_subcategory_pages"] = pages

      pages.each do |page_spec|
        site.pages << SubcategoryIndexPage.new(
          site,
          page_spec["dir"],
          page_spec["parent_category"],
          page_spec["subcategory"]
        )
      end
    end

    private

    def normalized_category_path(post)
      raw_path = post.data["category_path"] || post.data["categories"] || []
      raw_path = [raw_path] unless raw_path.is_a?(Array)
      raw_path.map { |part| part.to_s.strip }.reject(&:empty?)
    end

    def build_page_spec(parent, subcategory)
      dir = File.join("categories", stable_slug(parent), stable_slug(subcategory))

      {
        "parent_category" => parent,
        "subcategory" => subcategory,
        "dir" => dir,
        "url" => "/#{dir}/"
      }
    end

    def stable_slug(label)
      unnumbered_label = label.sub(ORDER_PREFIX, "")
      slug = Jekyll::Utils.slugify(unnumbered_label, mode: "default", cased: false)

      return slug unless slug.empty?

      raise Errors::FatalException, "Cannot generate a category URL from #{label.inspect}."
    end

    def ensure_unique_urls!(pages)
      owners_by_url = {}

      pages.each do |page|
        owner = [page["parent_category"], page["subcategory"]]
        existing_owner = owners_by_url[page["url"]]

        if existing_owner && existing_owner != owner
          raise Errors::FatalException,
                "Subcategory URL collision at #{page['url']}: #{existing_owner.inspect} and #{owner.inspect}."
        end

        owners_by_url[page["url"]] = owner
      end
    end
  end
end
