"""
Tests for scripts/diagram_glyphs.py: how it reads and moves an outline. Its fonts are TeX Live's,
so the run itself is not repeated here; test_tikzcd_renderer.rb checks the file it wrote.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import diagram_glyphs as glyphs  # noqa: E402


class OutlineTests(unittest.TestCase):
    def test_numbers_run_together_are_told_apart(self):
        self.assertEqual(glyphs.segments("M577-388V-390C666-433 719-487 734-551Z"), [
            ("M", [577, -388]), ("V", [-390]), ("C", [666, -433, 719, -487, 734, -551]), ("Z", [])])

    def test_an_outline_moves_down_and_not_sideways(self):
        self.assertEqual(glyphs.moved_down("M1-2H5V7C1 2 3 4 5 6S7 8 9 10Z", 100),
                         "M1 98H5V107C1 102 3 104 5 106S7 108 9 110Z")

    def test_the_box_follows_the_curve_not_its_control_points(self):
        left, top, right, bottom = glyphs.box("M0 0C0-40 100-40 100 0Z")
        self.assertEqual((left, right, bottom), (0, 100, 0))
        self.assertAlmostEqual(top, -30)

    def test_an_unknown_command_is_refused(self):
        with self.assertRaises(SystemExit):
            glyphs.segments("M0 0q1 1 2 2z")


class TableTests(unittest.TestCase):
    def test_the_tables_stay_inside_their_fonts(self):
        for font, (_, table) in glyphs.FONTS.items():
            with self.subTest(font=font):
                self.assertTrue(all(0 <= code < 128 for code in table))

    def test_the_calligraphic_capitals_are_unicodes_script_capitals(self):
        self.assertEqual("".join(chr(glyphs.CALLIGRAPHIC[ord(letter)]) for letter in "ABEFHILMNRTZ"),
                         "\U0001D49C\u212C\u2130\u2131\u210B\u2110\u2112\u2133\U0001D4A9\u211B\U0001D4AF\U0001D4B5")


if __name__ == "__main__":
    unittest.main()
