"""Stage 4 — planning, bucket layout, aliases, site manifests, feed. Fake store, no network."""
import json
import os
import tempfile
import unittest

from _narrator import feed, publish, siteconfig, voice
from _narrator.script import write_md
from _narrator.skeleton import build

HTML = ('<html lang="en"><head><link rel="canonical" href="https://x.test/2026/01/02/p.html">'
        '<meta name="description" content="About $A$ and $B$."><meta property="article:published_time" content="2026-01-02T15:00:00+00:00">'
        '<meta name="narrate" content="true"></head><body><article class="post"><h1 class="post-title">P</h1><div class="post-body">'
        '<p>' + 'Intro words here. ' * 12 + '</p><p><strong>Theorem 1.</strong> Let \\(y\\) be ' + 'more words. ' * 10 + '</p>'
        '</div></article></body></html>')
CFG = {"site_url": "https://x.test", "site_title": "Site", "description": "Desc", "title": "Site",
       "author": "Me", "audio_url": "https://audio.test", "cover": "", "category": "Science", "voice": "cedar",
       "language": "en"}


class FakeStore:
    def __init__(self):
        self.objects = {}
        self.copies = []

    def put(self, key, body, content_type, cache_control=""):
        self.objects[key] = bytes(body)

    def put_file(self, key, path, content_type, cache_control=""):
        with open(path, "rb") as handle:
            self.objects[key] = handle.read()

    def get(self, key):
        return self.objects.get(key)

    def head(self, key):
        return {"size": len(self.objects[key])} if key in self.objects else None

    def copy(self, src, dst, content_type, cache_control=""):
        self.copies.append((src, dst))
        self.objects[dst] = self.objects[src]


