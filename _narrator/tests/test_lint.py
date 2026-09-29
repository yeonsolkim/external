"""The script lint and the one retry it earns — no network. `python3 -m unittest _narrator.tests.test_lint`"""
import os
import tempfile
import unittest

from _narrator import lint, llm
from _narrator import script as stage2
from _narrator.tests.test_script import skel


class Problems(unittest.TestCase):
    def test_a_clean_script(self):
        self.assertEqual(lint.problems(
            "n factorial equals n times the quantity n minus one, and so on, down to two times one."), [])

    def test_spoken_typography(self):
        for text in ("times dot dot dot, times two", "open parenthesis x", "x comma y",
                     "the vertical bar", "a backslash"):
            self.assertTrue(lint.problems(text), text)

    def test_tex_left_in_the_script(self):
        for text in (r"the set \mathbb R", "x_i", "x^2", "the family {U}", "$x$"):
            self.assertTrue(lint.problems(text), text)

    def test_a_paragraph_that_stops_inside_a_sentence(self):
        found = lint.problems("The factorial of n is defined by\n\nn factorial equals one.")
        self.assertEqual(len(found), 1)
        self.assertIn("paragraph ends inside a sentence", found[0])
        for fine in ('He said "one."\n\nTwo.', "Two (three.)\n\nFour.", "Is it?\n\nYes!\n\nThe end"):
            self.assertEqual(lint.problems(fine), [], fine)

    def test_ordinary_words_are_not_marks(self):
        # "par", "bar", "brace yourself" … only the phrases lecturers must not say are caught.
        self.assertEqual(lint.problems("On a par with the bar exam, the barrier holds."), [])

    def test_the_tree_skips_glossaries_and_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, body in (("a.md", "x comma y"), ("glossary.md", r"\mathcal U — U"),
                               ("a.new.md", "x comma y"), ("b.md", "clean")):
                with open(os.path.join(tmp, name), "w", encoding="utf-8") as handle:
                    handle.write("---\nsection: s\n---\n\n" + body + "\n")
            found = lint.check_tree(tmp)
            self.assertEqual([os.path.basename(p) for p, _ in found], ["a.md"])


class Retry(unittest.TestCase):
    def setUp(self):
        self.real_chat = llm.chat
        self.calls = []

    def tearDown(self):
        llm.chat = self.real_chat

    def run_with(self, replies):
        """replies = (first draft, retry draft) for every section."""
        def fake(system, user, **kwargs):
            self.calls.append(user)
            if system.startswith("You are preparing the NOTATION GLOSSARY"):
                return ""
            return replies[1] if "YOUR PREVIOUS DRAFT" in user else replies[0]
        llm.chat = fake
        with tempfile.TemporaryDirectory() as tmp:
            stage2.run(skel(), tmp, model="m", workers=1, log=lambda *_: None)
            scripts = {}
            for name in os.listdir(tmp):
                if name.endswith(".md") and name != "glossary.md":
                    scripts[name] = stage2.read_md(os.path.join(tmp, name))[1].strip()
        return scripts

    def lecture_calls(self):
        return [c for c in self.calls if "SECTION" in c]

    def test_a_clean_draft_is_kept_without_a_retry(self):
        scripts = self.run_with(["Clean text."])
        self.assertTrue(all(body == "Clean text." for body in scripts.values()))
        self.assertTrue(all("YOUR PREVIOUS DRAFT" not in c for c in self.lecture_calls()))

    def test_a_slip_is_retried_once_and_the_better_draft_kept(self):
        scripts = self.run_with(["x comma y.", "x and y."])
        self.assertIn("x and y.", scripts.values())
        retries = [c for c in self.lecture_calls() if "YOUR PREVIOUS DRAFT" in c]
        self.assertEqual(len(retries), 2)             # one per section, never more
        self.assertIn('"comma"', retries[0])

    def test_a_retry_that_is_no_better_is_dropped(self):
        scripts = self.run_with(["x comma y.", "x comma y comma z."])
        self.assertIn("x comma y.", scripts.values())


if __name__ == "__main__":
    unittest.main()
