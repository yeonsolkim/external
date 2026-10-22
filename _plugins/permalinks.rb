# frozen_string_literal: true

require "cgi"
require "json"

# Where posts live, and where they used to.
#
# A post's URL is its subject and its title, both without ordering numbers:
# `_posts/1. Mathematics/2. Algebra/1. Linear Algebra/1. Vector Spaces/2026-06-02-1. Vector Spaces.md`
# is served at /linear-algebra/vector-spaces/. The subject is the textbook, the folder above
# the section (a post filed directly under a second-level category takes that category); a
# label "Others" names no subject, so the level above it stands in, and the section is
# added. Renumbering a post or moving it within its textbook leaves the URL alone.
#
# The URL is frozen on first publication: scripts/sync_posts_front_matter.py, run with
# --freeze-permalinks by `site.zsh publish`, writes it into the front matter as
# `permalink:`, like `title`, and never changes a permalink already there. A post with a
# permalink keeps it here too; one without (a draft never published) gets the derived URL.
# The derivation below and `derived_permalinks` in the sync script must agree, URL for URL.
#
# When two posts would share a URL, both take their section's name after the title
# (/introduction-to-analysis/exercises-metric-spaces/); a URL already frozen keeps it.
#
# _data/redirects.yml maps each old URL to the page that replaced it. Each old URL gets a
# small page that sends readers and search engines on: an instant meta refresh, which
# Google treats as a permanent redirect, a canonical link and noindex. Redirect pages stay
# out of the sitemap, and they are not posts, so the narration ignores them.
module ExternalPermalinks
  ORDER_PREFIX = /\A(?:(?:[IVXLCDM]+)|(?:\d+))[.)]\s*/i.freeze
  NUMBERED_TITLE = /\A(?:(?:[IVXLCDM]+)|(?:\d+(?:\.\d+)*))[.)]\s*/i.freeze
  GENERIC_LABEL = /\Aothers?\z/i.freeze
  # Latin letters Unicode does not decompose into a base letter and an accent.
  FOLDED = {
    "ß" => "ss", "æ" => "ae", "Æ" => "AE", "œ" => "oe", "Œ" => "OE", "ø" => "o", "Ø" => "O",
    "đ" => "d", "Đ" => "D", "ð" => "d", "Ð" => "D", "ł" => "l", "Ł" => "L", "þ" => "th",
    "Þ" => "Th", "ı" => "i"
  }.freeze

  module_function

  # Lower-case ASCII words joined by hyphens: "Axioms of Zermelo–Fraenkel Theory" →
  # "axioms-of-zermelo-fraenkel-theory", "Naïve Set Theory" → "naive-set-theory".
  def slug(text)
    plain = text.to_s.unicode_normalize(:nfkd).gsub(/\p{Mn}/, "")
    plain = plain.gsub(Regexp.union(FOLDED.keys), FOLDED)
    plain.downcase.gsub(/[^a-z0-9]+/, "-").gsub(/\A-+|-+\z/, "")
  end

  def labels(category_path)
    Array(category_path).map { |part| part.to_s.strip.sub(ORDER_PREFIX, "") }.reject(&:empty?)
  end

  # [the folders the URL is made of, the post's own name, the section's name or nil]
  def parts(category_path, title, date)
    path = labels(category_path)
    chain = path.length >= 3 ? path[0...-1] : path
    section = path.length >= 3 ? path.last : nil
    folders = []
    subject = chain.reverse.find { |label| !label.match?(GENERIC_LABEL) }
    folders << subject if subject
    folders << section if section && chain.last.to_s.match?(GENERIC_LABEL)
    name = slug(title.to_s.strip.sub(NUMBERED_TITLE, ""))
    name = date.to_s if name.empty?
    [folders.map { |folder| slug(folder) }.reject(&:empty?), name, section && slug(section)]
  end

  def url(folders, name)
    "/#{(folders + [name]).join('/')}/"
  end

  # `posts` are [key, category_path, title, date (YYYY-MM-DD), frozen permalink or nil].
  # Returns { key => URL } for the posts without a permalink.
  def derive(posts)
    taken = posts.filter_map { |*, frozen| frozen.to_s.strip.empty? ? nil : frozen.strip }
    open = posts.select { |*, frozen| frozen.to_s.strip.empty? }
    plans = open.to_h { |key, category_path, title, date, _| [key, parts(category_path, title, date)] }

    first = plans.transform_values { |folders, name, _| url(folders, name) }
    counts = first.values.tally
    urls = first.to_h do |key, candidate|
      folders, name, section = plans[key]
      shared = counts[candidate] > 1 || taken.include?(candidate)
      [key, shared && section && !section.empty? ? url(folders, "#{name}-#{section}") : candidate]
    end

    # Still shared (no section to tell the posts apart): the date says which is which.
    counts = urls.values.tally
    urls.to_h do |key, candidate|
      next [key, candidate] unless counts[candidate] > 1 || taken.include?(candidate)

      date = open.find { |entry| entry[0] == key }[3]
      [key, candidate.sub(%r{/\z}, "-#{date}/")]
    end
  end

  def assign(posts)
    entries = posts.map do |post|
      # The file name's date, as the sync script reads it (post.date is the UTC day before).
      date = File.basename(post.relative_path)[/\A\d{4}-\d{2}-\d{2}/] || post.date.strftime("%Y-%m-%d")
      [post, post.data["category_path"], post.data["title"], date, post.data["permalink"]]
    end
    derive(entries).each { |post, permalink| post.data["permalink"] = permalink }
  end

  def redirect_html(target)
    escaped = CGI.escapeHTML(target)
    <<~HTML
      <!DOCTYPE html>
      <html lang="en">
      <head>
      <meta charset="utf-8">
      <title>Moved</title>
      <link rel="canonical" href="#{escaped}">
      <meta name="robots" content="noindex">
      <meta http-equiv="refresh" content="0; url=#{escaped}">
      <script>location.replace(#{target.to_json} + location.hash);</script>
      </head>
      <body>
      <p>This page has moved to <a href="#{escaped}">#{escaped}</a>.</p>
      </body>
      </html>
    HTML
  end
end

if defined?(Jekyll::Generator)
  module Jekyll
    class RedirectPage < PageWithoutAFile
      def initialize(site, from, target)
        super(site, site.source, File.dirname(from), File.basename(from))
        self.content = ExternalPermalinks.redirect_html(target)
        self.data = { "permalink" => from, "sitemap" => false, "redirect" => true }
      end
    end

    class RedirectsGenerator < Generator
      safe true
      # After the category indexes exist, so a redirect may point at one.
      priority :low

      def generate(site)
        redirects = site.data["redirects"] || {}
        pages = (site.posts.docs + site.pages).to_h { |page| [page.url, page] }
        base = site.config["url"].to_s.chomp("/") + site.config["baseurl"].to_s.chomp("/")

        redirects.each do |from, to|
          from = from.to_s
          to = to.to_s
          if pages.key?(from)
            Jekyll.logger.warn "Redirects:", "#{from} is a page of the site; not redirecting it to #{to}"
            next
          end
          unless pages.key?(to)
            Jekyll.logger.warn "Redirects:", "#{from} points to #{to}, which is not a page of the site"
          end
          site.pages << RedirectPage.new(site, from, to.start_with?("/") ? base + to : to)
        end
      end
    end
  end

  # Before any URL is asked for: the generators and the layouts take it from here on.
  Jekyll::Hooks.register :site, :post_read do |site|
    ExternalPermalinks.assign(site.posts.docs)
  end
end
