"""
Stage 4 — publish: audio -> the bucket, manifests -> the built site, podcast.xml.

Bucket layout (all under S3_PREFIX):

    o/<page key>.mp3, o/<page key>.json     immutable, content-addressed (the web player)
    <url path>.mp3, .json, .chapters.json   stable aliases (podcast enclosure; guid never moves)
    cache/<section key>.flac, .json         mirror of the section cache, so a fresh checkout
                                            (CI, a new machine) re-assembles pages for free

A page's identity is `page_key` = the ordered section keys + AUDIO_VERSION. Publishing a
post therefore costs nothing when the bucket already holds `o/<page key>.json`: the
manifest is fetched and the site files are written. Otherwise sections are pulled from
the mirror where they exist, synthesised where they do not (guarded by --max-new-minutes),
the page is assembled and uploaded, and the aliases are re-pointed with a server-side copy.

Into the site — twice: the built `_site/` (so this deploy has them) and the SOURCE tree
(`audio/<url path>.json`, `podcast.xml`), which Jekyll copies on every build and which is
committed, so a rebuild never loses them and Pages serves them even when the narration
step does not run:

    audio/<url path>.json     what the page script reads (absolute audio URLs)
    podcast.xml               every published page, newest first
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
from typing import Optional

from . import feed as feedmod
from . import voice as stage3
from .skeleton import Skeleton
from .store import Store

IMMUTABLE = "public, max-age=31536000, immutable"
ALIAS = "public, max-age=300"
MIN_WORDS = 40


class PublishError(Exception):
    pass


def url_key(skel: Skeleton) -> str:
    return re.sub(r"\.html?$", "", skel.url.strip("/"))


class Publisher:
    def __init__(self, store: Optional[Store], base_url: str, site_dir: str, cfg: dict,
                 narration_root: str = "_narration", audio_root: str = "_audio",
                 voice: str = stage3.DEFAULT_VOICE, model: str = stage3.DEFAULT_TTS_MODEL,
                 workers: int = 4, source_dir: Optional[str] = ".", log=print) -> None:
        self.store = store
        self.base_url = base_url.rstrip("/")
        self.site_dir = site_dir
        self.source_dir = source_dir          # None: write only into the built site
        self.cfg = cfg
        self.narration_root = narration_root
        self.audio_root = audio_root
        self.cache_dir = os.path.join(audio_root, "cache")
        self.voice = voice
        self.model = model
        self.workers = workers
        self.log = log

    # -- urls -------------------------------------------------------------------
    def public(self, key: str) -> str:
        return "%s/%s" % (self.base_url, key)

    def site_manifest(self, skel: Skeleton, manifest: dict) -> dict:
        key = url_key(skel)
        return {
            "url": skel.url, "title": skel.title, "lang": skel.lang,
            "description": skel.description, "published_at": skel.published_at,
            "audio": self.public("o/%s.mp3" % manifest["page_key"]),
            "stable": self.public(key + ".mp3"),
            "chapters_url": self.public(key + ".chapters.json"),
            "duration": manifest["duration"], "bytes": manifest["bytes"],
            "voice": manifest["voice"], "page_key": manifest["page_key"],
            "skeleton_hash": manifest["skeleton_hash"],
            "generated": manifest.get("generated") or _dt.date.today().isoformat(),
            "podcast": bool(self.cfg.get("podcast", True)),
            "sections": manifest["sections"], "chapters": manifest["chapters"],
        }

    def chapters_json(self, skel: Skeleton, manifest: dict) -> dict:
        page = self.cfg["site_url"] + skel.url
        # The in-page player gives every located section an id, so the fragment resolves there.
        chapters = [{"startTime": c["start"], "title": c["title"], "url": page + "#" + c["id"]}
                    for c in manifest["chapters"]]
        return {"version": "1.2.0", "title": skel.title, "chapters": chapters}

    # -- mirror -----------------------------------------------------------------
    def fetch_section(self, key: str) -> bool:
        if self.store is None:
            return False
        meta = self.store.get("cache/%s.json" % key)
        if meta is None:
            return False
        flac = self.store.get("cache/%s.flac" % key)
        if flac is None:
            return False
        os.makedirs(self.cache_dir, exist_ok=True)
        for name, data in ((key + ".flac", flac), (key + ".json", meta)):
            tmp = os.path.join(self.cache_dir, name + ".tmp")
            with open(tmp, "wb") as handle:
                handle.write(data)
            os.replace(tmp, os.path.join(self.cache_dir, name))
        return True

    def mirror_sections(self, metas: list) -> int:
        if self.store is None:
            return 0
        uploaded = 0
        for meta in metas:
            key = meta["key"]
            if self.store.head("cache/%s.json" % key):
                continue
            self.store.put_file("cache/%s.flac" % key, os.path.join(self.cache_dir, key + ".flac"),
                                "audio/flac", IMMUTABLE)
            self.store.put_file("cache/%s.json" % key, os.path.join(self.cache_dir, key + ".json"),
                                "application/json", IMMUTABLE)
            uploaded += 1
        return uploaded

    # -- one post ---------------------------------------------------------------
    def plan(self, skel: Skeleton) -> dict:
        """What publishing this post would take. Never spends."""
        if not skel.narrate:
            return {"state": "skip", "why": "publish: true not set in the front matter"}
        if skel.words < MIN_WORDS:
            return {"state": "skip", "why": "%d words" % skel.words}
        try:
            scripts = stage3.scripts_for(skel, self.narration_root)
        except stage3.VoiceError as error:
            why = str(error)
            if why.startswith("no script for"):
                why = "no scripts yet (%d sections)" % (why.count(",") + 1)
            elif why.startswith("scripts out of date"):
                ids = why.split(":", 1)[1].split("—")[0].strip()
                why = ("scripts out of date with the page: %s — regenerated automatically unless "
                       "edited by hand; for an edited one, merge <id>.new.md or run "
                       "`script <post> --accept <id>`" % ids)
            return {"state": "scripts", "why": why}
        keys = [stage3.section_key(body, self.voice, self.model) for _, body in scripts]
        page = stage3.page_key(keys)
        # One HEAD decides the common case. A page the bucket already holds needs nothing
        # else — probing its sections (one HEAD each) is what made a no-op CI run take minutes.
        remote = self.store.head("o/%s.json" % page) if self.store else None
        if remote:
            return {"state": "published", "page_key": page, "scripts": scripts, "keys": keys, "local": None,
                    "remote": True, "to_fetch": 0, "to_synth": 0, "minutes": 0.0}
        local_mp3, local_json = stage3.page_paths(skel, self.audio_root)
        local = None
        if os.path.exists(local_json):
            with open(local_json, encoding="utf-8") as handle:
                local = json.load(handle)
            if local.get("page_key") != page or not os.path.exists(local_mp3):
                local = None
        missing = [(s, b, k) for (s, b), k in zip(scripts, keys) if stage3.cached_section(self.cache_dir, k) is None]
        to_synth = missing
        if self.store and missing and not local:
            to_synth = [(s, b, k) for s, b, k in missing if not self.store.head("cache/%s.json" % k)]
        chars = sum(len(b) for _, b, _ in to_synth)
        state = "assembled" if local else ("assemble" if not to_synth else "synthesise")
        return {"state": state, "page_key": page, "scripts": scripts, "keys": keys, "local": local,
                "remote": False, "to_fetch": len(missing) - len(to_synth),
                "to_synth": len(to_synth), "minutes": chars / 900.0}

    def publish_post(self, skel: Skeleton, max_new_minutes: float = 30.0, dry_run: bool = False,
                     log=None) -> Optional[dict]:
        p = self.plan(skel)
        log = log or self.log
        if p["state"] == "skip":
            log("%-50s skipped (%s)" % (skel.url, p["why"]))
            if not dry_run:
                self.remove_site_manifest(skel.url)
            return None
        if p["state"] == "scripts":
            log("%-50s %s%s" % (skel.url, p["why"], "" if not dry_run else " (a real run generates them first)"))
            return None
        log("%-50s %s%s" % (skel.url, p["state"], "" if p["state"] in ("published", "assembled") else
                            " (%d to fetch, %d to synthesise ≈ %.0f min)" % (p["to_fetch"], p["to_synth"], p["minutes"])))
        if dry_run:
            return None
        if p["to_synth"] and p["minutes"] > max_new_minutes:
            raise PublishError("%s needs ≈%.0f min of new speech, over the --max-new-minutes %.0f guard" % (
                skel.url, p["minutes"], max_new_minutes))

        key = url_key(skel)
        page = p["page_key"]
        manifest = None
        if p["remote"] and self.store:
            manifest = json.loads(self.store.get("o/%s.json" % page).decode("utf-8"))
        else:
            if p["local"]:
                manifest = p["local"]
                metas = [stage3.cached_section(self.cache_dir, k) for k in p["keys"]]
            else:
                metas = stage3.ensure_sections(p["scripts"], self.cache_dir, self.voice, self.model,
                                               workers=self.workers, fetch=self.fetch_section, log=log)
                out_mp3, out_json = stage3.page_paths(skel, self.audio_root)
                manifest = stage3.assemble_page(skel, p["scripts"], metas, self.cache_dir, out_mp3, out_json,
                                                self.voice, self.model, artist=self.cfg.get("author", ""),
                                                album=self.cfg.get("site_title", ""), log=log)
            if self.store:
                n = self.mirror_sections([m for m in metas if m])
                if n:
                    log("  mirrored %d section(s) to the bucket" % n)
            manifest["generated"] = _dt.date.today().isoformat()
            if self.store:
                out_mp3, _ = stage3.page_paths(skel, self.audio_root)
                self.store.put_file("o/%s.mp3" % page, out_mp3, "audio/mpeg", IMMUTABLE)
                self.store.put("o/%s.json" % page, json.dumps(manifest, ensure_ascii=False).encode("utf-8"),
                               "application/json", IMMUTABLE)
                log("  uploaded o/%s.mp3 (%.1f MB)" % (page[:12], manifest["bytes"] / 1e6))

        site = self.site_manifest(skel, manifest)
        if self.store:
            alias = self.store.get(key + ".json")
            current = alias and json.loads(alias.decode("utf-8")).get("page_key") == page
            if not current:
                self.store.copy("o/%s.mp3" % page, key + ".mp3", "audio/mpeg", ALIAS)
                self.store.put(key + ".json", json.dumps(site, ensure_ascii=False).encode("utf-8"),
                               "application/json", ALIAS)
                self.store.put(key + ".chapters.json",
                               json.dumps(self.chapters_json(skel, manifest), ensure_ascii=False).encode("utf-8"),
                               "application/json+chapters", ALIAS)
                log("  aliases -> %s.mp3 / .json / .chapters.json" % key)
        self.write_site_manifest(site)
        return site

    def _roots(self) -> list:
        roots = [self.site_dir]
        if self.source_dir and os.path.abspath(self.source_dir) != os.path.abspath(self.site_dir):
            roots.append(self.source_dir)
        return roots

    def write_site_manifest(self, site: dict) -> str:
        rel = os.path.join("audio", *(url_key_from(site["url"]) + ".json").split("/"))
        text = json.dumps(site, ensure_ascii=False, indent=2)
        path = ""
        for root in self._roots():
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
        return path

    def remove_site_manifest(self, url: str) -> None:
        """A post that is no longer published loses its manifest (the bucket keeps the audio)."""
        rel = os.path.join("audio", *(url_key_from(url) + ".json").split("/"))
        for root in self._roots():
            path = os.path.join(root, rel)
            if os.path.exists(path):
                os.remove(path)

    def orphans(self, site_dir: Optional[str] = None) -> list:
        """URLs of manifests whose page no longer exists in the built site (renamed or deleted posts)."""
        site_dir = site_dir or self.site_dir
        return [m["url"] for m in self.site_manifests()
                if not os.path.exists(os.path.join(site_dir, *m["url"].strip("/").split("/")))]

    def prune_orphans(self, site_dir: Optional[str] = None, dry_run: bool = False) -> list:
        """Drop the orphans' manifests; the bucket keeps their audio. Returns the URLs."""
        found = self.orphans(site_dir)
        for url in found:
            if not dry_run:
                self.remove_site_manifest(url)
            self.log("%-50s %s: page no longer exists" % (url, "would remove" if dry_run else "removed"))
        return found

    # -- feed ---------------------------------------------------------------------
    def site_manifests(self) -> list:
        root = os.path.join(self.source_dir or self.site_dir, "audio")
        found = []
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if name.endswith(".json"):
                    with open(os.path.join(dirpath, name), encoding="utf-8") as handle:
                        found.append(json.load(handle))
        return found

    def write_feed(self) -> Optional[str]:
        if not self.cfg.get("podcast", True):
            self.log("podcast.xml: disabled (narration.podcast: false)")
            for root in self._roots():
                if os.path.exists(os.path.join(root, "podcast.xml")):
                    os.remove(os.path.join(root, "podcast.xml"))
            return None
        manifests = self.site_manifests()
        xml = feedmod.build(manifests, self.cfg)
        path = ""
        for root in self._roots():
            path = os.path.join(root, "podcast.xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(xml)
        self.log("podcast.xml: %d episode(s)" % len(manifests))
        return path


def url_key_from(url: str) -> str:
    return re.sub(r"\.html?$", "", url.strip("/"))
