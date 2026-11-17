"""Stage 2 bookkeeping — no network. `python3 -m unittest _narrator.tests.test_script`"""
import os
import tempfile
import unittest
from unittest import mock

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

    def test_a_regenerated_script_keeps_its_take(self):
        # voice.Script: `--force` may write the very same text again, and take 1 of it was rejected.
        thm = self.skel.sections[1]
        self.seed(thm, take="2")
        with mock.patch.object(stage2.llm, "chat", lambda *args, **kw: "Script."):
            stage2.run(self.skel, self.out, force=True, only={thm.id}, workers=1, log=lambda m: None)
        meta, body = stage2.read_md(os.path.join(self.out, thm.id + ".md"))
        self.assertEqual((body, meta.get("take")), ("Script.\n", "2"))

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


class Phrasing(unittest.TestCase):
    """The comma pass: commas in, nothing else, and the bookkeeping that keeps CI from regenerating."""
    OLD = "Since A is contained in N, star implies A is contained in the union from k equals one to n of U k."
    NEW = "Since A is contained in N, star implies, A is contained in the union, from k equals one to n, of U k."

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = self.tmp.name
        self.skel = skel()
        self.intro, self.thm = self.skel.sections[:2]

    def tearDown(self):
        self.tmp.cleanup()

    def seed(self, section, body, generated=None, **over):
        meta = {"section": section.id, "source": section.hash, "prompt": "lecture-v4",
                "body": stage2._sha(generated if generated is not None else body)}
        meta.update(over)
        stage2.write_md(os.path.join(self.out, section.id + ".md"), meta, body)

    def run_pass(self, reply, **kw):
        calls = []

        def chat(system, user, **_):
            calls.append(user)
            return reply(user) if callable(reply) else reply
        with mock.patch.object(stage2.llm, "chat", chat):
            counts = stage2.phrase(self.skel, self.out, log=lambda m: None, **kw)
        return counts, calls

    def test_commas_only(self):
        self.assertTrue(stage2.commas_only(self.OLD, self.NEW))
        self.assertTrue(stage2.commas_only("A.\n\nB, c.", "\nA.\n\nB, c.  \n"))   # blank ends, trailing spaces
        self.assertFalse(stage2.commas_only(self.OLD, self.NEW.replace("star implies", "star gives")))
        self.assertFalse(stage2.commas_only("A, b.", "A b."))                     # a comma removed
        self.assertFalse(stage2.commas_only("A.\n\nB.", "A. B."))                 # a paragraph joined
        self.assertFalse(stage2.commas_only("A b.", "A b,."))                     # a stray comma
        self.assertFalse(stage2.commas_only("A b.", "A, b; c."))

    def test_phrases_an_untouched_script_and_makes_it_current(self):
        self.seed(self.thm, self.OLD)
        counts, calls = self.run_pass(self.NEW)
        self.assertEqual(counts["phrased"], 1)
        meta, body = stage2.read_md(os.path.join(self.out, self.thm.id + ".md"))
        self.assertEqual(body, self.NEW + "\n")
        self.assertEqual(meta["prompt"], PROMPT_VERSION)
        self.assertEqual(meta["body"], stage2._sha(self.NEW))                # not "edited by hand"
        self.assertIn("phrased", meta)
        self.assertIn(self.thm.id, [s.id for s in stage2.plan(self.skel, self.out).current])
        self.assertTrue(os.path.exists(os.path.join(self.out, "index.json")))

    def test_rewording_is_refused_after_a_retry(self):
        self.seed(self.thm, self.OLD)
        counts, calls = self.run_pass(self.NEW.replace("implies", "shows"))
        self.assertEqual((counts["refused"], len(calls)), (1, 2))
        meta, body = stage2.read_md(os.path.join(self.out, self.thm.id + ".md"))
        self.assertEqual((body, meta["prompt"]), (self.OLD + "\n", "lecture-v4"))  # left for regeneration

    def test_skips_what_it_must_not_touch(self):
        self.seed(self.intro, self.OLD, source="0" * 64)                   # the page changed
        self.seed(self.thm, "My own words, about U k.", generated="Script.")
        counts, calls = self.run_pass(self.NEW)
        self.assertEqual(calls, [])
        self.assertEqual((counts["page changed"], counts["edited by hand"]), (1, 1))
        self.seed(self.thm, self.OLD, prompt=PROMPT_VERSION)                # already current
        counts, calls = self.run_pass(self.NEW)
        self.assertEqual((calls, counts["current"]), ([], 1))

    def test_edited_scripts_on_request_stay_yours(self):
        self.seed(self.thm, self.OLD, generated="Script.")
        counts, _ = self.run_pass(self.NEW, include_edited=True)
        meta, body = stage2.read_md(os.path.join(self.out, self.thm.id + ".md"))
        self.assertEqual(body, self.NEW + "\n")
        self.assertEqual((meta["prompt"], meta["body"]), ("lecture-v4", stage2._sha("Script.")))
        counts, calls = self.run_pass(self.NEW, include_edited=True)        # phrased once is enough
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
