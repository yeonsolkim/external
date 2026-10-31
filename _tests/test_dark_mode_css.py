"""
Tests for scripts/dark_mode_css.py, which generates the dark-mode block of each stylesheet.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import dark_mode_css as dark  # noqa: E402


def run(*args):
    """The script's exit status and output, as if run with these arguments."""
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status = dark.main(list(args))
    return status, output.getvalue()


class Check(unittest.TestCase):
    def test_every_stored_block_is_what_the_script_generates(self):
        # A colour edited without rerunning the script leaves dark mode on the old colour.
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/dark_mode_css.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_colour_changed_since_the_last_run_fails_the_check_and_is_left_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            sheet = Path(tmp) / "style.css"
            sheet.write_text(".site-footer {\n  color: #575757c2 !important;\n}\n")
            with mock.patch.object(dark, "ROOT", Path(tmp)), mock.patch.object(dark, "STYLESHEETS", [sheet]):
                self.assertEqual(run(), (0, "updated style.css\n"))
                self.assertIn("color: #a8a8a8c2 !important;", sheet.read_text())
                self.assertEqual(run(), (0, "Every dark-mode block is up to date.\n"))
                self.assertEqual(run("--check"), (0, "Every dark-mode block is up to date.\n"))

                edited = sheet.read_text().replace("#575757c2", "#575757ed")
                sheet.write_text(edited)
                status, output = run("--check")
                self.assertEqual(status, 1)
                self.assertIn("-    color: #a8a8a8c2 !important;\n+    color: #a8a8a8ed !important;\n", output)
                self.assertEqual(sheet.read_text(), edited)


class Adjusted(unittest.TestCase):
    def test_a_key_with_an_alpha_adjusts_that_colour_only(self):
        # The posts' 71% black text is lifted on the black page; other blacks still just invert.
        block = dark.dark_block(".a { color: #000000b5; }\n.b { color: #000000; }\n.c { color: #00000091; }\n")
        self.assertIn("color: #e0e0e0;", block)
        self.assertIn("color: #ffffff;", block)
        self.assertIn("color: #ffffff91;", block)


if __name__ == "__main__":
    unittest.main()
