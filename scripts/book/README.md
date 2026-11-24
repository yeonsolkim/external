# Books

`build_book.py` typesets one textbook of the site, the posts under one textbook folder, as
a book: a section folder is a chapter, a post is a section. LuaLaTeX produces either the
approved `springer` design (the default) or the earlier `external` design.

```sh
python3 scripts/book/build_book.py                        # Linear Algebra
python3 scripts/book/build_book.py "Linear Algebra" --open
python3 scripts/book/build_book.py "Introduction to Analysis" --drafts
python3 scripts/book/build_book.py "Linear Algebra" --style external
python3 scripts/book/build_book.py "Linear Algebra" --section lattices
```

It needs what the site build needs (Homebrew Ruby's Bundler) and TeX Live with LuaLaTeX,
latexmk and the `newcomputermodern` fonts. The Springer edition also needs `newtxtext` and
`newtxmath`; its official `SNmono` class and MakeIndex style are kept under
`vendor/springer/`.

Everything goes under `~/Library/Caches/External-Jekyll/book/<textbook>/`. The built site
(`site/`) is shared, while styles and section samples have separate LaTeX directories:

| build | LaTeX directory | PDF |
|---|---|---|
| default / `--style springer` | `springer/tex/` | `springer/<Textbook> - Springer.pdf` |
| `--style external` | `tex/` | `<Textbook>.pdf` |
| `--section lattices` | `springer/samples/lattices/tex/` | `springer/samples/lattices/<Textbook> - Lattices - Springer.pdf` |
| `--style external --section lattices` | `samples/lattices/tex/` | `samples/lattices/<Textbook> - Lattices.pdf` |

`--section` selects the exact final slug of a post's permalink, retaining its original
chapter, section and statement numbers. It does not overwrite a full build. References
to material outside a sample cannot become links to that omitted material in the sample.

`--output` accepts a PDF filename or an existing directory; a directory keeps the distinct
style/sample filenames above. `--tex-only` stops before LaTeX, `--no-index` leaves out the
index, and `--drafts` takes posts that are not `published`.

Book editions omit the `source_note` presentation/credit paragraphs and all Exercises
sections, including their problems and solutions. The site posts retain both. The
semantic HTML is copied and filtered before reference targets, anchors and index terms
are collected; links to omitted anchors lead to the original site instead of a missing
PDF target. A standalone post titled `Exercises` is also excluded.

## How it works

1. The site is built into the cache with `tikzcd: enabled: false` laid over `_config.yml`,
   so diagrams arrive as the TikZ they were written in and LaTeX sets them itself.
2. Each post's built page is read, not its Markdown. `_plugins/document_structure.rb` has
   already shaped the page as a LaTeX document (`_docs/STRUCTURE.md`), so the book is one
   more reader of that contract, as `main.js` and `_narrator/` are, and never decides again
   where a statement or a proof ends. `latex_writer.py` writes it out:

   | page | book |
   |---|---|
   | a theorem, lemma, proposition or corollary (`math-statement-italic`) | `\begin{statement}{plain}{Theorem 3.1.8}[name]`: amsthm, italic body |
   | any other statement | `\begin{statement}{definition}{Definition 2.1.1}`: upright body |
   | `## Exercises` and its problems/solutions | omitted from the book projection |
   | `*Proof.*`, `*Subproof.*`, `*Solution.*` | `proof`, `subproof` (■), `proof` headed Solution; a period outside the marker is consumed once |
   | a QED span or `\tag*{\(\square\)}` | `\qedhere`; a proof that has none gets `\noqed` |
   | `**T.**`, `**3. T.**` (run-in headings) | `\bookruninhead{T.}`: the selected class supplies the layout |
   | other h2 headings | `\booksubsectionhead{...}` |
   | inline math with at least four commas outside brace groups | `\bookmath{...}`: Springer permits comma breaks only when the formula is wider than 35% of the local line |
   | a soft line in a paragraph of the body or of a unit | a paragraph of its own |
   | one blank line after display math; two | the same paragraph; a new one |
   | ordered lists by depth; `{:marker-prefix="L"}` | (1), (a), (i), (A); (L1) |
   | `$$\begin{align}…$$` | `align*`: MathJax numbers nothing here |
   | `Theorem 2.1.6` in prose | a link to it, by `main.js`'s rule (a bare number only when one statement has it) |
   | a diagram with a caption (`captioned-figure`) | `\begin{figure}[!htbp]` with `\figurecaption{1.1.1}{...}`: the number typed, the caption as the class sets it |
   | a footnote | `\footnote` |
   | `*term*` in a definition | `\emph` and an entry in the index |
   | `source_note` | retained by the site, omitted from the PDF |

   Heads are printed as the labels read. Numbers are read, never generated, as on the site;
   the chapter and section counters are set from the folders' and titles' numbers.
3. `book.tex` (written by the script) loads the selected design class and
   `tikz-preamble.tex`, which is `TIKZ_PREAMBLE` read out of
   `_plugins/tikzcd_renderer.rb`. latexmk runs LuaLaTeX and makeindex; the Springer
   profile selects `springer-hyperref.ist` without changing the default profile's
   index settings. This local adaptation keeps the official `svind.ist` formatting
   but separates page numbers with comma-space so hyperref can link them correctly.
   The vendor original stays unchanged. If the local style is newer than a cached
   `.ind`, the stale Springer index is regenerated on the next build.

## What it reports

- A reference whose kind is not its target's (`“Theorem 2.1.6” points at
  proposition-2-1-6`). The site leaves it unlinked, and so does the book.
- A macro of `assets/js/mathjax-config.js` that `site-macros.tex` does not define; a test
  checks this too.
- LaTeX's overfull lines. A display wider than the style's text block (30pc for `external`,
  117mm for `springer`), one the page lets scroll, needs checking in the PDF.
- Undefined references, missing glyphs and unreferenced PDF destinations, including
  malformed index page links.

## Springer default edition

`external-springer-book.cls` adapts the same generated content to Springer Nature's
`SNmono` v6.00 (11 November 2025). The source package is the monograph template linked
from the [official book manuscript guidelines](https://www.springernature.com/gp/authors/publish-a-book/manuscript-guidelines):
[monograph template ZIP](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27837776/data/v1).

The edition uses `SNmono`'s text block, heading hierarchy, running heads and theorem
presentation, with the template's `newtxtext` / `newtxmath` font combination. The approved
default paper size is 155 x 235mm with a 117 x 191mm text block. Body margins are 20mm
inner, 18mm outer, 20mm top and 24mm bottom, with running heads and folios outside the
body area. This trim is a local design choice, not a universal Springer specification.
The earlier `external` profile remains available on 7 x 10 inch paper.
The wrapper supplies the site's statement labels, proof/QED conventions, mathematics
macros, TikZ, links, title metadata and index without changing the posts' numbering.

Source subheadings are numbered subsections, reset within each section (for example,
`1.3.1 The length of a poset.`). Their titles run into the following paragraph using
SNmono's native run-in typography; a following list or statement starts on its own line.
Subsection numbers also appear in the contents and PDF outline. This numbering is
independent of the literal statement numbers.

All links use pure RGB blue `(0, 0, 1)`, including body references, footnotes, URLs,
contents titles and page numbers, and linked index page numbers. The white star is the
site's: `scripts/white_star.py` draws it once, as the site's one-glyph White Star face and as
the book's PGF drawing in `site-macros.tex` (both editions), from the same numbers, and its
`--check` (a test) fails when either is stale. The book sets it as large beside its math as
the site sets it beside MathJax's (.576em by .54em of ink, as high above the math axis),
scaled for subscripts and copied as U+2606. Missing IPA letters
in pronunciation footnotes also use a character-level New Computer Modern fallback.

List margins are computed from their labels, with a zero label indent and a half-em
gap, so prefixes such as `(L1)` stay inside the current text block. Long footnotes are
strongly discouraged from splitting (`\interfootnotelinepenalty=9000`), while a safe
fallback remains for notes too long for one page. `footmisc`'s `splitrule` makes a
continued footnote visible with a full-width continuation rule.

LuaTeX's glyph-to-Unicode mapping is enabled before loading NewTX, using the distribution's
`glyphtounicode`, `glyphtounicode-cmr` and `glyphtounicode-ntx` tables. This preserves the
existing visual math fonts while providing Unicode text for copying and searching
symbols such as the diamond, sum and QED squares. It does not encode the full semantic
structure or two-dimensional reading order of a formula.

The official template is for manuscript preparation; Springer creates the final
publication layout. This profile is therefore an independent template-based
edition. It does not imply Springer publication or reproduce the final design of a
particular series. The pipeline uses LuaLaTeX for both profiles; font and diagram
compatibility is checked by compiling the same content with the new class.

## Changing the design

For the earlier profile, `external-book.cls` holds the trim (7 × 10 in, `geometry`), the faces, the
headings (`titlesec`), the running heads (`fancyhdr`), statements and proofs (`amsthm`),
lists (`enumitem`), the title page and its verso. Change the Springer adapter separately;
loading the earlier class over `SNmono` would replace the approved design. A new
MathJax macro needs its LaTeX twin in `site-macros.tex` and compatibility with both font
sets. `_tests/test_book_latex.py` covers the conversion, unchanged numbering across styles,
and isolation of full/sample builds and output filenames. `_tests/test_book_pdf.py`
also compiles a small real PDF to check symbols, numbered headings, links, label
placement, link colors and footnote placement.