class Publishing(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        self.narration = os.path.join(root, "_narration")
        self.audio = os.path.join(root, "_audio")
        self.site = os.path.join(root, "_site")
        os.makedirs(self.site)
        self.skel = build(HTML, "p.html")
        self.store = FakeStore()
        self.source = os.path.join(root, "src")
        os.makedirs(self.source)
        self.pub = publish.Publisher(self.store, "https://audio.test", self.site, CFG,
                                     narration_root=self.narration, audio_root=self.audio,
                                     source_dir=self.source, log=lambda m: None)

    def tearDown(self):
        self.tmp.cleanup()

    def scripts(self):
        d = os.path.join(self.narration, "2026", "01", "02", "p")
        for s in self.skel.sections:
            write_md(os.path.join(d, s.id + ".md"), {"section": s.id, "source": s.hash, "body": "x"}, "Script for %s." % s.id)

    def fake_page(self):
        """A page 'assembled' earlier: cache metas + mp3 + manifest with the right page_key."""
        keys = [voice.section_key("Script for %s." % s.id, "cedar", "gpt-4o-mini-tts") for s in self.skel.sections]
        cache = os.path.join(self.audio, "cache")
        os.makedirs(cache)
        for k in keys:
            with open(os.path.join(cache, k + ".flac"), "wb") as f:
                f.write(b"flac")
            with open(os.path.join(cache, k + ".json"), "w") as f:
                json.dump({"key": k, "duration": 1.0}, f)
        mp3, js = voice.page_paths(self.skel, self.audio)
        os.makedirs(os.path.dirname(mp3))
        with open(mp3, "wb") as f:
            f.write(b"mp3bytes")
        manifest = {"url": self.skel.url, "title": "P", "lang": "en", "page_key": voice.page_key(keys),
                    "audio": "p.mp3", "duration": 2.0, "bytes": 8, "voice": "cedar", "model": "gpt-4o-mini-tts",
                    "audio_version": voice.AUDIO_VERSION, "skeleton_hash": self.skel.hash,
                    "sections": [{"id": s.id, "title": s.title, "kind": s.kind, "level": 2, "start": 0, "duration": 1}
                                 for s in self.skel.sections],
                    "chapters": [{"id": "introduction", "title": "Introduction", "start": 0, "end": 1},
                                 {"id": "theorem-1", "title": "Theorem 1", "start": 1, "end": 2}]}
        with open(js, "w") as f:
            json.dump(manifest, f)
        return manifest

    def test_plan_states(self):
        self.assertEqual(self.pub.plan(self.skel)["state"], "scripts")
        self.scripts()
        self.assertEqual(self.pub.plan(self.skel)["state"], "synthesise")
        self.assertGreater(self.pub.plan(self.skel)["minutes"], 0)
        self.fake_page()
        self.assertEqual(self.pub.plan(self.skel)["state"], "assembled")
        self.store.objects["o/%s.json" % self.pub.plan(self.skel)["page_key"]] = b"{}"
        self.assertEqual(self.pub.plan(self.skel)["state"], "published")

    def test_unmarked_post_is_skipped(self):
        unmarked = build(HTML.replace('<meta name="narrate" content="true">', ''), "p.html")
        self.assertFalse(unmarked.narrate)
        self.assertEqual(self.pub.plan(unmarked)["state"], "skip")
        self.assertIn("publish: true", self.pub.plan(unmarked)["why"])

    def test_short_post_is_skipped(self):
        short = build(HTML.replace("Intro words here. " * 12, "Hi.").replace("more words. " * 10, "ok."), "p.html")
        self.assertEqual(self.pub.plan(short)["state"], "skip")

    def test_publish_uploads_then_is_free(self):
        self.scripts()
        manifest = self.fake_page()
        site = self.pub.publish_post(self.skel)
        pk = manifest["page_key"]
        self.assertEqual(self.store.objects["o/%s.mp3" % pk], b"mp3bytes")
        self.assertIn("o/%s.json" % pk, self.store.objects)
        self.assertEqual(self.store.copies, [("o/%s.mp3" % pk, "2026/01/02/p.mp3")])
        self.assertIn("2026/01/02/p.json", self.store.objects)
        chapters = json.loads(self.store.objects["2026/01/02/p.chapters.json"])
        self.assertEqual(chapters["chapters"][1], {"startTime": 1, "title": "Theorem 1", "url": "https://x.test/2026/01/02/p.html#theorem-1"})
        self.assertEqual(site["audio"], "https://audio.test/o/%s.mp3" % pk)
        self.assertEqual(site["stable"], "https://audio.test/2026/01/02/p.mp3")
        self.assertEqual(site["description"], "About $A$ and $B$.")
        self.assertTrue(os.path.exists(os.path.join(self.site, "audio", "2026", "01", "02", "p.json")))
        self.assertTrue(os.path.exists(os.path.join(self.source, "audio", "2026", "01", "02", "p.json")))
        # section cache mirrored
        self.assertEqual(sum(1 for k in self.store.objects if k.startswith("cache/") and k.endswith(".flac")), 2)
        # second run: nothing new
        before = dict(self.store.objects)
        self.pub.publish_post(self.skel)
        self.assertEqual(self.store.objects, before)
        self.assertEqual(len(self.store.copies), 1)

    def test_alias_repointed_when_page_changes(self):
        self.scripts()
        manifest = self.fake_page()
        self.pub.publish_post(self.skel)
        # pretend the alias points at an older page
        self.store.objects["2026/01/02/p.json"] = json.dumps({"page_key": "old"}).encode()
        self.pub.publish_post(self.skel)
        self.assertEqual(len(self.store.copies), 2)

    def test_unpublished_post_loses_its_manifest(self):
        self.scripts()
        self.fake_page()
        self.pub.publish_post(self.skel)
        unmarked = build(HTML.replace('<meta name="narrate" content="true">', ''), "p.html")
        self.pub.publish_post(unmarked)
        self.assertFalse(os.path.exists(os.path.join(self.source, "audio", "2026", "01", "02", "p.json")))
        self.assertFalse(os.path.exists(os.path.join(self.site, "audio", "2026", "01", "02", "p.json")))

    def test_orphan_manifest_is_pruned(self):
        self.scripts()
        self.fake_page()
        self.pub.publish_post(self.skel)
        os.makedirs(os.path.join(self.site, "2026", "01", "02"))
        with open(os.path.join(self.site, "2026", "01", "02", "p.html"), "w") as f:
            f.write("x")
        self.assertEqual(self.pub.prune_orphans(), [])
        os.remove(os.path.join(self.site, "2026", "01", "02", "p.html"))
        self.assertEqual(self.pub.prune_orphans(), ["/2026/01/02/p.html"])
        self.assertEqual(self.pub.site_manifests(), [])

    def test_feed(self):
        self.scripts()
        self.fake_page()
        self.pub.publish_post(self.skel)
        path = self.pub.write_feed()
        self.assertTrue(os.path.exists(os.path.join(self.source, "podcast.xml")))
        with open(path, encoding="utf-8") as handle:
            xml = handle.read()
        self.assertIn("<title>P</title>", xml)
        self.assertIn('<enclosure url="https://audio.test/2026/01/02/p.mp3" length="8" type="audio/mpeg"/>', xml)
        self.assertIn("<pubDate>Fri, 02 Jan 2026 15:00:00 +0000</pubDate>", xml)
        self.assertIn("About A and B. Read the page at https://x.test/2026/01/02/p.html", xml)
        self.assertIn('<podcast:chapters url="https://audio.test/2026/01/02/p.chapters.json"', xml)
        self.assertIn('<guid isPermaLink="true">https://x.test/2026/01/02/p.html</guid>', xml)
        # deterministic: building the feed twice gives identical bytes
        self.assertEqual(xml, feed.build(self.pub.site_manifests(), CFG))
        self.assertIn("<lastBuildDate>", xml)


class Config(unittest.TestCase):
    def test_narration_block(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as handle:
            handle.write('url: "https://x.test"\ntitle: T\nauthor: A\nnarration:\n  author: Real Name\n  audio_url: https://a.test/  # note\n  voice: onyx\nother: 1\n')
            path = handle.name
        try:
            os.environ.pop("AUDIO_BASE_URL", None)
            cfg = siteconfig.load(path)
        finally:
            os.unlink(path)
        self.assertEqual(cfg["site_url"], "https://x.test")
        self.assertEqual(cfg["author"], "Real Name")
        self.assertEqual(cfg["audio_url"], "https://a.test")
        self.assertEqual(cfg["voice"], "onyx")
        self.assertEqual(cfg["title"], "T")


if __name__ == "__main__":
    unittest.main()


class Parallel(unittest.TestCase):
    def test_two_posts_publish_concurrently(self):
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as root:
            store = FakeStore()
            site, source = os.path.join(root, "_site"), os.path.join(root, "src")
            os.makedirs(site); os.makedirs(source)
            pub = publish.Publisher(store, "https://audio.test", site, CFG,
                                    narration_root=os.path.join(root, "_narration"),
                                    audio_root=os.path.join(root, "_audio"), source_dir=source, log=lambda m: None)
            skels = [build(HTML.replace("2026/01/02/p.html", "2026/01/0%d/p%d.html" % (i, i)), "p.html") for i in (3, 4)]
            for sk in skels:
                d = os.path.join(root, "_narration", *publish.url_key(sk).split("/"))
                keys = []
                for s in sk.sections:
                    write_md(os.path.join(d, s.id + ".md"), {"section": s.id, "source": s.hash, "body": "x"}, "Script %s." % s.id)
                    keys.append(voice.section_key("Script %s." % s.id, "cedar", "gpt-4o-mini-tts"))
                cache = os.path.join(root, "_audio", "cache"); os.makedirs(cache, exist_ok=True)
                for k in keys:
                    with open(os.path.join(cache, k + ".flac"), "wb") as f:
                        f.write(b"flac")
                    with open(os.path.join(cache, k + ".json"), "w") as f:
                        json.dump({"key": k, "duration": 1.0}, f)
                mp3, js = voice.page_paths(sk, os.path.join(root, "_audio")); os.makedirs(os.path.dirname(mp3), exist_ok=True)
                with open(mp3, "wb") as f:
                    f.write(b"mp3")
                with open(js, "w") as f:
                    json.dump({"url": sk.url, "title": "P", "lang": "en", "page_key": voice.page_key(keys), "audio": "p.mp3",
                               "duration": 2.0, "bytes": 3, "voice": "cedar", "model": "gpt-4o-mini-tts", "audio_version": voice.AUDIO_VERSION,
                               "skeleton_hash": sk.hash, "sections": [], "chapters": []}, f)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda sk: pub.publish_post(sk), skels))
            self.assertTrue(all(r is not None for r in results))
            self.assertEqual(sorted(k for k in store.objects if k.endswith("p3.mp3") or k.endswith("p4.mp3")),
                             ["2026/01/03/p3.mp3", "2026/01/04/p4.mp3"])
            path = pub.write_feed()
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read().count("<item>"), 2)
