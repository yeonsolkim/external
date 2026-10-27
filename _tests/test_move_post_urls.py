"""
Tests for scripts/move_post_urls.py, which Publish runs right after freezing the post URLs.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import move_post_urls as move  # noqa: E402

LA = ["1. Mathematics", "2. Algebra", "1. Linear Algebra"]
SITE = "https://yeonsolkim.com"
STAMP = "2026-09-26 18:37:18 +0900"


def post(section, name, permalink="", created_at="2026-10-22 10:08:33 +0900", title=None):
    """A Linear Algebra post; its title is the file name's, without the date."""
    folders = LA + [section]
    return move.Post("/".join(["_posts", *folders, name + ".md"]), folders, title or name[11:], name[:10],
                     permalink, created_at)


def moves(before, after):
    return sorted((old, new) for _, old, new in move.url_changes(before, after))


class Changes(unittest.TestCase):
    def test_a_moved_post_whose_permalink_was_deleted_takes_its_title_url(self):
        # As on 2026-10-26: the section folder renamed, the permalink deleted.
        before = [post("2. Linear Maps and Isomorphisms", "2026-10-22-2. Composition, Identities, and Inverses",
                       "/linear-algebra/isomorphisms/")]
        after = [post("2. Linear Maps", "2026-10-22-2. Composition, Identities, and Inverses")]
        self.assertEqual(moves(before, after),
                         [("/linear-algebra/isomorphisms/", "/linear-algebra/composition-identities-and-inverses/")])

    def test_a_moved_post_that_keeps_its_permalink_moves_nothing(self):
        before = [post("2. Linear Maps and Isomorphisms", "2026-10-21-1. Linear Maps and Hom spaces",
                       "/linear-algebra/linear-maps/")]
        after = [post("2. Linear Maps", "2026-10-21-1. Linear Maps and Hom-spaces", "/linear-algebra/linear-maps/")]
        self.assertEqual(moves(before, after), [])

    def test_an_edited_permalink_moves(self):
        before = [post("1. Vector Spaces", "2026-06-02-2. Vector Spaces", "/linear-algebra/vector-spaces/")]
        after = [post("1. Vector Spaces", "2026-06-02-2. Vector Spaces", "/linear-algebra/spaces/")]
        self.assertEqual(moves(before, after), [("/linear-algebra/vector-spaces/", "/linear-algebra/spaces/")])

    def test_a_new_post_moves_nothing(self):
        self.assertEqual(moves([], [post("1. Vector Spaces", "2026-06-02-2. Vector Spaces")]), [])

    def test_posts_stamped_alike_are_told_apart_by_their_date(self):
        # A fresh checkout gave both one created_at; both are moved and lose their permalink.
        before = [post("1. Vector Spaces", "2026-09-01-1. Groups", "/linear-algebra/groups/", STAMP),
                  post("1. Vector Spaces", "2026-06-02-2. Vector Spaces", "/linear-algebra/vector-spaces/", STAMP)]
        after = [post("1. Spaces", "2026-09-01-1. Groups and Fields", created_at=STAMP),
                 post("1. Spaces", "2026-06-02-2. Vector Spaces over a Field", created_at=STAMP)]
        self.assertEqual(moves(before, after),
                         [("/linear-algebra/groups/", "/linear-algebra/groups-and-fields/"),
                          ("/linear-algebra/vector-spaces/", "/linear-algebra/vector-spaces-over-a-field/")])

    def test_posts_nothing_tells_apart_are_not_guessed(self):
        before = [post("1. Vector Spaces", "2026-09-01-1. Groups", "/linear-algebra/groups/", STAMP),
                  post("1. Vector Spaces", "2026-09-01-2. Rings", "/linear-algebra/rings/", STAMP)]
        after = [post("1. Spaces", "2026-09-01-1. Monoids", created_at=STAMP),
                 post("1. Spaces", "2026-09-01-2. Fields", created_at=STAMP)]
        self.assertEqual(moves(before, after), [])


class Mismatches(unittest.TestCase):
    def test_a_post_retitled_since_the_last_publish_is_news(self):
        before = [post("2. Linear Maps", "2026-10-21-1. Linear Maps", "/linear-algebra/linear-maps/")]
        after = [post("2. Linear Maps", "2026-10-21-1. Linear Maps", "/linear-algebra/linear-maps/",
                      title="1. Linear Maps and Hom-spaces")]
        self.assertEqual([found[1:] for found in move.title_mismatches(before, after)],
                         [("/linear-algebra/linear-maps/", "/linear-algebra/linear-maps-and-hom-spaces/", True)])

    def test_an_older_mismatch_is_named_but_is_no_news(self):
        kept = post("2. Linear Maps", "2026-10-21-1. Linear Maps", "/linear-algebra/linear-maps/",
                    title="1. Linear Maps and Hom-spaces")
        self.assertEqual([found[3] for found in move.title_mismatches([kept], [kept])], [False])

    def test_two_posts_of_one_title_carrying_their_sections_are_fine(self):
        posts = [post("2. Metric Spaces", "2026-08-01-Exercises", "/linear-algebra/exercises-metric-spaces/"),
                 post("3. Sequences", "2026-09-01-Exercises", "/linear-algebra/exercises-sequences/")]
        self.assertEqual(move.title_mismatches(posts, posts), [])


