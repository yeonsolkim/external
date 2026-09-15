"""Stage 2 bookkeeping — no network. `python3 -m unittest _narrator.tests.test_script`"""
import os
import tempfile
import unittest

from _narrator import script as stage2
from _narrator.prompts import PROMPT_VERSION
from _narrator.skeleton import build

HTML = ('<html lang="en"><head><link rel="canonical" href="https://x.test/2026/01/02/p.html"></head>'
        '<body><article class="post"><h1 class="post-title">P</h1><div class="post-body">'
        '<p>Intro \\(x\\).</p><p><strong>Theorem 1.</strong> Let \\(y\\).</p>'
        '<h2 id="references">References</h2><ol><li>r</li></ol></div></article></body></html>')


def skel(html=HTML):
    return build(html, "p.html")


class Files(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.md")
            stage2.write_md(path, {"section": "a", "title": "Theorem 1 (Heine–Borel): x", "n": 3}, "Body.\n\nMore.")
            meta, body = stage2.read_md(path)
            self.assertEqual(meta["section"], "a")
            self.assertEqual(meta["title"], "Theorem 1 (Heine–Borel): x")
            self.assertEqual(meta["n"], "3")
            self.assertEqual(body, "Body.\n\nMore.\n")

    def test_body_hash_ignores_trailing_whitespace(self):
        self.assertEqual(stage2._sha("A.\n\nB.  \n"), stage2._sha("\nA.\n\nB."))

    def test_post_dir(self):
        self.assertEqual(stage2.post_dir("_narration", skel()), os.path.join("_narration", "2026", "01", "02", "p"))


class Planning(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = self.tmp.name
        self.skel = skel()

    def tearDown(self):
        self.tmp.cleanup()

    def seed(self, section, body="Script.", **over):
        meta = {"section": section.id, "source": section.hash, "prompt": PROMPT_VERSION, "body": stage2._sha(body)}
        meta.update(over)
        stage2.write_md(os.path.join(self.out, section.id + ".md"), meta, body)

    def ids(self, items):
        return [s.id for s, _ in items]

    def test_fresh(self):
        p = stage2.plan(self.skel, self.out)
        self.assertEqual(p.glossary, "new")
        self.assertEqual(self.ids(p.generate), ["introduction", "theorem-1"])
        self.assertEqual([s.id for s, r in p.skipped], ["references"])

    def test_current(self):
        for s in self.skel.sections[:2]:
            self.seed(s)
        stage2.write_md(os.path.join(self.out, "glossary.md"),
                        {"source": stage2.glossary_key(self.skel), "body": stage2._sha("g")}, "g")
        p = stage2.plan(self.skel, self.out)
        self.assertIsNone(p.glossary)
        self.assertEqual(p.generate, [])
        self.assertEqual([s.id for s in p.current], ["introduction", "theorem-1"])

    def test_source_changed(self):
        intro, thm = self.skel.sections[:2]
        self.seed(intro, source="0" * 64)                          # untouched -> regenerate
        self.seed(thm, source="0" * 64, body="My own words.")     # hand-edited -> protect
        stage2.write_md(os.path.join(self.out, thm.id + ".md"),
                        {"section": thm.id, "source": "0" * 64, "prompt": PROMPT_VERSION,
                         "body": stage2._sha("Script.")}, "My own words.")
        p = stage2.plan(self.skel, self.out)
        self.assertEqual(self.ids(p.generate), ["introduction"])
        self.assertEqual([s.id for s, _ in p.stale], ["theorem-1"])

    def test_prompt_bump(self):
        intro, thm = self.skel.sections[:2]
        self.seed(intro, prompt="old")
        stage2.write_md(os.path.join(self.out, thm.id + ".md"),
                        {"section": thm.id, "source": thm.hash, "prompt": "old",
                         "body": stage2._sha("Script.")}, "Edited by hand.")
        p = stage2.plan(self.skel, self.out)
        self.assertEqual(self.ids(p.generate), ["introduction"])   # unedited: new prompt wins
        self.assertEqual([s.id for s in p.current], ["theorem-1"])  # edited: your words win

    def test_force_keeps_edits(self):
        intro, thm = self.skel.sections[:2]
        self.seed(intro)
        stage2.write_md(os.path.join(self.out, thm.id + ".md"),
                        {"section": thm.id, "source": thm.hash, "prompt": PROMPT_VERSION,
                         "body": stage2._sha("Script.")}, "Edited by hand.")
        p = stage2.plan(self.skel, self.out, force=True)
        self.assertEqual(self.ids(p.generate), ["introduction"])
        self.assertEqual([s.id for s, _ in p.stale], ["theorem-1"])

    def test_only(self):
        p = stage2.plan(self.skel, self.out, only={"theorem-1"})
        self.assertEqual(self.ids(p.generate), ["theorem-1"])

    def test_accept_makes_an_edited_script_current(self):
        thm = self.skel.sections[1]
        stage2.write_md(os.path.join(self.out, thm.id + ".md"),
                        {"section": thm.id, "source": "0" * 64, "prompt": PROMPT_VERSION,
                         "body": stage2._sha("Script."), "stale": "true"}, "My own words.")
        stage2.write_md(os.path.join(self.out, thm.id + ".new.md"), {"source": thm.hash}, "Draft.")
        self.assertEqual([s.id for s, _ in stage2.plan(self.skel, self.out).stale], [thm.id])
        n = stage2.accept(self.skel, self.out, {thm.id}, log=lambda m: None)
        self.assertEqual(n, 1)
        meta, body = stage2.read_md(os.path.join(self.out, thm.id + ".md"))
        self.assertEqual(meta["source"], thm.hash)
        self.assertNotIn("stale", meta)
        self.assertEqual(body, "My own words.\n")
        self.assertFalse(os.path.exists(os.path.join(self.out, thm.id + ".new.md")))
        p = stage2.plan(self.skel, self.out)
        self.assertEqual([s.id for s in p.current], [thm.id])      # current, and still yours
        self.assertEqual(p.stale, [])

    def test_glossary_key_ignores_prose(self):
        a = stage2.glossary_key(skel())
        b = stage2.glossary_key(skel(HTML.replace("Intro", "Changed intro")))
        c = stage2.glossary_key(skel(HTML.replace("\\(y\\)", "\\(z\\)")))
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


if __name__ == "__main__":
    unittest.main()
