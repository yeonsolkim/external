"""
Tests for scripts/book: a built post (the HTML _docs/STRUCTURE.md describes) -> LaTeX.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import contextlib
import copy
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "book"))

import build_book  # noqa: E402
from _narrator.htmltree import parse_html  # noqa: E402
from latex_writer import PostWriter, reference_targets  # noqa: E402


def body_of(html):
    root = parse_html('<div class="post-body">%s</div>' % html)
    return root.find(lambda n: n.tag == "div" and n.has_class("post-body"))


def convert(html, targets=None, **options):
    writer = PostWriter("post", targets or {}, lambda href: None, **options)
    return writer.write(body_of(html)), writer.warnings


def statement(kind, number, inner, italic=False):
    anchor = "%s-%s" % (kind.lower(), number.replace(".", "-"))
    return (
        '<section class="semantic-unit math-environment math-environment--%s%s" data-doc="%s" '
        'data-environment-kind="%s" data-number="%s" id="unit-%s">\n'
        '<p><strong id="%s" class="math-label-anchor">%s %s.</strong> %s\n</section>\n'
        % (kind.lower(), " math-statement-italic" if italic else "", kind.lower(), kind, number,
           anchor, anchor, kind, number, inner))


QED = '<span data-environment-end="proof" class="qed"><span class="math-inline">\\(\\square\\)</span></span>'
FIGURE = (
    '<figure class="captioned-figure" data-number="1.1.1" id="unit-figure-1-1-1">\n%s\n'
    '<figcaption><strong id="figure-1-1-1" class="figure-label">Figure 1.1.1.</strong> '
    'A basis at <span class="math-inline">\\(x\\)</span></figcaption>\n</figure>')


class StatementTests(unittest.TestCase):
    def test_head_is_the_label_and_the_name_its_note(self):
        latex, _ = convert(
            '<section class="semantic-unit math-environment math-environment--theorem '
            'math-statement-italic" data-doc="theorem" data-environment-kind="Theorem" '
            'data-number="4.2.4" data-name="Rank–nullity theorem" id="unit-theorem-4-2-4">\n'
            '<p><strong id="theorem-4-2-4" class="math-label-anchor">Theorem 4.2.4 '
            '<span class="math-statement-name">(Rank–nullity theorem)</span>.</strong> Let '
            '<span class="math-inline">\\(V\\)</span> be finite-dimensional.</p>\n</section>')
        self.assertEqual(
            latex,
            "\\begin{statement}{plain}{Theorem 4.2.4}[{Rank–nullity theorem}]"
            "\\unitlabel{post:theorem-4-2-4}\nLet $V$ be finite-dimensional.\n\\end{statement}")

    def test_a_definition_is_upright_and_indexes_its_terms(self):
        latex, _ = convert(statement("Definition", "2.1.1", "A <em>vector space</em> is a set.</p>"))
        self.assertIn("\\begin{statement}{definition}{Definition 2.1.1}", latex)
        self.assertIn("\\emph{vector space}\\index{vector space}", latex)
        latex, _ = convert(statement("Definition", "3.2.4", "A <em>Galois connection</em>.</p>"))
        self.assertIn("\\emph{Galois connection}\\index{galois connection@Galois connection}", latex)
        latex, _ = convert(statement("Definition", "2.1.1", "A <em>vector space</em>.</p>"),
                           index_terms=False)
        self.assertNotIn("\\index", latex)

    def test_a_bare_label_keeps_a_line_of_its_own_above_a_list(self):
        latex, _ = convert(statement("Definition", "1.1.1", "</p>\n<ol>\n<li>one</li>\n</ol>"))
        self.assertIn("\\unitlabel{post:definition-1-1-1}\\leavevmode\n\\begin{enumerate}", latex)


class ProofTests(unittest.TestCase):
    def test_marker_period_outside_emphasis_is_consumed_without_changing_the_source(self):
        for kind, begin in (("Proof", "\\begin{proof}"), ("Subproof", "\\begin{subproof}"),
                            ("Solution", "\\begin{proof}[Solution]")):
            with self.subTest(kind=kind):
                body = body_of(
                    '<section class="semantic-unit math-environment" data-doc="proof" '
                    'data-environment-kind="%s"><p><em class="math-proof-marker">%s</em>. '
                    'Suppose that <span class="math-inline">\\(W\\)</span> is a subspace.%s'
                    '</p></section>' % (kind, kind, QED))
                original = [(id(node), node.text, tuple(map(id, node.children)), id(node.parent))
                            for node in body.iter()]
                for _ in range(2):
                    writer = PostWriter("post", {}, lambda href: None)
                    self.assertEqual(writer.write(body),
                                     begin + "\nSuppose that $W$ is a subspace.\\qedhere\n"
                                     + "\\end{%s}" % ("subproof" if kind == "Subproof" else "proof"))
                self.assertEqual(
                    [(id(node), node.text, tuple(map(id, node.children)), id(node.parent))
                     for node in body.iter()], original)

    def test_only_one_period_after_a_proof_marker_is_consumed(self):
        latex, _ = convert(
            '<section class="semantic-unit math-environment" data-doc="proof" '
            'data-environment-kind="Proof"><p><em class="math-proof-marker">Proof</em>.. '
            'Start.%s</p></section>' % QED)
        self.assertIn("\\begin{proof}\n. Start.\\qedhere", latex)

    def test_qed_marks_become_qedhere_and_a_subproof_keeps_its_black_square(self):
        latex, _ = convert(
            '<section class="semantic-unit math-environment math-environment--proof" data-doc="proof" '
            'data-environment-kind="Proof" id="unit-proof-exercise-1">\n'
            '<p><em id="proof-exercise-1" class="math-proof-marker">Proof.</em> Start.</p>\n'
            '<section class="semantic-unit math-environment math-environment--subproof" data-doc="proof" '
            'data-environment-kind="Subproof" id="unit-proof-math-lemma-2">\n'
            '<p><em class="math-proof-marker">Subproof.</em> Inner.<span data-environment-end="subproof" '
            'class="qed"><span class="math-inline">\\(\\blacksquare\\)</span></span></p>\n</section>\n'
            '<p>End.%s</p>\n</section>' % QED)
        self.assertEqual(
            latex,
            "\\begin{proof}\nStart.\n\n\\begin{subproof}\nInner.\\qedhere\n\\end{subproof}\n\n"
            "End.\\qedhere\n\\end{proof}")

    def test_a_proof_the_page_ends_without_a_qed_has_none(self):
        latex, warnings = convert(
            '<section class="semantic-unit math-environment math-environment--proof" data-doc="proof" '
            'data-environment-kind="Proof" data-proves="exercise-1" id="unit-proof-1">\n'
            '<p><em class="math-proof-marker">Proof 2.</em> Unfinished.</p>\n</section>')
        self.assertTrue(latex.startswith("\\begin{proof}[Proof 2]\\noqed\n"))
        self.assertEqual(warnings, ["the proof 2 of exercise-1 ends without a QED mark"])

    def test_a_tagged_qed_ends_an_unnumbered_align(self):
        latex, _ = convert(
            '<section class="semantic-unit math-environment math-environment--proof" data-doc="proof" '
            'data-environment-kind="Proof" id="unit-proof-1">\n'
            '<p><em class="math-proof-marker">Proof.</em> Hence</p>\n\n'
            '\\[\\begin{align}\na&amp;=b\\\\\n&amp;=c.\\tag*{\\(\\square\\)}\n\\end{align}\\]\n\n'
            '<div class="math-environment-end" data-environment-end="proof" aria-hidden="true"></div>\n'
            '</section>')
        self.assertIn("Hence\n\\begin{align*}\na&=b\\\\\n&=c.\\qedhere\n\\end{align*}\n\\end{proof}", latex)


class ParagraphTests(unittest.TestCase):
    def test_source_run_in_headings_use_the_design_interface_and_keep_their_anchor(self):
        latex, _ = convert(
            '<section class="doc-section doc-section--run-in" data-doc="section">'
            '<p><strong class="doc-heading" id="span-as-closure">Span as a closure operator.</strong> '
            'A function maps inputs to outputs.</p></section>')
        self.assertEqual(
            latex, "\\bookruninhead{Span as a closure operator.}\\unitlabel{post:span-as-closure}\n"
            "A function maps inputs to outputs.")

    def test_h2_uses_the_subsection_interface_before_an_exercise_list(self):
        latex, _ = convert('<section class="doc-section doc-section--heading" data-doc="subsection">'
                           '<h2 id="exercises">Exercises</h2><ol><li>Prove it.</li></ol></section>')
        self.assertEqual(
            latex, "\\booksubsectionhead{Exercises}\\unitlabel{post:exercises}\n\n"
            "\\begin{enumerate}\n\\item Prove it.\n\\end{enumerate}")

    def test_display_math_continues_its_paragraph_unless_two_blank_lines_followed(self):
        latex, _ = convert(statement(
            "Definition", "1.1.1",
            "Let</p>\n\n\\[x=y\\]\n\n<p>hold.</p>\n\n\\[z\\]\n\n"
            '<div class="post-structural-continuation" aria-hidden="true"></div>\n\n'
            '<p data-paragraph-continuation="structural">New.</p>'))
        self.assertIn("Let\n\\[\nx=y\n\\]\nhold.\n\\[\nz\n\\]\n\nNew.\n\\end{statement}", latex)

    def test_a_soft_line_is_a_paragraph_in_the_body_not_in_a_list_item(self):
        latex, _ = convert("<p>One\nTwo</p>\n<ol>\n<li>Three\nfour</li>\n</ol>")
        self.assertEqual(latex, "One\n\nTwo\n\\begin{enumerate}\n\\item Three four\n\\end{enumerate}")

    def test_list_labels_take_their_prefix(self):
        latex, _ = convert('<ol marker-prefix="L">\n<li>first</li>\n</ol>')
        self.assertTrue(latex.startswith("\\begin{enumerate}[label={(L\\arabic*)}]"))

    def test_footnotes_go_to_their_reference_without_the_back_link(self):
        latex, _ = convert(
            '<p>Text.<sup id="fnref:1"><a href="#fn:1" class="footnote" rel="footnote" '
            'role="doc-noteref">1</a></sup></p>\n<div class="footnotes" role="doc-endnotes"><ol>'
            '<li id="fn:1"><p>Note <em>here</em>. <a href="#fnref:1" class="reversefootnote" '
            'role="doc-backlink">&#8617;</a></p></li></ol></div>')
        self.assertEqual(latex, "Text.\\footnote{Note \\emph{here}.}")

    def test_text_is_escaped_and_punctuation_stays_outside_the_formula(self):
        latex, _ = convert('<p>50% of $5 &amp; #1_a ~ {b}: '
                           '<span class="math-inline math-inline-punctuated">\\(F\\to V\\),</span></p>')
        self.assertEqual(latex, "50\\% of \\$5 \\& \\#1\\_a \\textasciitilde{} \\{b\\}: $F\\to V$,")


class InlineMathTests(unittest.TestCase):
    def test_only_long_tuple_candidates_use_the_measured_math_interface(self):
        for tex, candidate in (
            (r"C(\mathbb R,\mathbb R)", False),
            (r"(a,b,c,d)", False),
            (r"(a,b,c,d,e)", True),
            (r"\{a,b,c,d,e\}", True),
            (r"{a,b,c,d,e}", False),
            (r"\text{a,b,c,d,e}", False),
            (r"(\text{a,b},c,d,e)", False),
            (r"(\text{a,b},c,d,e,f)", True),
            (r"(a\,b,c,d,e)", False),
            (r"(a\,b,c,d,e,f)", True),
            (r"\text{a\{b,c,d,e,f\}g}", False),
            (r"\{a,b,c,{d,e,f}\}", False),
            (r"(a,b,c,d,\{e,f\})", True),
        ):
            with self.subTest(tex=tex):
                expected = "\\bookmath{%s}" % tex if candidate else "$%s$" % tex
                self.assertEqual(PostWriter.math(tex), expected)

    def test_long_math_keeps_punctuation_outside_and_display_math_unchanged(self):
        tex = r"(a,b,c,d,e)"
        latex, _ = convert('<p><span class="math-inline math-inline-punctuated">\\(%s\\),'
                           '</span></p>\\[%s\\]' % (tex, tex))
        self.assertEqual(latex, "\\bookmath{%s},\n\\[\n%s\n\\]" % (tex, tex))


class ReferenceTests(unittest.TestCase):
    def test_references_link_as_main_js_links_them(self):
        labels = body_of(statement("Theorem", "2.1.6", "A.</p>", italic=True)
                         + statement("Proposition", "2.1.7", "B.</p>", italic=True))
        targets = reference_targets([("post", labels)])
        latex, warnings = convert("<p>By Theorem 2.1.6 and 2.1.7; see Theorem 2.1.7.</p>", targets)
        self.assertEqual(
            latex,
            "By Theorem~\\hyperref[post:theorem-2-1-6]{2.1.6} and "
            "\\hyperref[post:proposition-2-1-7]{2.1.7}; see Theorem 2.1.7.")
        self.assertEqual(warnings, ["“Theorem 2.1.7” points at proposition-2-1-7"])

    def test_a_number_two_statements_share_links_nowhere(self):
        labels = [("a", body_of(statement("Theorem", "1.1.1", "A.</p>"))),
                  ("b", body_of(statement("Lemma", "1.1.1", "B.</p>")))]
        targets = reference_targets(labels)
        self.assertIsNone(targets["1.1.1"])
        self.assertEqual(targets["Lemma 1.1.1"], "b:lemma-1-1-1")

    def test_a_figure_is_referred_to_by_its_kind_only(self):
        targets = reference_targets([("post", body_of(
            statement("Definition", "1.1.1", "A.</p>") + FIGURE % "\\[\\begin{tikzcd}A\\end{tikzcd}\\]"))])
        latex, warnings = convert("<p>See Figure 1.1.1 and 1.1.1.</p>", targets)
        self.assertEqual(
            latex,
            "See Figure~\\hyperref[post:figure-1-1-1]{1.1.1} and \\hyperref[post:definition-1-1-1]{1.1.1}.")
        self.assertEqual(warnings, [])


class FigureTests(unittest.TestCase):
    def test_a_captioned_diagram_is_a_float_numbered_as_its_label_reads(self):
        latex, warnings = convert(
            "<p>Before.</p>\n"
            + FIGURE % ("\\[\\begin{tikzpicture}\n  \\node (a) {$x$\\\\[1pt] b};\n"
                        "  \\draw[-&gt;] (a) -- (1,0);\n\\end{tikzpicture}\\]")
            + "\n<p>After.</p>")
        self.assertEqual(
            latex,
            "Before.\n\n\\begin{figure}[!htbp]\\unitlabel{post:figure-1-1-1}\n\\centering\n"
            "\\begin{tikzpicture}\n  \\node (a) {$x$\\\\[1pt] b};\n  \\draw[->] (a) -- (1,0);\n"
            "\\end{tikzpicture}\n\\figurecaption{1.1.1}{A basis at $x$}\n\\end{figure}\n\nAfter.")
        self.assertEqual(warnings, [])

    def test_diagrams_among_other_math_stay_one_formula(self):
        formula = "\\begin{tikzcd}A\\end{tikzcd}\n\\quad\n\\begin{tikzcd}B\\end{tikzcd}"
        latex, _ = convert(FIGURE % ("\\[%s\\]" % formula))
        self.assertIn("\\centering\n$\\displaystyle\n%s\n$\n\\figurecaption{1.1.1}" % formula, latex)

    def test_a_diagram_that_arrives_as_svg_is_reported(self):
        _, warnings = convert(FIGURE % '<div class="commutative-diagram"><svg></svg></div>')
        self.assertEqual(len(warnings), 1)
        self.assertIn("a diagram arrived as SVG", warnings[0])

    def test_every_design_sets_the_caption(self):
        for name in build_book.BOOK_STYLES.values():
            with self.subTest(name=name):
                source = (ROOT / "scripts" / "book" / (name + ".cls")).read_text(encoding="utf-8")
                self.assertIn("\\newcommand\\figurecaption[2]", source)


class BuildTests(unittest.TestCase):
    def test_book_projection_omits_exercise_sections_without_mutating_the_site_tree(self):
        source = body_of(
            '<p>Retained introduction.</p>'
            '<section class="doc-section doc-section--heading" data-title="Exercises">'
            '<h2 id="exercises">Exercises</h2><p>Omitted solutions.</p>'
            + statement("Exercise", "1.3.99", "Omitted problem.</p>") + '</section>'
            + statement("Exercise", "1.3.100", "Standalone problem.</p>")
            + '<section class="doc-section doc-section--heading" data-title="Further results">'
              '<h2 id="further">Further results</h2><p>Retained conclusion.</p></section>')
        before = [(id(n), dict(n.attrs), n.text, tuple(map(id, n.children))) for n in source.iter()]
        projected = build_book.book_body(source)
        text = projected.text_content()
        self.assertIn("Retained introduction.", text)
        self.assertIn("Retained conclusion.", text)
        self.assertNotIn("Exercises", text)
        self.assertNotIn("Omitted", text)
        self.assertNotIn("Standalone", text)
        self.assertEqual(before, [(id(n), dict(n.attrs), n.text, tuple(map(id, n.children)))
                                  for n in source.iter()])
        self.assertTrue(all(child.parent is node for node in projected.iter() for child in node.children))

    def test_order_numbers_read_as_the_site_reads_them(self):
        self.assertEqual(build_book.order_number("2. Vector Spaces"), (2, "Vector Spaces"))
        self.assertEqual(build_book.order_number("III. Topology"), (3, "Topology"))
        self.assertEqual(build_book.order_number("Exercises"), (None, "Exercises"))

    def test_source_notes_keep_their_emphasis(self):
        self.assertEqual(
            build_book.tex_markdown("Friedberg, *Linear Algebra*, 5th ed. (2025) & more"),
            "Friedberg, \\emph{Linear Algebra}, 5th ed. (2025) \\& more")

    def test_the_hasse_style_comes_from_the_renderer(self):
        self.assertIn("hasse/.style", build_book.tikz_preamble())

    def test_every_mathjax_macro_has_a_latex_definition(self):
        self.assertEqual(build_book.unmatched_mathjax_macros(), [])


class BookStyleTests(unittest.TestCase):
    config = {"title": "External", "author": "Yeonsol Kim", "url": "https://example.test"}

    def test_all_book_styles_omit_exercises_and_source_notes_before_resolving_links(self):
        post = self.posts()[0]
        post.source_note = "The presentation in this section draws in part on Friedberg."
        post.body = body_of(
            statement("Definition", "1.3.1", "A <em>retained term</em>.</p>")
            + '<p>Read <a href="/linear-algebra/lattices/#exercise-1">the omitted problem</a>.</p>'
              '<section class="doc-section doc-section--heading" data-title="Exercises">'
              '<h2 id="exercises">Exercises</h2>'
              '<section class="math-environment math-environment--exercise" data-doc="exercise">'
              '<p><strong class="math-label-anchor" id="exercise-1">Exercise 1.3.99.</strong> '
              'An <em>omitted term</em>.</p></section>'
              '<section data-doc="proof" data-environment-kind="Proof"><p>'
              '<em class="math-proof-marker">Proof.</em> Omitted incomplete proof.</p></section></section>')
        post.anchors = build_book.anchors_of(post.body)
        exercise_post = build_book.replace(post, title="Exercises", key="exercise-post", number=None)
        with tempfile.TemporaryDirectory() as temporary:
            for style in ("external", "springer"):
                directory = Path(temporary) / style
                warnings = build_book.write_book([post, exercise_post], directory, "Linear Algebra",
                                                 self.config, index=True, style=style)
                files = list((directory / "sections").glob("*.tex"))
                self.assertEqual(len(files), 1)
                latex = files[0].read_text()
                self.assertNotIn("Exercises", latex)
                self.assertNotIn("omitted term", latex)
                self.assertNotIn("Omitted incomplete proof", latex)
                self.assertNotIn("presentation in this section", latex)
                self.assertNotIn("\\sourcenote", latex)
                self.assertIn("\\index{retained term}", latex)
                self.assertIn("\\href{https://example.test/linear-algebra/lattices/\\#exercise-1}", latex)
                self.assertNotIn("\\hyperref[lattices:exercise-1]", latex)
                self.assertEqual(warnings, {})
        self.assertIn("Omitted incomplete proof", post.body.text_content())

    def posts(self):
        return [build_book.Post(
            path=ROOT / "_posts" / (key + ".md"), chapter_number=chapter,
            chapter_title=chapter_title, number=number, title=title,
            url="/linear-algebra/%s/" % key, published=True, date="2026-11-04",
            key=key, body=body_of(statement("Theorem", label, "Let $V$ be finite.</p>", italic=True)
                                   + "<p>By Theorem %s.</p>" % label))
            for chapter, chapter_title, number, title, key, label in [
                (1, "Preliminaries", 3, "Lattices", "lattices", "1.3.11"),
                (3, "Dimension", 2, "The Dimension Function", "the-rank-function", "3.2.5"),
            ]]

    def run_cli(self, cache, *arguments):
        posts = self.posts()
        bodies = {post.url: post.body for post in posts}

        def fake_typeset(tex_dir, jobname, style="external"):
            pdf = tex_dir / (jobname + ".pdf")
            pdf.write_bytes(style.encode())
            return pdf

        with mock.patch.object(sys, "argv", ["build_book.py", *arguments]), \
                mock.patch.object(build_book, "CACHE", cache), \
                mock.patch.object(build_book, "find_textbook", return_value=ROOT / "_posts" / "2. Linear Algebra"), \
                mock.patch.object(build_book, "read_posts", side_effect=lambda _: copy.deepcopy(posts)), \
                mock.patch.object(build_book, "build_site", return_value=cache / "site") as site_build, \
                mock.patch.object(build_book, "post_body", side_effect=lambda _, post: bodies[post.url]), \
                mock.patch.object(build_book, "site_config", return_value=self.config), \
                mock.patch.object(build_book, "typeset", side_effect=fake_typeset), \
                contextlib.redirect_stdout(io.StringIO()):
            result = build_book.main()
        return result, site_build

    def test_styles_change_the_class_without_changing_numbered_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            roots = {style: Path(temporary) / style for style in ("default", "external", "springer")}
            for style, root in roots.items():
                arguments = {} if style == "default" else {"style": style}
                warnings = build_book.write_book(self.posts(), root, "Linear Algebra", self.config,
                                                 index=True, **arguments)
                self.assertEqual(warnings, {})
                master = (root / "book.tex").read_text()
                expected_class = "external-book" if style == "external" else "external-springer-book"
                self.assertIn("\\documentclass{%s}" % expected_class, master)
                self.assertIn("\\setcounter{chapter}{2}\n\\chapter{Dimension}", master)
                section = root / "sections" / "03-02-the-rank-function.tex"
                self.assertIn("\\setcounter{section}{1}\n\\section{The Dimension Function}", section.read_text())
                self.assertIn("{Theorem 3.2.5}", section.read_text())
                self.assertIn("\\hyperref[the-rank-function:theorem-3-2-5]{3.2.5}", section.read_text())
            for name in (roots["default"] / "sections").iterdir():
                self.assertEqual(name.read_bytes(), (roots["external"] / "sections" / name.name).read_bytes())
                self.assertEqual(name.read_bytes(), (roots["springer"] / "sections" / name.name).read_bytes())

    def test_sample_and_springer_builds_leave_full_default_sources_intact(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary)
            self.run_cli(cache, "--style", "external", "--tex-only")
            original = cache / "linear-algebra" / "tex"
            original_master = (original / "book.tex").read_bytes()
            original_sections = {p.name: p.read_bytes() for p in (original / "sections").iterdir()}
            self.run_cli(cache, "--style", "springer", "--tex-only")
            self.run_cli(cache, "--style", "external", "--section", "lattices", "--tex-only")
            self.run_cli(cache, "--section", "lattices", "--tex-only")
            self.run_cli(cache, "--style", "springer", "--section", "lattices", "--tex-only")
            self.assertEqual((original / "book.tex").read_bytes(), original_master)
            self.assertEqual({p.name: p.read_bytes() for p in (original / "sections").iterdir()}, original_sections)
            for style_root in (cache / "linear-algebra", cache / "linear-algebra" / "springer"):
                self.assertTrue((style_root / "tex" / "sections" / "03-02-the-rank-function.tex").is_file())
                sample = style_root / "samples" / "lattices" / "tex"
                self.assertEqual([p.name for p in (sample / "sections").iterdir()], ["01-03-lattices.tex"])
                self.assertIn("\\setcounter{section}{2}", (sample / "sections" / "01-03-lattices.tex").read_text())

    def test_output_directory_keeps_both_full_and_sample_style_pdfs(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary) / "cache"
            output = Path(temporary) / "output"
            output.mkdir()
            for arguments in ((), ("--style", "external"), ("--section", "lattices"),
                              ("--style", "external", "--section", "lattices")):
                self.run_cli(cache, *arguments, "--output", str(output))
            self.assertEqual({p.name for p in output.iterdir()}, {
                "Linear Algebra.pdf", "Linear Algebra - Springer.pdf",
                "Linear Algebra - Lattices.pdf", "Linear Algebra - Lattices - Springer.pdf"})
            for pdf in output.iterdir():
                self.assertEqual(pdf.read_bytes(), b"springer" if "Springer" in pdf.name else b"external")

    def test_springer_uses_its_index_style_without_losing_existing_search_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            for style in ("external", "springer"):
                with self.subTest(style=style), \
                        mock.patch.object(build_book, "tool_env", return_value={
                            "TEXINPUTS": "/custom/tex:", "INDEXSTYLE": "/custom/index"}), \
                        mock.patch.object(build_book.subprocess, "run", return_value=mock.Mock(returncode=0)) as run, \
                        contextlib.redirect_stdout(io.StringIO()):
                    tex_dir = Path(temporary)
                    self.assertEqual(build_book.typeset(tex_dir, "sample", style=style), tex_dir / "sample.pdf")
                    command = run.call_args.args[0]
                    environment = run.call_args.kwargs["env"]
                    self.assertEqual(run.call_args.kwargs["cwd"], tex_dir)
                    self.assertIn("/custom/tex:", environment["TEXINPUTS"])
                    if style == "springer":
                        self.assertIn("-e", command)
                        self.assertIn("makeindex -s springer-hyperref.ist", command[command.index("-e") + 1])
                        self.assertEqual(environment["INDEXSTYLE"].split(":")[-2:], ["/custom/index", ""])
                        self.assertEqual(environment["INDEXSTYLE"].split(":")[0], str(build_book.BOOK_DIR))
                        self.assertIn(str(build_book.BOOK_DIR / "vendor" / "springer"),
                                      environment["INDEXSTYLE"].split(":"))
                    else:
                        self.assertNotIn("-e", command)
                        self.assertEqual(environment["INDEXSTYLE"], "/custom/index")

    def test_changed_springer_index_style_invalidates_only_its_stale_index(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            book_dir = root / "book"
            book_dir.mkdir()
            index_style = book_dir / "springer-hyperref.ist"
            index_style.write_text('delim_n ", "\n')
            os.utime(index_style, ns=(2_000_000_000, 2_000_000_000))
            tex_dir = root / "tex"
            tex_dir.mkdir()
            index = tex_dir / "sample.ind"
            for style, modified, retained in (("springer", 1_000_000_000, False),
                                               ("springer", 3_000_000_000, True),
                                               ("external", 1_000_000_000, True)):
                with self.subTest(style=style, index_mtime=modified):
                    index.write_text("previous index\n")
                    os.utime(index, ns=(modified, modified))

                    def check_index_at_latexmk_start(*args, **kwargs):
                        self.assertEqual(index.exists(), retained)
                        return mock.Mock(returncode=0)

                    with mock.patch.object(build_book, "BOOK_DIR", book_dir), \
                            mock.patch.object(build_book.subprocess, "run", side_effect=check_index_at_latexmk_start), \
                            contextlib.redirect_stdout(io.StringIO()):
                        build_book.typeset(tex_dir, "sample", style=style)

    def test_unknown_sample_fails_before_building_the_site(self):
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(sys, "argv", ["build_book.py", "--section", "missing-section", "--tex-only"]), \
                    mock.patch.object(build_book, "CACHE", Path(temporary)), \
                    mock.patch.object(build_book, "find_textbook", return_value=ROOT / "_posts" / "2. Linear Algebra"), \
                    mock.patch.object(build_book, "read_posts", return_value=self.posts()), \
                    mock.patch.object(build_book, "build_site") as site_build:
                with self.assertRaises(SystemExit):
                    build_book.main()
                site_build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
