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


def keys_of(text):
    return [match.group(1) for match in map(sync.TOP_LEVEL_KEY_RE.match, text.splitlines()) if match]


class KeyOrder(unittest.TestCase):
    def test_the_keys_come_in_one_order(self):
        text = front_matter_for("\n".join([
            'title: "2. Functions"', "line_indent: false", "", "publish: true",
            "source_note: After Munkres.", 'description: "Functions as sets of pairs."',
            "permalink: /a/functions/",
        ]))
        self.assertEqual(keys_of(text), ["layout", "category_path", "title", "permalink", "date", "created_at",
                                         "last_modified_at", "publish", "description", "line_indent",
                                         "source_note"])
        self.assertNotIn("\n\n", text)

    def test_a_value_of_several_lines_moves_whole(self):
        text = front_matter_for("source_note: |\n  After Munkres.\n\n  And Halmos.\npublish: true")
        self.assertEqual(keys_of(text)[-2:], ["publish", "source_note"])
        self.assertIn("\nsource_note: |\n  After Munkres.\n\n  And Halmos.\n---\n", text)


# The same cases as _tests/test_permalinks.rb: the sync script and _plugins/permalinks.rb
# must derive the same URL for every post.
ANALYSIS = ["1. Mathematics", "3. Mathematical Analysis", "1. Introduction to Analysis"]
CASES = [
    ("vector spaces", ["1. Mathematics", "2. Algebra", "1. Linear Algebra", "1. Vector Spaces"],
     "1. Vector Spaces", "/linear-algebra/vector-spaces/"),
    ("zf", ["1. Mathematics", "1. Foundations of Mathematics", "3. Axiomatic Set Theory"],
     "1. Axioms of Zermelo–Fraenkel Theory", "/foundations-of-mathematics/axioms-of-zermelo-fraenkel-theory/"),
    ("putnam", ["1. Mathematics", "6. Others"], "The 62nd Putnam", "/mathematics/the-62nd-putnam/"),
    ("questions", ["1. Mathematics", "6. Others", "Questions"], "Linear Algebra",
     "/mathematics/questions/linear-algebra/"),
    ("conditional", ["3. English", "1. Grammar"], "Conditional", "/grammar/conditional/"),
    ("naive", ["1. Mathematics", "Naïve Set Theory"], "1. Sets", "/naive-set-theory/sets/"),
    ("metric", ANALYSIS + ["2. Metric Spaces"], "Exercises", "/introduction-to-analysis/exercises-metric-spaces/"),
    ("ordered", ANALYSIS + ["1. Algebraic and Ordered Structures"], "Exercises",
     "/introduction-to-analysis/exercises-algebraic-and-ordered-structures/"),
]


class Permalinks(unittest.TestCase):
    def test_the_derived_urls(self):
        posts = [(key, path, title, "2026-01-01", None) for key, path, title, _ in CASES]
        derived = sync.derived_permalinks(posts)
        for key, _, _, url in CASES:
            self.assertEqual(derived[key], url, key)

    def test_a_frozen_permalink_keeps_its_url(self):
        posts = [
            ("old", ANALYSIS + ["2. Metric Spaces"], "Exercises", "2026-01-01", "/introduction-to-analysis/exercises/"),
            ("new", ANALYSIS + ["3. Sequences"], "Exercises", "2026-01-02", None),
        ]
        self.assertEqual(sync.derived_permalinks(posts), {"new": "/introduction-to-analysis/exercises-sequences/"})

    def test_without_a_section_the_date_tells_them_apart(self):
        posts = [("a", ["3. English", "1. Grammar"], "Notes", "2026-01-01", None),
                 ("b", ["3. English", "1. Grammar"], "Notes", "2026-01-02", None)]
        self.assertEqual(sync.derived_permalinks(posts),
                         {"a": "/grammar/notes-2026-01-01/", "b": "/grammar/notes-2026-01-02/"})

    def test_freezing_writes_the_permalink_once(self):
        posts_root = sync.POSTS_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            sync.POSTS_ROOT = Path(tmp)
            try:
                path = Path(tmp) / "2026-06-24-2. Functions.md"
                path.write_text("x", encoding="utf-8")
                fresh = sync.desired_front_matter(path, path.stat(), 'title: "2. Functions"', "/a/functions/")
                kept = sync.desired_front_matter(path, path.stat(), 'title: "2. Renamed"\npermalink: /a/functions/',
                                                 "/a/renamed/")
                plain = sync.desired_front_matter(path, path.stat(), 'title: "2. Functions"')
            finally:
                sync.POSTS_ROOT = posts_root
        self.assertIn("\npermalink: /a/functions/\n", fresh)
        self.assertEqual(kept.count("permalink:"), 1)
        self.assertIn("permalink: /a/functions/", kept)
        self.assertNotIn("permalink:", plain)

    def test_an_emptied_permalink_takes_the_frozen_url(self):
        # Obsidian keeps a property whose value was cleared as `permalink:`.
        posts_root = sync.POSTS_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            sync.POSTS_ROOT = Path(tmp)
            try:
                path = Path(tmp) / "2026-06-24-2. Functions.md"
                path.write_text("x", encoding="utf-8")
                frozen = sync.desired_front_matter(path, path.stat(), 'title: "2. Functions"\npermalink:',
                                                   "/a/functions/")
                waiting = sync.desired_front_matter(path, path.stat(), 'title: "2. Functions"\npermalink:')
            finally:
                sync.POSTS_ROOT = posts_root
        self.assertEqual(frozen.count("permalink:"), 1)
        self.assertIn("\npermalink: /a/functions/\n", frozen)
        self.assertIn("\npermalink:\n", waiting)

    def test_a_quoted_title_is_read_as_written(self):
        self.assertEqual(sync.yaml_scalar(['title: "1. Say \\"hi\\""']), '1. Say "hi"')
        self.assertEqual(sync.yaml_scalar(["title: 1. Vector Spaces"]), "1. Vector Spaces")


if __name__ == "__main__":
    unittest.main()
