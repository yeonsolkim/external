"""
Pins the skeleton. The skeleton is a cache-key dimension: if its output changes for
unchanged HTML, every recording downstream is regenerated (and paid for). The golden
hash below is the live "2.2. Compact Sets" page as fetched on 2026-09-15; change it only
on purpose, with a skeleton version bump.

    python3 -m unittest _narrator.tests.test_skeleton
"""
import os
import unittest

from _narrator.skeleton import build, glossary_source

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "compact-sets.html")
GOLDEN_DOC_HASH = "94b54ab26a9d29610c829187b95c2cce476babb65b95cbd0337fbcbe45eefabe"
GOLDEN_THEOREM_2_2_3 = "61386823ca3342dc22411d348ce623ca80870c5ade0c45cfb9d5f71bb8e6a919"


def wrap(body: str) -> str:
    return ('<html lang="en"><head><link rel="canonical" href="https://x.test/p.html"></head>'
            '<body><article class="post"><h1 class="post-title">T</h1>'
            '<div class="post-body">%s</div></article></body></html>' % body)


class CompactSets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, encoding="utf-8") as handle:
            cls.skel = build(handle.read(), FIXTURE)

    def test_golden(self):
        s = self.skel
        self.assertEqual(s.hash, GOLDEN_DOC_HASH)
        self.assertEqual(len(s.sections), 33)
        self.assertEqual(sum(1 for x in s.sections if not x.skip), 32)
        self.assertEqual((s.math, s.words), (351, 3726))
        self.assertEqual(s.sections[4].hash, GOLDEN_THEOREM_2_2_3)

    def test_document_fields(self):
        s = self.skel
        self.assertEqual(s.url, "/2026/07/30/2.-Compact-Sets.html")
        self.assertEqual(s.title, "2.2. Compact Sets")
        self.assertEqual((s.lang, s.scope), ("en", "introduction-to-analysis"))
        self.assertEqual((s.published, s.modified), ("2026-07-30", "2026-09-12"))

    def test_sections(self):
        ids = [x.id for x in self.skel.sections]
        self.assertEqual(ids[:5], ["introduction", "definition-2-2-1", "prose-after-definition-2-2-1",
                                   "definition-2-2-2", "theorem-2-2-3"])
        self.assertEqual(ids[-1], "references")
        self.assertEqual(self.skel.sections[-1].skip, "reference list")
        named = {x.id: x for x in self.skel.sections}
        self.assertEqual(named["theorem-2-2-20"].title, "Theorem 2.2.20 (Heine–Borel theorem)")
        self.assertEqual(named["theorem-2-2-20"].name, "Heine–Borel theorem")
        self.assertTrue(named["theorem-2-2-20"].has_proof)
        self.assertFalse(named["definition-2-2-19"].has_proof)

    def test_math_numbering_restarts_per_section(self):
        for section in self.skel.sections:
            if section.math:
                self.assertIn("[MATH 1; ", section.text)

    def test_qed_forms(self):
        named = {x.id: x for x in self.skel.sections}
        # inline <span class="qed"> at the end of a proof paragraph
        self.assertTrue(named["theorem-2-2-3"].text.rstrip().endswith("[END PROOF]") or
                        "[MATH 44; TeX] M [/MATH]. [END PROOF]" in named["theorem-2-2-3"].text)
        # \tag*{\(\square\)} inside a display equation: tag stripped, cue after the block
        text = named["corollary-2-2-12"].text
        self.assertNotIn("\\tag*", text)
        self.assertIn("\\varnothing. [/MATH] [END PROOF]", text)
        # a display tag that is a real label survives
        self.assertIn("\\tag{$\\ast$}", named["theorem-2-2-3"].text)

    def test_punctuation_leaves_the_math(self):
        named = {x.id: x for x in self.skel.sections}
        text = named["definition-2-2-1"].text
        self.assertIn("[MATH 2; TeX] A\\subseteq M [/MATH]. A collection", text)      # `\(A\subseteq M.\)`
        self.assertIn("[MATH 13; TeX] A [/MATH].", text)                               # `\(A\).`
        self.assertIn("[MATH 22; TeX] k [/MATH]-cell", named["theorem-2-2-20"].text)   # `\(k\)-cell`

    def test_list(self):
        text = {x.id: x for x in self.skel.sections}["theorem-2-2-16"].text
        self.assertIn("\n(1) [MATH 27; TeX] I\\supseteq I_1", text)
        self.assertIn("\n(3) if [MATH 30; TeX]", text)

    def test_transitional_prose_is_its_own_section(self):
        named = {x.id: x for x in self.skel.sections}
        # after a proof: everything past the QED
        self.assertTrue(named["theorem-2-2-3"].text.endswith("[END PROOF]"))
        self.assertTrue(named["prose-after-theorem-2-2-3"].text.startswith("Thus compactness is intrinsic"))
        self.assertEqual(named["prose-after-theorem-2-2-3"].kind, "prose")
        # a display equation's QED counts as the proof's end
        self.assertTrue(named["prose-after-corollary-2-2-12"].text.startswith("This result assumes"))
        # without a proof: a paragraph that finishes a display stays; a new sentence leaves
        self.assertIn("is called a finite subcover", named["definition-2-2-1"].text)
        self.assertTrue(named["prose-after-definition-2-2-1"].text.startswith("Since openness depends"))
        # lowercase continuation stays with the statement
        self.assertTrue(named["definition-2-2-19"].text.endswith("[MATH 6; TeX] x,y\\in A [/MATH]."))
        self.assertNotIn("prose-after-definition-2-2-19", named)
        self.assertEqual(sum(1 for x in self.skel.sections if x.kind == "prose"), 11)

    def test_glossary_source_excludes_skipped(self):
        self.assertNotIn("Rudin", glossary_source(self.skel))


