# frozen_string_literal: true

module Jekyll
  class SubcategoryIndexPage < PageWithoutAFile
    def initialize(site, page_spec)
      category_path = page_spec["category_path"]

      super(site, site.source, page_spec["dir"], "index.html")

      self.content = ""
      self.data = {
        "layout" => "subcategory",
        "title" => category_path.last,
        "index_page" => true,
        "generated_subcategory" => true,
        "category_path" => category_path,
        "parent_category" => page_spec["parent_category"],
        "subcategory" => page_spec["subcategory"]
      }
    end
  end

  class SubcategoryPagesGenerator < Generator
    safe true
    priority :high

    def generate(site)
      category_paths = site.posts.docs.filter_map do |post|
        path = normalized_category_path(post)
        path.first(2) if path.length >= 2
      end

      pages = category_paths.uniq.sort.map do |category_path|
        build_page_spec(category_path)
      end

      ensure_unique_urls!(pages)
      site.data["generated_subcategory_pages"] = pages

      pages.each do |page_spec|
        site.pages << SubcategoryIndexPage.new(site, page_spec)
      end
    end

    private

    def normalized_category_path(post)
      raw_path = post.data["category_path"] || post.data["categories"] || []
      raw_path = [raw_path] unless raw_path.is_a?(Array)
      raw_path.map { |part| part.to_s.strip }.reject(&:empty?)
    end

    def build_page_spec(category_path)
      dir = File.join("categories", *category_path.map { |part| stable_slug(part) })

      {
        "category_path" => category_path,
        "path_key" => category_path.join("|"),
        "depth" => category_path.length,
        "parent_category" => category_path[0...-1].join("|"),
        "subcategory" => category_path.last,
        "dir" => dir,
        "url" => "/#{dir}/"
      }
    end

    def stable_slug(label)
      unnumbered_label = CategoryLabels.strip_order_prefix(label)
      slug = Jekyll::Utils.slugify(unnumbered_label, mode: "default", cased: false)

      return slug unless slug.empty?

      raise Errors::FatalException, "Cannot generate a category URL from #{label.inspect}."
    end

    def ensure_unique_urls!(pages)
      owners_by_url = {}

      pages.each do |page|
        owner = page["category_path"]
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
