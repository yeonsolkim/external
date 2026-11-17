"""
Tests for scripts/sync_posts_front_matter.py.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import contextlib
import io
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
            'title: "2. Functions"', "line_indent: false", "", "published: true", "narration: true",
            "source_note: After Munkres.", 'description: "Functions as sets of pairs."',
            "permalink: /a/functions/",
        ]))
        self.assertEqual(keys_of(text), ["layout", "category_path", "title", "permalink", "date", "created_at",
                                         "last_modified_at", "narration", "published", "description",
                                         "line_indent", "source_note"])
        self.assertNotIn("\n\n", text)

    def test_a_value_of_several_lines_moves_whole(self):
        text = front_matter_for("source_note: |\n  After Munkres.\n\n  And Halmos.\nnarration: true\npublished: true")
        self.assertEqual(keys_of(text)[-3:], ["narration", "published", "source_note"])
        self.assertIn("\nsource_note: |\n  After Munkres.\n\n  And Halmos.\n---\n", text)


class Checkboxes(unittest.TestCase):
    def test_a_post_without_them_gets_them_unticked(self):
        self.assertIn("\nnarration: false\npublished: false\n", front_matter_for('title: "x"'))

    def test_a_ticked_box_stays_ticked(self):
        text = front_matter_for('title: "x"\nnarration: true\npublished: true')
        self.assertIn("\nnarration: true\npublished: true\n", text)


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

    def test_a_namesake_of_a_post_carrying_its_section_takes_its_own(self):
        posts = [
            ("old", ANALYSIS + ["2. Metric Spaces"], "Exercises", "2026-01-01",
             "/introduction-to-analysis/exercises-metric-spaces/"),
            ("new", ANALYSIS + ["3. Sequences"], "Exercises", "2026-01-02", None),
        ]
        self.assertEqual(sync.derived_permalinks(posts), {"new": "/introduction-to-analysis/exercises-sequences/"})

    def test_without_a_section_a_namesake_of_a_frozen_post_takes_its_date(self):
        posts = [("a", ["3. English", "1. Grammar"], "Notes", "2026-01-01", "/grammar/notes-2026-01-01/"),
                 ("b", ["3. English", "1. Grammar"], "Notes", "2026-01-02", None)]
        self.assertEqual(sync.derived_permalinks(posts), {"b": "/grammar/notes-2026-01-02/"})

    def test_freezing_writes_the_permalink_it_is_given(self):
        posts_root = sync.POSTS_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            sync.POSTS_ROOT = Path(tmp)
            try:
                path = Path(tmp) / "2026-06-24-2. Functions.md"
                path.write_text("x", encoding="utf-8")
                fresh = sync.desired_front_matter(path, path.stat(), 'title: "2. Functions"\npublished: true',
                                                  "/a/functions/")
                moved = sync.desired_front_matter(path, path.stat(),
                                                  'title: "2. Renamed"\npublished: true\npermalink: /a/functions/',
                                                  "/a/renamed/")
                kept = sync.desired_front_matter(path, path.stat(),
                                                 'title: "2. Functions"\npublished: true\npermalink: /a/functions/')
                plain = sync.desired_front_matter(path, path.stat(), 'title: "2. Functions"\npublished: true')
            finally:
                sync.POSTS_ROOT = posts_root
        self.assertIn("\npermalink: /a/functions/\n", fresh)
        self.assertEqual(moved.count("permalink:"), 1)
        self.assertIn("\npermalink: /a/renamed/\n", moved)
        self.assertIn("\npermalink: /a/functions/\n", kept)
        self.assertNotIn("permalink:", plain)

    def test_a_post_not_published_keeps_no_url_yet(self):
        # Unticked, or without the box yet: the sync is about to write it unticked.
        posts_root = sync.POSTS_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            sync.POSTS_ROOT = Path(tmp)
            try:
                path = Path(tmp) / "2026-06-24-2. Functions.md"
                path.write_text("x", encoding="utf-8")
                for existing in ('title: "2. Functions"\npublished: false', 'title: "2. Functions"'):
                    text = sync.desired_front_matter(path, path.stat(), existing, "/a/functions/")
                    self.assertNotIn("permalink:", text)
            finally:
                sync.POSTS_ROOT = posts_root

    def test_an_emptied_permalink_takes_the_frozen_url(self):
        # Obsidian keeps a property whose value was cleared as `permalink:`.
        posts_root = sync.POSTS_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            sync.POSTS_ROOT = Path(tmp)
            try:
                path = Path(tmp) / "2026-06-24-2. Functions.md"
                path.write_text("x", encoding="utf-8")
                frozen = sync.desired_front_matter(path, path.stat(),
                                                   'title: "2. Functions"\npublished: true\npermalink:',
                                                   "/a/functions/")
                waiting = sync.desired_front_matter(path, path.stat(),
                                                    'title: "2. Functions"\npublished: true\npermalink:')
            finally:
                sync.POSTS_ROOT = posts_root
        self.assertEqual(frozen.count("permalink:"), 1)
        self.assertIn("\npermalink: /a/functions/\n", frozen)
        self.assertIn("\npermalink:\n", waiting)

    def test_a_quoted_title_is_read_as_written(self):
        self.assertEqual(sync.yaml_scalar(['title: "1. Say \\"hi\\""']), '1. Say "hi"')
        self.assertEqual(sync.yaml_scalar(["title: 1. Vector Spaces"]), "1. Vector Spaces")


LINEAR = ["1. Mathematics", "3. Linear Algebra"]


class DuePermalinks(unittest.TestCase):
    """What Publish writes as `permalink:`: the URL follows the title, not the numbering."""

    def test_a_permalink_the_title_still_gives_stays(self):
        # Renumbered, and moved to another section of its textbook.
        posts = [("rank", LINEAR + ["4. Dimension"], "3. The Rank Function", "2026-11-04",
                  "/linear-algebra/the-rank-function/")]
        self.assertEqual(sync.due_permalinks(posts), {})

    def test_a_retitled_post_takes_its_title_url(self):
        posts = [("rank", LINEAR + ["3. Dimension"], "2. The Dimension Function", "2026-11-04",
                  "/linear-algebra/the-rank-function/")]
        self.assertEqual(sync.due_permalinks(posts), {"rank": "/linear-algebra/the-dimension-function/"})

    def test_a_post_filed_under_another_textbook_takes_its_url(self):
        posts = [("compact", ["1. Mathematics", "4. Mathematical Analysis", "2. Metric Spaces"], "2. Compact Sets",
                  "2026-07-31", "/introduction-to-analysis/compact-sets/")]
        self.assertEqual(sync.due_permalinks(posts), {"compact": "/mathematical-analysis/compact-sets/"})

    def test_a_post_without_one_takes_its_title_url(self):
        posts = [("rank", LINEAR + ["3. Dimension"], "3. Rank", "2026-11-20", None)]
        self.assertEqual(sync.due_permalinks(posts), {"rank": "/linear-algebra/rank/"})

    def test_a_permalink_edited_by_hand_gives_way_to_the_title(self):
        posts = [("spaces", LINEAR + ["2. Vector Spaces"], "1. Vector Spaces", "2026-06-02", "/linear-algebra/spaces/")]
        self.assertEqual(sync.due_permalinks(posts), {"spaces": "/linear-algebra/vector-spaces/"})

    def test_a_url_told_apart_by_its_section_or_date_stays_without_its_namesake(self):
        posts = [("metric", ANALYSIS + ["2. Metric Spaces"], "Exercises", "2026-08-31",
                  "/introduction-to-analysis/exercises-metric-spaces/"),
                 ("notes", ["3. English", "1. Grammar"], "Notes", "2026-01-01", "/grammar/notes-2026-01-01/")]
        self.assertEqual(sync.due_permalinks(posts), {})

    def test_a_renamed_section_renames_the_url_that_carries_it(self):
        posts = [("ordered", ANALYSIS + ["1. Number Systems"], "Exercises", "2026-09-18",
                  "/introduction-to-analysis/exercises-algebraic-and-ordered-structures/"),
                 ("metric", ANALYSIS + ["2. Metric Spaces"], "Exercises", "2026-08-31",
                  "/introduction-to-analysis/exercises-metric-spaces/")]
        self.assertEqual(sync.due_permalinks(posts), {"ordered": "/introduction-to-analysis/exercises-number-systems/"})

    def test_a_textbook_renamed_moves_namesakes_together(self):
        analysis = ["1. Mathematics", "4. Mathematical Analysis"]
        posts = [("ordered", analysis + ["1. Number Systems"], "Exercises", "2026-09-18",
                  "/introduction-to-analysis/exercises-algebraic-and-ordered-structures/"),
                 ("metric", analysis + ["2. Metric Spaces"], "Exercises", "2026-08-31",
                  "/introduction-to-analysis/exercises-metric-spaces/")]
        self.assertEqual(sync.due_permalinks(posts),
                         {"ordered": "/mathematical-analysis/exercises-number-systems/",
                          "metric": "/mathematical-analysis/exercises-metric-spaces/"})

    def test_a_retitled_post_freezes_once_and_then_stays(self):
        # What the stabilizing sync relies on: a second pass changes nothing.
        saved = sync.ROOT, sync.POSTS_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            sync.ROOT, sync.POSTS_ROOT = Path(tmp), Path(tmp)
            try:
                path = Path(tmp) / "1. Mathematics" / "3. Linear Algebra" / "3. Dimension" / \
                    "2026-11-04-2. The Dimension Function.md"
                path.parent.mkdir(parents=True)
                path.write_text('---\ntitle: 2. The Dimension Function\npermalink: /linear-algebra/the-rank-function/\n'
                                'published: true\n---\nx\n', encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()):
                    first, second = sync.sync_all_posts(True), sync.sync_all_posts(True)
                text = path.read_text(encoding="utf-8")
            finally:
                sync.ROOT, sync.POSTS_ROOT = saved
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertIn("\npermalink: /linear-algebra/the-dimension-function/\n", text)


if __name__ == "__main__":
    unittest.main()
