"""podcast.xml — one episode per published page, from the site manifests."""
from __future__ import annotations

import datetime as _dt
import email.utils
import re
from xml.sax.saxutils import escape, quoteattr


def _rfc822(iso: str) -> str:
    if not iso:
        return email.utils.format_datetime(_dt.datetime.now(_dt.timezone.utc))
    try:
        when = _dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return email.utils.format_datetime(_dt.datetime.now(_dt.timezone.utc))
    if when.tzinfo is None:
        when = when.replace(tzinfo=_dt.timezone.utc)
    return email.utils.format_datetime(when)


def _plain(text: str) -> str:
    """Page descriptions carry $TeX$; podcast apps show them as text."""
    return re.sub(r"\$([^$]+)\$", r"\1", text)


def _duration(seconds: float) -> str:
    total = int(round(seconds))
    return "%d:%02d:%02d" % (total // 3600, total % 3600 // 60, total % 60)


def build(manifests: list, cfg: dict) -> str:
    """`manifests` are site manifests (see publish.site_manifest); newest first in the feed."""
    site = cfg["site_url"]
    items = sorted(manifests, key=lambda m: m.get("published_at") or "", reverse=True)
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"'
        ' xmlns:podcast="https://podcastindex.org/namespace/1.0"'
        ' xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        "<title>%s</title>" % escape(cfg["title"]),
        "<link>%s/</link>" % escape(site),
        '<atom:link href=%s rel="self" type="application/rss+xml"/>' % quoteattr(site + "/podcast.xml"),
        "<language>%s</language>" % escape(cfg.get("language") or "en"),
        "<description>%s</description>" % escape(cfg.get("description") or cfg["title"]),
        "<itunes:author>%s</itunes:author>" % escape(cfg.get("author") or ""),
        "<itunes:explicit>false</itunes:explicit>",
        "<itunes:type>episodic</itunes:type>",
        "<itunes:category text=%s/>" % quoteattr(cfg.get("category") or "Science"),
        "<lastBuildDate>%s</lastBuildDate>" % _rfc822(""),
    ]
    if cfg.get("cover"):
        cover = cfg["cover"] if cfg["cover"].startswith("http") else site + cfg["cover"]
        out.append("<itunes:image href=%s/>" % quoteattr(cover))
        out.append("<image><url>%s</url><title>%s</title><link>%s/</link></image>" % (
            escape(cover), escape(cfg["title"]), escape(site)))
    for m in items:
        page = site + m["url"]
        out += [
            "<item>",
            "<title>%s</title>" % escape(m["title"]),
            "<link>%s</link>" % escape(page),
            '<guid isPermaLink="true">%s</guid>' % escape(page),
            "<pubDate>%s</pubDate>" % _rfc822(m.get("published_at") or ""),
            "<description>%s</description>" % escape(_plain(m.get("description") or m["title"]) + " Read the page at " + page),
            '<enclosure url=%s length="%d" type="audio/mpeg"/>' % (quoteattr(m["stable"]), int(m.get("bytes") or 0)),
            "<itunes:duration>%s</itunes:duration>" % _duration(m.get("duration") or 0),
            "<itunes:episodeType>full</itunes:episodeType>",
        ]
        if m.get("chapters_url"):
            out.append('<podcast:chapters url=%s type="application/json+chapters"/>' % quoteattr(m["chapters_url"]))
        out.append("</item>")
    out += ["</channel>", "</rss>", ""]
    return "\n".join(out)