class Synthetic(unittest.TestCase):
    def test_bare_delimiters(self):
        skel = build(wrap("<p>Let \\(x\\) and $y$ with $$a=b$$ and \\[c=d\\] and a \\$5 note.</p>"))
        text = skel.sections[0].text
        self.assertIn("[MATH 1; TeX] x [/MATH]", text)
        self.assertIn("[MATH 2; TeX] y [/MATH]", text)
        self.assertIn("[MATH 3; TeX display] a=b [/MATH]", text)
        self.assertIn("[MATH 4; TeX display] c=d [/MATH]", text)
        self.assertIn("a $5 note", text)

    def test_unnumbered_environment_and_heading(self):
        skel = build(wrap('<h2 id="intro">Intro</h2><p>Hi.</p><p><strong>Remark.</strong> One.</p>'
                          '<p><strong>Remark.</strong> Two.</p><h2 id="references">References</h2><ol><li>x</li></ol>'))
        self.assertEqual([s.id for s in skel.sections], ["intro", "remark-1", "remark-2", "references"])
        self.assertEqual(skel.sections[0].anchor, "intro")
        self.assertEqual(skel.sections[0].text, "Intro\n\nHi.")

    def test_statement_paragraph_before_proof_stays(self):
        skel = build(wrap("<p><strong>Theorem 1.</strong> A.</p><p>Here B.</p><p><em>Proof.</em> C."
                          '<span data-environment-end="proof"></span></p><p>Next.</p>'))
        self.assertEqual([s.id for s in skel.sections], ["theorem-1", "prose-after-theorem-1"])
        self.assertIn("Here B.", skel.sections[0].text)
        self.assertEqual(skel.sections[1].text, "Next.")
        self.assertEqual(skel.sections[1].title, "Next.")

    def test_bold_that_is_not_an_environment(self):
        skel = build(wrap("<p><strong>Warning</strong> this is bold prose.</p>"))
        self.assertEqual([s.id for s in skel.sections], ["introduction"])

    def test_omissions(self):
        skel = build(wrap("<table><tr><td>1</td></tr></table><pre>a\nb\nc\nd\ne</pre>"
                          '<figure><img alt="A cat"></figure><div class="footnotes"><p>fn</p></div>'))
        self.assertEqual(skel.sections[0].text, "[TABLE omitted]\n\n[CODE omitted]\n\n[FIGURE: A cat]")
        self.assertEqual(skel.warnings, ["code block omitted", "figure narrated as its caption only", "footnotes omitted", "table omitted"])

    def test_nbsp_and_nfc_are_normalised(self):
        a = build(wrap("<p>café au lait</p>")).sections[0]
        b = build(wrap("<p>café au   lait</p>")).sections[0]
        self.assertEqual(a.hash, b.hash)

    def test_not_a_post(self):
        from _narrator.skeleton import SkeletonError
        with self.assertRaises(SkeletonError):
            build("<html><body><p>hi</p></body></html>")


if __name__ == "__main__":
    unittest.main()
