"""
Tests for scripts/sync_posts_front_matter.py.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import sync_posts_front_matter as sync  # noqa: E402

RECORDED = "2026-08-06 13:53:49 +0900"


def front_matter_for(existing):
    posts_root = sync.POSTS_ROOT
    with tempfile.TemporaryDirectory() as tmp:
        sync.POSTS_ROOT = Path(tmp)                 # category_path is relative to it
        try:
            path = Path(tmp) / "2026-06-24-2. Functions.md"
            path.write_text("x", encoding="utf-8")
            text = sync.desired_front_matter(path, path.stat(), existing)
        finally:
            sync.POSTS_ROOT = posts_root
    return text


def created_line(text):
    return [line for line in text.splitlines() if line.startswith("created_at:")][0]


class CreatedAt(unittest.TestCase):
    def test_a_recorded_creation_time_survives_a_recreated_file(self):
        # The file was just written (as git's autostash does), so its birth time is now.
        text = front_matter_for('title: "2. Functions"\ncreated_at: %s' % RECORDED)
        self.assertEqual(created_line(text), "created_at: " + RECORDED)

    def test_a_file_older_than_the_record_wins(self):
        future = "2099-01-01 00:00:00 +0900"
        text = front_matter_for('title: "x"\ncreated_at: %s' % future)
        self.assertNotEqual(created_line(text), "created_at: " + future)

    def test_without_a_record_the_birth_time_is_used(self):
        text = front_matter_for('title: "x"')
        stamp = created_line(text).split(": ", 1)[1]
        age = datetime.now().timestamp() - datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S %z").timestamp()
        self.assertLess(abs(age), 60)

    def test_an_unreadable_record_falls_back_to_the_birth_time(self):
        text = front_matter_for('title: "x"\ncreated_at: sometime')
        self.assertNotIn("sometime", text)


if __name__ == "__main__":
    unittest.main()
