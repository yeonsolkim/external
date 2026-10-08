"""
Tests for scripts/check_spelling.py.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_spelling as spelling  # noqa: E402

DICTIONARY = {
    "Sequences", "Subsequences", "Viewpoint", "Categorical", "Sets", "Theory", "Axioms", "of", "into", "uniform",
}


def stand_in_checker(words):
    """The macOS spell checker's part: the words it rejects, with guesses."""
    return {word: ["Subsequences"] if word == "Subsequenes" else [] for word in words if word not in DICTIONARY}


class Words(unittest.TestCase):
    def test_numbers_and_other_scripts_are_skipped(self):
        self.assertEqual(spelling.words_in("2. The Spaces of the 62nd 집합"), ["The", "Spaces", "of", "the"])

    def test_a_decomposed_letter_stays_in_its_word(self):
        self.assertEqual(spelling.words_in("Nai\u0308ve"), ["Naïve"])

    def test_dashes_split_words_and_apostrophes_do_not(self):
        self.assertEqual(
            spelling.words_in("Zermelo–Fraenkel Outer-Measure Euler’s"),
            ["Zermelo", "Fraenkel", "Outer", "Measure", "Euler’s"],
        )

    def test_math_goes_with_what_is_attached_to_it(self):
        self.assertEqual(
            spelling.words_in("the $n$th term of an $n$-ary relation, where $$\\sum_k a_k$$ converges"),
            ["the", "term", "of", "an", "relation", "where", "converges"],
        )
        self.assertEqual(spelling.words_in("the $n$-*th root*"), ["the", "root"])

    def test_pronunciations_are_skipped_but_and_or_is_prose(self):
        self.assertEqual(
            spelling.words_in("<b>society</b> /səˈsaiət̬i/: people, and/or /rizembl/ Weierstrass \\|ˈwaɪ.ɚ.stræs\\|"),
            ["society", "people", "and", "or", "Weierstrass"],
        )

    def test_ipa_in_a_table_cell_leaves_the_next_cell_alone(self):
        self.assertEqual(
            spelling.words_in("|Karl Weierstrass \\|ˈwaɪ.ɚ.stræs\\||Rigorous analysis|"),
            ["Karl", "Weierstrass", "Rigorous", "analysis"],
        )

    def test_code_html_liquid_and_link_targets_are_skipped(self):
        self.assertEqual(
            spelling.words_in('`cdoe` <span class="qed">x</span> {% include nav.html %} [the text](https://exmaple.com/pth)'),
            ["the", "text"],
        )

    def test_a_less_than_sign_in_prose_is_not_a_tag(self):
        self.assertEqual(
            spelling.words_in("since a < bigger and certain > d holds"),
            ["since", "bigger", "and", "certain", "holds"],
        )

    def test_a_fenced_block_is_skipped(self):
        self.assertEqual(spelling.words_in("Before\n```tikzcd\nA \\arrow[r] & Bxyz\n```\nAfter"), ["Before", "After"])