class Redirects(unittest.TestCase):
    LINES = ["# Old URLs of posts.", "", '"/2026/10/22/Isomorphisms.html": "/linear-algebra/isomorphisms/"']

    def test_the_old_url_is_sent_on_and_a_redirect_to_it_skips_it(self):
        self.assertEqual(move.redirected(self.LINES, "/linear-algebra/isomorphisms/", "/linear-algebra/composition/"),
                         ["# Old URLs of posts.", "",
                          '"/2026/10/22/Isomorphisms.html": "/linear-algebra/composition/"',
                          '"/linear-algebra/isomorphisms/": "/linear-algebra/composition/"'])

    def test_a_post_back_at_an_old_url_drops_the_redirect_from_it(self):
        self.assertEqual(move.redirected(['"/a/": "/b/"'], "/b/", "/a/"), ['"/b/": "/a/"'])

    def test_twice_is_once(self):
        once = move.redirected(self.LINES, "/linear-algebra/isomorphisms/", "/linear-algebra/composition/")
        self.assertEqual(move.redirected(once, "/linear-algebra/isomorphisms/", "/linear-algebra/composition/"), once)


class Guids(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved, move.AUDIO = move.AUDIO, Path(self.tmp.name)

    def tearDown(self):
        move.AUDIO = self.saved
        self.tmp.cleanup()

    def test_an_episode_keeps_the_url_it_was_first_published_at(self):
        manifest = move.AUDIO / "linear-algebra" / "vector-spaces.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("{}", encoding="utf-8")
        guids = {}
        self.assertTrue(move.keep_guid(guids, "/linear-algebra/vector-spaces/", "/linear-algebra/spaces/", SITE))
        self.assertEqual(guids, {"/linear-algebra/spaces/": SITE + "/linear-algebra/vector-spaces/"})

    def test_a_guid_moves_on_with_its_episode_once(self):
        guids = {"/b/": SITE + "/2026/06/01/1.-Vector-Spaces.html"}
        self.assertTrue(move.keep_guid(guids, "/b/", "/c/", SITE))
        self.assertFalse(move.keep_guid(guids, "/b/", "/c/", SITE))
        self.assertEqual(guids, {"/c/": SITE + "/2026/06/01/1.-Vector-Spaces.html"})

    def test_a_post_without_an_episode_gets_no_guid(self):
        guids = {}
        self.assertFalse(move.keep_guid(guids, "/a/", "/b/", SITE))
        self.assertEqual(guids, {})


class Narration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = move.ROOT, move.NARRATION
        move.ROOT = Path(self.tmp.name)
        move.NARRATION = move.ROOT / "_narration"

    def tearDown(self):
        move.ROOT, move.NARRATION = self.saved
        self.tmp.cleanup()

    def test_the_scripts_move_and_the_old_date_folders_go(self):
        old = move.NARRATION / "2026" / "07" / "30" / "2.-Compact-Sets"
        old.mkdir(parents=True)
        (old / "theorem-2-2-3.md").write_text("x", encoding="utf-8")
        said = move.move_narration("/2026/07/30/2.-Compact-Sets.html", "/introduction-to-analysis/compact-sets/")
        self.assertEqual(said, "moved _narration/2026/07/30/2.-Compact-Sets/ to "
                               "_narration/introduction-to-analysis/compact-sets/")
        self.assertTrue((move.NARRATION / "introduction-to-analysis" / "compact-sets" / "theorem-2-2-3.md").is_file())
        self.assertFalse((move.NARRATION / "2026").exists())

    def test_scripts_already_at_the_new_url_are_left_alone(self):
        for key in ("linear-algebra/isomorphisms", "linear-algebra/composition"):
            (move.NARRATION / key).mkdir(parents=True)
        self.assertTrue(move.move_narration("/linear-algebra/isomorphisms/", "/linear-algebra/composition/")
                        .startswith("left _narration/linear-algebra/isomorphisms/ alone"))
        self.assertTrue((move.NARRATION / "linear-algebra" / "isomorphisms").is_dir())

    def test_a_post_without_narration_has_nothing_to_move(self):
        self.assertIsNone(move.move_narration("/a/", "/b/"))


class Committed(unittest.TestCase):
    def test_head_is_what_was_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "_posts" / "1. Mathematics" / "2026-10-22-3. Kernels and Rank–Nullity.md"
            path.parent.mkdir(parents=True)
            path.write_text("---\ntitle: 3. Kernels and Rank–Nullity\npermalink: /mathematics/dual-spaces/\n---\nx\n",
                            encoding="utf-8")
            git = ["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@example.com"]
            for args in (["init", "-q"], ["add", "."], ["commit", "-q", "-m", "x"]):
                subprocess.run(git + args, check=True)
            path.write_text("---\ntitle: 3. Kernels and Rank–Nullity\n---\nx\n", encoding="utf-8")
            posts = move.committed_posts(Path(tmp))
        self.assertEqual([(found.path, found.title, found.permalink) for found in posts],
                         [("_posts/1. Mathematics/2026-10-22-3. Kernels and Rank–Nullity.md",
                           "3. Kernels and Rank–Nullity", "/mathematics/dual-spaces/")])

    def test_without_a_commit_nothing_was_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            self.assertEqual(move.committed_posts(Path(tmp)), [])


if __name__ == "__main__":
    unittest.main()
