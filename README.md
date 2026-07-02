[Go to page](https://yeonsolkim.github.io/external/)

## Development Notes

This site contains many Markdown posts with inline LaTeX math written as
`$...$`. Plain GitHub Pages/Jekyll rendering can confuse characters inside
math, especially `_` and `*`, with Markdown emphasis syntax. Typical symptoms
are:

- Inline math such as `$<_A$` opening an unintended `<em>` tag.
- Text such as `*lexicographic order relation*` appearing literally instead of
  italicized.
- Ordinary emphasis near math being broken by underscores inside math.

To avoid this, `_plugins/inline_math_preprocessor.rb` protects inline math
before Markdown rendering and restores it afterward as:

```html
<span class="math-inline">\( ... \)</span>
```

This means these math/emphasis issues should be fixed at the build layer, not by
rewriting each post.

## Repository Structure Notes

The repo intentionally uses a few Jekyll-specific files that may look
removable at first glance. Keep these notes in mind before simplifying the
structure.

### Posts and Categories

- `_posts` is the content source. Nested folders are meaningful, not just
  organization.
- Each post has `category_path` in its front matter. This mirrors the folder
  path under `_posts` and is used for the home page category tree, post header
  category label, and theorem/definition reference scope.
- Numbered and roman-numeral folder prefixes such as `I. Calculus` and
  `1. Vector Spaces` are used for ordering. The UI hides many of these prefixes
  when displaying titles/categories, so do not remove them only because they are
  not visible on the site.
- `_site` is generated output. Do not edit `_site` directly; changes should be
  made in `_posts`, layouts, includes, assets, or plugins.

### Front Matter

- `scripts/sync_posts_front_matter.py` manages the standard front matter keys:
  `layout`, `title`, `date`, `category_path`, `created_at`, and
  `last_modified_at`.
- Running the sync script may rewrite those managed keys based on filename,
  folder path, and file timestamps. Put custom front matter in other keys if it
  should be preserved.
- New posts should keep the filename pattern `YYYY-MM-DD-title.md`. Files
  without a date prefix may be renamed by the sync script.
- The Obsidian templates in `templates/` help create/update post front matter,
  but the Python sync script is the more consistent source of truth when many
  files need repair.

### Home Page Category Tree

- `index.md` discovers top-level categories from `site.posts`, then renders
  them using `_includes/category_tree.html`.
- `_includes/category_tree.html` recursively groups posts by `category_path`.
  It also hides numeric prefixes in visible category and post labels while
  preserving those prefixes in the real folder/title data for ordering.
- `assets/js/edited-time.js` only runs on the home page and turns
  `last_modified_at` into relative edited-time labels.

### Post Layout

- `_layouts/post.html` removes numeric title prefixes from visible post titles.
  For example, `3. Relations` displays as `Relations`.
- The post header shows the second item of `category_path` above the title and
  strips roman prefixes there. For example, `III. Topology` displays as
  `Topology`.
- The layout sets `data-reference-scope` from `category_path[1]`. This is what
  keeps theorem/definition links scoped by subject, such as Calculus, Linear
  Algebra, or Topology.
- Post dates use `"%B %-d, %Y"` so dates render as `June 2, 2026`, not
  `June 02, 2026`.

### Reference Links

- `assets/js/main.js` is a Jekyll-processed JavaScript file. The leading
  front matter markers are intentional because Liquid is used inside the file.
- It scans posts for labels such as `Definition 1.3.9` and links references to
  matching labels in the same `data-reference-scope`.
- If theorem/definition links disappear, check that `category_path[1]`,
  `_layouts/post.html`, and the Liquid-generated `labelSources` in
  `assets/js/main.js` still agree.

### Math and Post Styling

- `assets/js/mathjax-config.js` prepares math before MathJax runs. It handles
  raw `$...$` fallback normalization, list items containing display math,
  ordered-list marker prefixes, mobile math scrolling, and MathJax startup
  visibility.
- `assets/css/post.css` is paired with `mathjax-config.js`. It styles custom
  ordered-list markers, display math scrolling, reference-link boxes, QED
  markers, and hides the post body while MathJax is loading.
- `assets/css/style.scss` imports the Cayman theme and applies global site
  overrides. The front matter at the top is intentional so Jekyll processes the
  Sass file.
- `assets/css/index.css` is only for the home page category tree and edited
  time labels.

### Other Includes

- `_includes/comments.html` contains the Giscus comment embed used by
  `_layouts/post.html`.
- `_includes/head.html` is not currently included by the active layout. Check
  before relying on it for live page behavior.

## GitHub Pages Deployment

GitHub Pages' default "Deploy from a branch" build does not run custom Jekyll
plugins from `_plugins`. If the live site is built that way, inline math may
remain as raw `$...$`, and Markdown emphasis can break again.

Use the GitHub Actions workflow in `.github/workflows/pages.yml` instead. It
runs:

```sh
bundle exec jekyll build
```

and therefore includes the custom inline math preprocessor.

Important Pages setting:

- Repository Settings -> Pages -> Source should be set to `GitHub Actions`.

After pushing to `main`, the workflow should build and deploy the site.

## Local Build

On this machine, use Homebrew Ruby's Bundler:

```sh
/opt/homebrew/opt/ruby/bin/bundle exec jekyll build
```

For local preview:

```sh
/opt/homebrew/opt/ruby/bin/bundle exec jekyll serve
```
