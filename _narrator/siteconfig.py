"""What the publish stage needs from `_config.yml`, without a YAML dependency.

Reads top-level `key: value` lines and an optional `narration:` block:

    narration:
      title: External — read aloud      # podcast title (default: the site title)
      author: Yeonsol Kim               # podcast author / ID3 artist
      audio_url: https://audio.yeonsolkim.com   # public base of the bucket (env AUDIO_BASE_URL wins)
      cover: /assets/podcast-cover.png  # square artwork, 1400–3000 px, for podcast apps
      category: Science                 # Apple Podcasts category
      voice: cedar
      podcast: true                     # false: no podcast.xml, no feed link
"""
from __future__ import annotations

import os
import re


def _clean(value: str) -> str:
    value = value.strip()
    if value[:1] in ("'", '"') and value[-1:] == value[:1] and len(value) >= 2:
        return value[1:-1]
    return re.sub(r"\s+#.*$", "", value).strip()


def load(path: str = "_config.yml") -> dict:
    top: dict = {}
    block: dict = {}
    current = None
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().split("\n")
    except OSError:
        lines = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        match = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        if indent == 0:
            current = key if value.strip() == "" else None
            if value.strip():
                top[key] = _clean(value)
        elif current == "narration" and indent >= 2 and value.strip():
            block[key] = _clean(value)

    site_url = (top.get("url") or "").rstrip("/") + (top.get("baseurl") or "").rstrip("/")
    title = block.get("title") or top.get("fixed_banner_title") or top.get("title") or "Audio"
    return {
        "site_url": site_url,
        "site_title": top.get("fixed_banner_title") or top.get("title") or "",
        "description": top.get("description") or "",
        "title": title,
        "author": block.get("author") or top.get("author") or "",
        "audio_url": (os.environ.get("AUDIO_BASE_URL") or block.get("audio_url") or "").rstrip("/"),
        "cover": block.get("cover") or "",
        "category": block.get("category") or "Science",
        "voice": block.get("voice") or "",
        "podcast": (block.get("podcast") or "true").lower() not in ("false", "no", "off", "0"),
        "language": top.get("lang") or "en",
    }
