"""The script lint and the one retry it earns — no network. `python3 -m unittest _narrator.tests.test_lint`"""
import json
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

    def test_a_term_said_again_for_its_notation(self):
        for text in (
                "If every entry equals zero, the matrix is called the zero matrix, denoted by the zero matrix.",
                "The closure of A in M is the set of all closure points of A, denoted by the closure of A.",
                "The interior of A denotes the interior of A in M, the set of all interior points of A in M.",
                "The open ball of radius r centered at a is the set, the open ball of radius r about a, defined "
                "by the open ball of radius r about a equals the set of all x in M such that d of x and a is less than r.",
                "Note that the zero subspace is a subspace; it is called the zero subspace of V.",
                "The set closure of S is called the closure of S."):
            found = lint.problems(text)
            self.assertEqual(len(found), 1, text)
            self.assertIn("term said again for its notation", found[0])

    def test_the_notation_said_as_written(self):
        for text in (
                "If every entry equals zero, the matrix is called the zero matrix, denoted by capital O.",
                "The closure of A in M is the set of all closure points of A, denoted by A bar.",
                "Int A denotes the interior of A in M, the set of all interior points of A in M.",
                # A notation repeated on purpose: only the names of marks repeat.
                "The closed ball of radius r centered at a is the set B bar r of a, defined by B bar r of a "
                "equals the set of all x in M such that d of x and a is at most r.",
                # Words that meet across a comma ("n, the factorial") are not a repetition.
                "For a positive integer n, the factorial of n is defined by n factorial equals n times the "
                "quantity n minus one, and so on, down to two times one.",
                "If W one intersect W two equals the zero subspace, then the sum of W one and W two is called "
                "the direct sum, which is denoted by W one direct sum W two."):
            self.assertEqual(lint.problems(text), [], text)

    def test_accepted_repetitions(self):
        for text in (
                "Two functions f and g are equal if f of x equals g of x for all x in S, and the zero function "
                "is defined by the zero function of x equals zero for all x in S.",
                "If S is nonempty, the span of S is the set span of S, defined by span of S equals the set of "
                "all v in V such that v is a linear combination of the vectors in S."):
            self.assertEqual(lint.problems(text), [], text)

    def test_the_tree_skips_glossaries_and_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, body in (("a.md", "x comma y"), ("glossary.md", r"\mathcal U — U"),
                               ("a.new.md", "x comma y"), ("b.md", "clean")):
                with open(os.path.join(tmp, name), "w", encoding="utf-8") as handle:
                    handle.write("---\nsection: s\n---\n\n" + body + "\n")
            found = lint.check_tree(tmp)
            self.assertEqual([os.path.basename(p) for p, _ in found], ["a.md"])

    def test_the_tree_skips_scripts_the_index_no_longer_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("sec-4.md", "numbered-4.md"):
                with open(os.path.join(tmp, name), "w", encoding="utf-8") as handle:
                    handle.write("---\nsection: s\n---\n\nx comma y\n")
            with open(os.path.join(tmp, "index.json"), "w", encoding="utf-8") as handle:
                json.dump({"sections": [{"id": "sec-4", "file": "sec-4.md"}]}, handle)
            self.assertEqual([os.path.basename(p) for p, _ in lint.check_tree(tmp)], ["sec-4.md"])


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

    def test_a_term_said_again_is_retried(self):
        scripts = self.run_with(["The matrix is called the zero matrix, denoted by the zero matrix.",
                                 "The matrix is called the zero matrix, denoted by capital O."])
        self.assertIn("The matrix is called the zero matrix, denoted by capital O.", scripts.values())
        retries = [c for c in self.lecture_calls() if "YOUR PREVIOUS DRAFT" in c]
        self.assertIn("term said again for its notation", retries[0])
        self.assertIn("the notation is said as written", retries[0])


if __name__ == "__main__":
    unittest.main()
