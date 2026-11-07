# frozen_string_literal: true

require "fileutils"
require "yaml"

# Each post's Markdown source, served beside its page: the post at /linear-algebra/lattices/
# has its source at /linear-algebra/lattices.md, which the page names in its <head> as an
# alternate (_layouts/default.html). The page stays what readers get; the source is the same
# text as plain Markdown and TeX, for a program that would rather not read the rendered HTML.
#
# Everything after the front matter is the post's file, byte for byte. It is read from disk
# because the plugins here rewrite a post's content in memory. The front matter says where the
# text comes from (`canonical_url`, `author`) and keeps the entries of KEPT_KEYS as the file
# writes them; the others only steer the build, and a new key stays private until it is added.
# `source_note` must stay: it credits the books a post draws on, in front matter, not the text.
#
# A source is a static file, because a page ending in .md would go through Liquid and kramdown
# and come out as HTML. Only posts that are built get one, so an unpublished post has no
# source. The sitemap takes HTML and PDF files only. GitHub Pages cannot send a noindex header,
# so pages/robots.txt keeps Googlebot off the sources: the page is what should rank.
module ExternalMarkdownSources
  KEPT_KEYS = %w[title description date last_modified_at source_note].freeze
  KEY_LINE = /\A[a-z_]+(?=:)/.freeze
  # Jekyll's own pattern also takes the blank lines after the closing line, which are the text's.
  FRONT_MATTER = /\A(---.*?\n)^(?:---|\.\.\.)[ \t]*\r?(?:\n|\z)/m.freeze

  module_function

  def url_for(post_url)
    "#{post_url.chomp('/')}.md"
  end

  # The entries of a front matter that are kept, as written. The lines under a key (the items
  # of a list, a value on several lines) belong to it.
  def kept_entries(front_matter)
    front_matter.lines.slice_before(KEY_LINE)
                .select { |lines| KEPT_KEYS.include?(lines.first[KEY_LINE]) }
                .join
  end

  def document(raw, canonical_url, author)
    match = raw.match(FRONT_MATTER)
    origin = { "canonical_url" => canonical_url, "author" => author }.compact
    "#{origin.to_yaml}#{kept_entries(match[1])}---\n#{match.post_match}"
  end
end

if defined?(Jekyll::Generator)
  module Jekyll
    class MarkdownSource < StaticFile
      def initialize(site, post)
        @post = post
        url = ExternalMarkdownSources.url_for(post.url)
        super(site, site.source, File.dirname(url), File.basename(url))
      end

      # The post's file, so that Jekyll asks it for the modification time.
      def path
        @post.path
      end

      def write(dest)
        target = destination(dest)
        FileUtils.mkdir_p(File.dirname(target))
        File.write(target, text)
        true
      end

      private

      def text
        raw = File.read(path, **Utils.merged_file_read_opts(@site, {}))
        base = @site.config["url"].to_s.chomp("/") + @site.config["baseurl"].to_s.chomp("/")
        ExternalMarkdownSources.document(raw, base + @post.url, @site.config["author"])
      end
    end

    class MarkdownSourcesGenerator < Generator
      safe true

      def generate(site)
        site.posts.docs.each do |post|
          source = MarkdownSource.new(site, post)
          post.data["markdown_source"] = source.url
          site.static_files << source
        end
      end
    end
  end
end