class ReportedOncePerPost(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def post(self, name, title=None, body="", date="2026-09-04"):
        path = self.root / "3. Sequences" / f"{date}-{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'---\nlayout: post\ntitle: "{title or name}"\n---\n\n{body}\n', encoding="utf-8")
        return path

    def run_check(self, seen):
        findings, record = spelling.check(self.root, seen, stand_in_checker)
        return [finding.line() for finding in findings], record

    def test_a_reported_post_passes_while_it_does_not_change(self):
        self.post("2. Subsequenes")
        report, record = self.run_check({})
        self.assertEqual(report, ["Subsequenes (Subsequences?) in 2. Subsequenes"])
        report, record = self.run_check(record)
        self.assertEqual(report, [])
        self.assertEqual(record, {"3. Sequences/2026-09-04-2. Subsequenes.md": ["Subsequenes"]})

    def test_the_text_is_checked_and_the_front_matter_is_not(self):
        self.post("2. Subsequences", body="Sets of Sequences, into a uniform conlcusion.")
        report, _ = self.run_check({})
        self.assertEqual(report, ["conlcusion in 2. Subsequences"])

    def test_only_a_new_word_in_the_text_is_reported(self):
        self.post("2. Subsequences", body="Sets of Zermelo.")
        _, record = self.run_check({})
        self.post("2. Subsequences", body="Sets of Zermelo, into Fraenkel.")
        report, _ = self.run_check(record)
        self.assertEqual(report, ["Fraenkel in 2. Subsequences"])

    def test_only_a_new_word_in_the_title_is_reported(self):
        self.post("1. Axioms of Zermelo Theory")
        _, record = self.run_check({})
        self.post("1. Axioms of Zermelo Theory", title="1. Axioms of Zermelo Theroy")
        report, _ = self.run_check(record)
        self.assertEqual(report, ["Theroy in 1. Axioms of Zermelo Theory"])

    def test_a_fixed_post_leaves_the_record(self):
        path = self.post("2. Subsequenes")
        _, record = self.run_check({})
        path.unlink()
        self.post("2. Subsequences")
        report, record = self.run_check(record)
        self.assertEqual((report, record), ([], {}))

    def test_a_title_left_behind_by_a_rename_is_reported_again(self):
        path = self.post("2. Subsequenes")
        _, record = self.run_check({})
        path.rename(path.with_name("2026-09-04-2. Subsequences.md"))
        report, _ = self.run_check(record)
        self.assertEqual(report, ["Subsequenes (Subsequences?) in 2. Subsequences"])

    def test_a_renamed_file_is_a_new_post(self):
        path = self.post("3. Zermelo Sets")
        _, record = self.run_check({})
        path.rename(path.with_name("2026-09-04-4. Zermelo Sets.md"))
        report, _ = self.run_check(record)
        self.assertEqual(report, ["Zermelo in 4. Zermelo Sets"])

    def test_a_title_that_differs_from_the_file_name_is_checked_too(self):
        self.post("Categorical Viewpoint", title="Setz: Categorical Viewpoint")
        report, _ = self.run_check({})
        self.assertEqual(report, ["Setz in Categorical Viewpoint"])

    def test_without_a_record_everything_is_reported_every_time(self):
        self.post("2. Subsequenes")
        first, _ = self.run_check(None)
        second, _ = self.run_check(None)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 1)


class ReportPage(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def page(self, name, body, title=None):
        path = self.root / "2. Metric Spaces" / f"2026-07-31-{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'---\ntitle: "{title or name}"\n---\n{body}\n', encoding="utf-8")
        findings, _ = spelling.check(
            self.root, None, lambda words: {w: ["conclusion", "concussion"] for w in words if w in ("conlcusion", "adj")}
        )
        return spelling.report_page(findings, "Publish stopped.")

    def test_a_word_is_shown_in_its_line_with_the_guesses_and_a_link_to_the_post(self):
        page = self.page("2. Compact Sets", "Before.\n\nTurning <b>pointwise</b> information into a uniform conlcusion.\nAfter.")
        self.assertIn("Turning pointwise information into a uniform <mark>conlcusion</mark>.", page)
        self.assertNotIn("&lt;b&gt;", page)  # the quoted line drops its markup
        self.assertIn("→ conclusion? concussion?", page)
        self.assertIn('<p class="note">Publish stopped.</p>', page)
        self.assertIn('href="obsidian://open?path=%2F', page)
        self.assertIn('<p class="path">2. Metric Spaces</p>', page)

    def test_every_place_a_word_occurs_is_named(self):
        page = self.page("Vocabularies I", "x (adj) y\n\nz (adj) w (adj)", title="Vocabularies adj")
        self.assertIn("· title, text, 3 times", page)

    def test_a_long_line_is_cut_around_the_word(self):
        page = self.page("2. Compact Sets", "word " * 40 + "conlcusion" + " word" * 40)
        context = re.search(r'<p class="context">(.*?)</p>', page).group(1)
        self.assertTrue(context.startswith("…") and context.endswith("…"), context)
        self.assertLess(len(context), 200)


if __name__ == "__main__":
    unittest.main()
