"""
Tests for scripts/learn_spelling.py and its word list, scripts/spelling_words.txt.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_spelling as spelling  # noqa: E402
import learn_spelling as learn  # noqa: E402


class ListedWords(unittest.TestCase):
    def test_comments_blank_lines_and_repeats_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "words.txt"
            path.write_text("# people\nZermelo\n\nFraenkel  # set theory\nZermelo\nNai\u0308ve\n", encoding="utf-8")
            self.assertEqual(learn.listed_words(path), ["Zermelo", "Fraenkel", "Naïve"])

    def test_every_listed_word_is_one_word_to_the_spelling_check(self):
        # A hyphenated or spaced entry would never match: the check splits text into words first.
        for word in learn.listed_words():
            self.assertEqual(spelling.words_in(word), [word], word)


if __name__ == "__main__":
    unittest.main()
