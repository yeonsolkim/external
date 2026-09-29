"""
Tests for scripts/commit_summary.py, the Publish workflow's commit message.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import commit_summary as cs  # noqa: E402

P = "_posts/1. Mathematics/2. Analysis/1. Topology"
TITLES = {
    P + "/2026-07-30-2. Compact Sets.md": "2. Compact Sets",
    P + "/2026-08-05-3. Perfect Sets.md": "3. Perfect Sets",
    P + "/2026-09-21-2. Dihedral Groups.md": "2. Dihedral Groups",
    P + "/2026-06-24-2. Functions.md": "2. Functions",
}


def title_of(path, rev):
    return TITLES.get(path, "")


def subject(*changes):
    return cs.subject_for([cs.Change(*c) for c in changes], title_of)


class Subject(unittest.TestCase):
    def test_posts_are_named_by_title_without_the_ordinal(self):
        self.assertEqual(subject(("A", P + "/2026-09-21-2. Dihedral Groups.md"),
                                 ("M", P + "/2026-07-30-2. Compact Sets.md"),
                                 ("M", P + "/2026-08-05-3. Perfect Sets.md")),
                         "posts: add Dihedral Groups; update Compact Sets, Perfect Sets")

    def test_a_post_without_a_title_falls_back_to_its_file_name(self):
        self.assertEqual(subject(("M", "_posts/x/2026-09-26-Categorical Viewpoint.md")),
                         "posts: update Categorical Viewpoint")

    def test_categories_are_joined_in_a_fixed_order(self):
        self.assertEqual(subject(("M", "index.md"),
                                 ("M", "assets/css/post.css"),
                                 ("M", "_narration/2026/09/18/1.-Series/theorem-1.md"),
                                 ("M", "_posts/x/2026-01-01-A.md")),
                         "posts: update A; narration: edit Series; site: assets; misc: index.md")

    def test_later_categories_keep_only_their_name_when_nothing_else_fits(self):
        self.assertEqual(subject(("M", "assets/css/post.css"),
                                 ("M", "_plugins/document_structure.rb"),
                                 ("M", P + "/2026-06-24-2. Functions.md"),
                                 ("M", "_narration/2026/07/30/2.-Compact-Sets/theorem-2-2-3.md"),
                                 ("M", "README.md")),
                         "posts: update Functions; narration: edit Compact Sets; +site, misc")

    def test_narration_outputs_group_by_post(self):
        self.assertEqual(subject(("M", "_narration/2026/07/30/2.-Compact-Sets/index.json"),
                                 ("M", "_narration/2026/07/30/2.-Compact-Sets/glossary.md"),
                                 ("M", "audio/2026/07/30/2.-Compact-Sets.json"),
                                 ("M", "podcast.xml")),
                         "narration: edit Compact Sets, feed")

    def test_a_rename_that_keeps_the_title_is_a_move(self):
        self.assertEqual(subject(("R", P + "/2026-06-24-2. Functions.md",
                                  "_posts/old place/2026-06-24-2. Functions.md")),
                         "posts: move Functions")

    def test_a_rename_that_changes_the_title_shows_both(self):
        TITLES["_posts/x/2026-09-12-4. Upper and Lower Limits.md"] = "4. Upper and Lower Limits"
        self.assertEqual(subject(("R", P + "/2026-06-24-2. Functions.md",
                                  "_posts/x/2026-09-12-4. Upper and Lower Limits.md")),
                         "posts: rename Upper and Lower Limits → Functions")

    def test_a_long_list_is_cut_and_counted(self):
        changes = [("M", "_posts/x/2026-01-%02d-%d. Long Post Title %d.md" % (n, n, n))
                   for n in range(1, 8)]
        text = subject(*changes)
        self.assertEqual(text, "posts: update Long Post Title 1, Long Post Title 2 (+5)")

    def test_the_longest_list_is_cut_first(self):
        changes = [("M", "_posts/x/2026-01-%02d-Post number %d.md" % (n, n)) for n in range(1, 9)]
        changes.append(("M", "assets/css/post.css"))
        text = subject(*changes)
        self.assertLessEqual(len(text), cs.SUBJECT_LIMIT)
        self.assertTrue(text.endswith("; site: assets"), text)

    def test_on_a_tie_the_later_list_gives_way(self):
        self.assertEqual(subject(("M", "_posts/x/2026-01-01-Functions.md"),
                                 ("M", "_posts/x/2026-01-02-Categorical Viewpoint.md"),
                                 ("M", "_posts/x/2026-01-03-Vocabularies II.md"),
                                 ("A", "_tests/test_commit_summary.py"),
                                 ("A", "scripts/site.zsh")),
                         "posts: update Functions, Categorical Viewpoint (+1); site: _tests (+1)")

    def test_one_huge_name_is_truncated(self):
        text = subject(("A", "_posts/x/2026-01-01-" + "Very long " * 12 + ".md"))
        self.assertLessEqual(len(text), cs.SUBJECT_LIMIT)
        self.assertTrue(text.endswith("…"), text)


class Body(unittest.TestCase):
    def test_every_path_is_listed_under_its_status(self):
        changes = [cs.Change("A", "a.md"), cs.Change("M", "b.md"), cs.Change("M", "c.md"),
                   cs.Change("R", "new.md", "old.md"), cs.Change("D", "gone.md")]
        self.assertEqual(cs.body_for(changes),
                         "Added:\n  a.md\nUpdated:\n  b.md\n  c.md\n"
                         "Renamed:\n  old.md -> new.md\nDeleted:\n  gone.md")


class FrontMatter(unittest.TestCase):
    def test_quoted_title(self):
        self.assertEqual(cs.front_matter_title('---\nlayout: post\ntitle: "2. Functions"\n---\nx'),
                         "2. Functions")

    def test_no_front_matter(self):
        self.assertEqual(cs.front_matter_title("title: not front matter\n"), "")


if __name__ == "__main__":
    unittest.main()
