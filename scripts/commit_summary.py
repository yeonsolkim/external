#!/usr/bin/env python3
"""
Commit message for `scripts/site.zsh publish`, summarised from what is staged:

    posts: add Dihedral Groups; update Functions, Categorical Viewpoint; site: assets

    Added:
      _posts/…/2026-09-21-2. Dihedral Groups.md
    Updated:
      …

The subject names posts by their front-matter title (without the "2." ordinal), hand-edited
narration by post, and everything else by its top-level directory. It is at most 72
characters: a list that does not fit keeps its first items and says how many it dropped,
"(+2)". The body lists every staged path, so nothing is hidden by the shortening.

    python3 scripts/commit_summary.py      # prints the message; exit 1 when nothing is staged
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, List, NamedTuple, Optional

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_LIMIT = 72

# Site code, named by directory; a change anywhere else that is not a post or narration is "misc".
SITE_ENTRIES = {
    ".github", "_docs", "_includes", "_layouts", "_narrator", "_plugins", "_sass", "_tests",
    "assets", "scripts", "_config.yml", "Gemfile", "Gemfile.lock",
}
NARRATION_ENTRIES = {"_narration", "audio", "podcast.xml"}
POST_SUFFIXES = {".md", ".markdown"}

VERBS = {"A": "add", "M": "update", "R": "rename", "V": "move", "D": "delete"}
VERB_ORDER = ["A", "M", "R", "V", "D"]
BODY_HEADINGS = {"A": "Added", "M": "Updated", "R": "Renamed", "D": "Deleted"}

ORDINAL_RE = re.compile(r"^\d+(?:\.\d+)*\.[\s-]*")
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
TITLE_RE = re.compile(r"^title:\s*(.*?)\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


class Change(NamedTuple):
    status: str                 # A, M, D or R (C and T are folded into A and M)
    path: str
    old_path: Optional[str] = None


# -- reading git ----------------------------------------------------------------------------
def staged_changes(root: Path = ROOT) -> List[Change]:
    out = subprocess.run(["git", "diff", "--cached", "--name-status", "-z", "-M"], cwd=root,
                         check=True, capture_output=True).stdout.decode("utf-8")
    fields = out.split("\0")
    changes: List[Change] = []
    i = 0
    while i < len(fields) and fields[i]:
        code = fields[i][0]
        if code in "RC":
            old, new = fields[i + 1], fields[i + 2]
            changes.append(Change("R", new, old) if code == "R" else Change("A", new))
            i += 3
        else:
            changes.append(Change({"T": "M"}.get(code, code), fields[i + 1]))
            i += 2
    return changes


def git_title(root: Path = ROOT) -> Callable[[str, str], str]:
    """title_of(path, rev) reading the index (rev ":") or a commit (rev "HEAD")."""
    def title_of(path: str, rev: str) -> str:
        spec = ":" + path if rev == ":" else "%s:%s" % (rev, path)
        shown = subprocess.run(["git", "show", spec], cwd=root, capture_output=True)
        return front_matter_title(shown.stdout.decode("utf-8", "replace")) or ""
    return title_of


def front_matter_title(text: str) -> str:
    match = FRONT_MATTER_RE.match(text)
    title = TITLE_RE.search(match.group(1)) if match else None
    if not title:
        return ""
    value = title.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value.strip()


# -- naming -----------------------------------------------------------------------------------
def clean_name(name: str) -> str:
    """"2. Functions" → "Functions"; also for a file stem or a narration slug."""
    return ORDINAL_RE.sub("", name).strip() or name.strip()


def post_name(path: str, title: str) -> str:
    if title:
        return clean_name(title)
    stem = DATE_PREFIX_RE.sub("", Path(path).stem)
    return clean_name(stem)


def narration_name(path: str) -> str:
    """_narration/2026/07/30/2.-Compact-Sets/<id>.md or audio/2026/07/30/2.-Compact-Sets.json
    → "Compact Sets"; podcast.xml → "feed"."""
    parts = path.split("/")
    if parts[0] == "podcast.xml":
        return "feed"
    slug = parts[4] if parts[0] == "_narration" and len(parts) > 4 else Path(parts[-1]).stem
    return clean_name(slug).replace("-", " ")


def category_of(path: str) -> str:
    top = path.split("/")[0]
    if top == "_posts" and Path(path).suffix in POST_SUFFIXES:
        return "posts"
    if top in NARRATION_ENTRIES:
        return "narration"
    if top in SITE_ENTRIES:
        return "site"
    return "misc"


def misc_name(path: str) -> str:
    parts = path.split("/")
    return "/".join(parts[:2]) if parts[0] == "_posts" and len(parts) > 1 else parts[0]


# -- the message ------------------------------------------------------------------------------
class Group:
    """One "verb items" run in the subject, e.g. "update Functions, Series (+1)"."""

    def __init__(self, verb: str, items: List[str]) -> None:
        self.verb = verb
        self.items = items
        self.shown = len(items)

    def render(self) -> str:
        text = ", ".join(self.items[:self.shown])
        hidden = len(self.items) - self.shown
        head = "%s %s" % (self.verb, text) if self.verb else text
        return head + (" (+%d)" % hidden if hidden else "")


def _unique(items: List[str]) -> List[str]:
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _render(segments: List[tuple]) -> str:
    out = []
    for label, groups in segments:
        rendered = "; ".join(g.render() for g in groups)
        out.append("%s: %s" % (label, rendered))
    return "; ".join(out)


def subject_for(changes: List[Change], title_of: Callable[[str, str], str]) -> str:
    posts: Dict[str, List[str]] = {verb: [] for verb in VERB_ORDER}
    narration, site, misc = [], [], []

    for change in changes:
        category = category_of(change.path)
        if category == "posts":
            if change.status == "R":
                old = post_name(change.old_path or "", title_of(change.old_path or "", "HEAD"))
                new = post_name(change.path, title_of(change.path, ":"))
                if old == new:
                    posts["V"].append(new)
                else:
                    posts["R"].append("%s → %s" % (old, new))
            else:
                rev = "HEAD" if change.status == "D" else ":"
                posts[change.status].append(post_name(change.path, title_of(change.path, rev)))
        elif category == "narration":
            narration.append(narration_name(change.path))
        elif category == "site":
            site.append(change.path.split("/")[0])
        else:
            misc.append(misc_name(change.path))

    segments = []
    post_groups = [Group(VERBS[v], _unique(posts[v])) for v in VERB_ORDER if posts[v]]
    if post_groups:
        segments.append(("posts", post_groups))
    if narration:
        segments.append(("narration", [Group("edit", _unique(narration))]))
    if site:
        segments.append(("site", [Group("", sorted(_unique(site)))]))
    if misc:
        segments.append(("misc", [Group("", sorted(_unique(misc)))]))

    groups = [g for _, gs in segments for g in gs]
    subject = _render(segments)
    while len(subject) > SUBJECT_LIMIT:
        # The longest list gives way first; on a tie the later one (site before posts).
        longest = max(reversed(groups), key=lambda g: g.shown)
        if longest.shown <= 1:
            break
        longest.shown -= 1
        subject = _render(segments)
    # Still too long with one item per list: the later categories keep only their name.
    dropped: List[str] = []
    while len(subject) > SUBJECT_LIMIT and len(segments) > 1:
        dropped.insert(0, segments.pop()[0])
        subject = "%s; +%s" % (_render(segments), ", ".join(dropped))
    if len(subject) > SUBJECT_LIMIT:
        subject = subject[:SUBJECT_LIMIT - 1].rstrip() + "…"
    return subject


def body_for(changes: List[Change]) -> str:
    lines = []
    for status in ("A", "M", "R", "D"):
        entries = [c for c in changes if c.status == status]
        if not entries:
            continue
        lines.append("%s:" % BODY_HEADINGS[status])
        for c in entries:
            lines.append("  %s -> %s" % (c.old_path, c.path) if status == "R" else "  %s" % c.path)
    return "\n".join(lines)


def message_for(changes: List[Change], title_of: Callable[[str, str], str]) -> str:
    return "%s\n\n%s\n" % (subject_for(changes, title_of), body_for(changes))


def main() -> int:
    changes = staged_changes()
    if not changes:
        print("nothing staged", file=sys.stderr)
        return 1
    sys.stdout.write(message_for(changes, git_title()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
