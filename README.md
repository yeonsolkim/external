## Development Notes

### Commutative Diagrams

Posts can use a `tikzcd` environment inside display-math delimiters. Do not add
a document class, package imports, or a `document` environment to the post:

````markdown
$$
\begin{tikzcd}
A \arrow{r}{f} \arrow[swap]{dr}{g\circ f} & B \arrow{d}{g} \\
 & C
\end{tikzcd}
$$
````

The concise ```` ```tikzcd ```` fenced form remains supported for existing
posts.

`_plugins/tikzcd_renderer.rb` wraps each block in a standalone LaTeX document,
compiles it with `latex`, converts the DVI output to inline SVG with `dvisvgm`,
and caches the undecorated SVG under `.jekyll-cache/tikzcd`. The generated SVG
IDs are namespaced before insertion so multiple diagrams can safely appear in
one post.

For Obsidian preview, enable the tracked `TikZ-cd Preview` plugin and install a
TeX distribution that provides `latex`, `dvisvgm`, and `tikz-cd`. The plugin
runs before the normal Markdown post-processors, diverts display-math `tikzcd`
environments to the same TeX-to-SVG pipeline used by the site, and leaves all
other display math for MathJax. Its SVG output is scaled to match the
surrounding MathJax typography.

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

When punctuation immediately follows inline math, the preprocessor moves that
punctuation into the same wrapper and adds `math-inline-punctuated`. The paired
CSS rule prevents a line break from leaving the punctuation on a line by itself.

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

- `index.md` discovers top-level categories from `site.posts`. It keeps posts
  whose `category_path` has only one item directly on the home page and links
  each second-level category to its own generated index page.
- The penultimate folder in a post's `category_path` represents its textbook;
  the final folder represents a section within that textbook. A textbook's
  ordering prefix is hidden in category entries and breadcrumbs.
- `_plugins/subcategory_pages_generator.rb` creates an index page for every
  distinct `category_path` prefix below the top level through the textbook. For
  example, a post at `Mathematics / Algebra / Linear Algebra / Vector Spaces`
  produces pages for `Algebra` and `Linear Algebra`, but not `Vector Spaces`.
  Generated URLs mirror that hierarchy under `/categories/`; ordering prefixes
  are omitted from URL slugs so reordering categories does not break links.
- `_layouts/subcategory.html` normally renders direct posts and the immediately
  nested categories for the selected path. When the selected path is the
  textbook, it also expands each final folder's posts as a hierarchical contents
  list. Final folders are headings rather than links because they do not have
  separate index pages. The textbook is detected from the path rather than from
  a fixed depth. Textbook pages receive their own contents-layout class; other
  generated indexes use the same category-tree styling as the home page.
- `_includes/category_tree.html` recursively groups posts by `category_path`.
  It also hides numeric and roman-numeral ordering prefixes in visible category
  and post labels while preserving those prefixes in the real folder/title data
  for ordering.
- `assets/js/edited-time.js` runs on the home page and generated category index
  pages, turning `last_modified_at` into relative edited-time labels.

### Post Layout

- `_layouts/post.html` builds a visible post number from the final section
  folder and the post title. A textbook's own ordering prefix is not included.
- The post header shows the second item of `category_path` above the title and
  strips ordering prefixes there. For example, `III. Topology` displays as
  `Topology` and links to that subcategory's generated index page.
- The layout sets `data-reference-scope` from the penultimate, textbook folder.
  This keeps theorem/definition links scoped to their textbook even when more
  category layers are inserted before it. Its ordering prefix is stripped so
  reordering textbooks does not change the reference scope.
- Post dates use `"%B %-d, %Y"` so dates render as `June 2, 2026`, not
  `June 02, 2026`.

### Reference Links

- `assets/js/main.js` is a Jekyll-processed JavaScript file. The leading
  front matter markers are intentional because Liquid is used inside the file.
- It scans posts for labels such as `Definition 1.3.9` and links references to
  matching labels in the same `data-reference-scope`.
- If theorem/definition links disappear, check the `textbook_category` filter,
  `_layouts/post.html`, and the Liquid-generated `labelSources` in
  `assets/js/main.js` still agree.

### Math and Post Styling

- `assets/js/mathjax-config.js` prepares math before MathJax runs. It handles
  raw `$...$` fallback normalization, list items containing display math,
  ordered-list marker prefixes, mobile math scrolling, and MathJax startup
  visibility. It also defines `\lowparen{...}` for a lowered, fixed-size pair
  of parentheses around large operators with lower limits.
- `_posts/.obsidian/plugins/tikzcd-preview/main.js` registers the same
  `\lowparen{...}` definition with Obsidian's MathJax instance when the vault
  plugin loads.
- Statement names written immediately after a numbered label, such as
  `**Theorem 1.1.1.** (Example name).`, are kept upright even when theorem
  text is italicized.
- For bibliography-style lists under `## References`, use an ordered list and
  put `{:reference}` directly below it. The preprocessor maps that tag to
  `class="reference"`, and ordered-list markers render as `[1]` instead of
  `(1)`.
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

Pull requests targeting `main` run `.github/workflows/pr-build.yml`. This
workflow performs the complete Jekyll build with read-only repository
permissions and does not upload or deploy a Pages artifact.

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
