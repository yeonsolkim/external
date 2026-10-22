#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import re
import sys
import time
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
POSTS_ROOT = ROOT / "_posts"
KST = timezone(timedelta(hours=9))
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", flags=re.DOTALL)
TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s.*)?$")
MANAGED_KEYS = {"layout", "title", "date", "category_path", "created_at", "last_modified_at"}

# Post URLs, as _plugins/permalinks.rb derives them: /<subject>/<title>/ without ordering
# numbers. The two must agree URL for URL (_tests/test_sync_front_matter.py and
# _tests/test_permalinks.rb check the same cases).
ORDER_PREFIX_RE = re.compile(r"^(?:[IVXLCDM]+|\d+)[.)][ \t\n\r\f\v]*", re.IGNORECASE)
NUMBERED_TITLE_RE = re.compile(r"^(?:[IVXLCDM]+|\d+(?:\.\d+)*)[.)][ \t\n\r\f\v]*", re.IGNORECASE)
GENERIC_LABEL_RE = re.compile(r"others?", re.IGNORECASE)
# Latin letters Unicode does not decompose into a base letter and an accent.
FOLDED = {
    "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "ø": "o", "Ø": "O", "đ": "d",
    "Đ": "D", "ð": "d", "Ð": "D", "ł": "l", "Ł": "L", "þ": "th", "Þ": "Th", "ı": "i",
}
STABILITY_INTERVAL_SECONDS = 1.0
REQUIRED_QUIET_CHECKS = 2
MAX_STABILITY_CHECKS = 10


def fmt_time(ts: float) -> str:
    return datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d %H:%M:%S %z")


def fmt_date(ts: float) -> str:
    return datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d")


def created_ts(stat: os.stat_result) -> float:
    return getattr(stat, "st_birthtime", stat.st_mtime)


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def has_top_level_key(front_matter: str, key: str) -> bool:
    for line in front_matter.splitlines():
        match = TOP_LEVEL_KEY_RE.match(line)
        if match and match.group(1) == key:
            return True

    return False


def top_level_entry(front_matter: str, key: str) -> list[str]:
    lines = front_matter.splitlines()

    for i, line in enumerate(lines):
        match = TOP_LEVEL_KEY_RE.match(line)
        if match and match.group(1) == key:
            end = i + 1
            while end < len(lines) and (lines[end].startswith(" ") or lines[end].startswith("\t")):
                end += 1
            return lines[i:end]

    return []


def strip_managed_keys(front_matter: str) -> list[str]:
    lines = front_matter.splitlines()
    kept: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = TOP_LEVEL_KEY_RE.match(line)

        if match and match.group(1) in MANAGED_KEYS:
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                i += 1
            continue

        kept.append(line)
        i += 1

    while kept and not kept[0].strip():
        kept.pop(0)
    while kept and not kept[-1].strip():
        kept.pop()

    return kept


def slug(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text)
    plain = "".join(char for char in plain if unicodedata.category(char) != "Mn")
    plain = "".join(FOLDED.get(char, char) for char in plain)
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def permalink_parts(category_path: list[str], title: str, date: str) -> tuple:
    """(the folders of the URL, the post's own name, its section's name or None)"""
    path = [ORDER_PREFIX_RE.sub("", part.strip(), count=1) for part in category_path]
    path = [part for part in path if part]
    chain = path[:-1] if len(path) >= 3 else path
    section = path[-1] if len(path) >= 3 else None
    folders = []
    subject = next((label for label in reversed(chain) if not GENERIC_LABEL_RE.fullmatch(label)), None)
    if subject:
        folders.append(subject)
    if section and chain and GENERIC_LABEL_RE.fullmatch(chain[-1]):
        folders.append(section)
    name = slug(NUMBERED_TITLE_RE.sub("", title.strip(), count=1)) or date
    return [s for s in map(slug, folders) if s], name, (slug(section) if section else None)


def permalink_url(folders: list[str], name: str) -> str:
    return "/" + "/".join(folders + [name]) + "/"


def derived_permalinks(posts: list[tuple]) -> dict:
    """posts: (key, category_path, title, date, frozen permalink or None). Returns {key: URL}
    for the posts without a permalink; two that would share one take their sections' names."""
    taken = {frozen.strip() for *_, frozen in posts if frozen and frozen.strip()}
    open_posts = [post for post in posts if not (post[4] and post[4].strip())]
    plans = {key: permalink_parts(category_path, title, date)
             for key, category_path, title, date, _ in open_posts}

    first = {key: permalink_url(folders, name) for key, (folders, name, _) in plans.items()}
    counts = Counter(first.values())
    urls = {}
    for key, candidate in first.items():
        folders, name, section = plans[key]
        shared = counts[candidate] > 1 or candidate in taken
        urls[key] = permalink_url(folders, f"{name}-{section}") if shared and section else candidate

    # Still shared (no section to tell the posts apart): the date says which is which.
    counts = Counter(urls.values())
    dates = {key: date for key, _, _, date, _ in open_posts}
    for key, candidate in list(urls.items()):
        if counts[candidate] > 1 or candidate in taken:
            urls[key] = candidate[:-1] + f"-{dates[key]}/"
    return urls


def yaml_scalar(lines: list[str]) -> str | None:
    """The value of a one-line `key: value` entry, unquoted; None without one."""
    if not lines:
        return None
    value = lines[0].split(":", 1)[1].strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return re.sub(r'\\(.)', r"\1", value[1:-1])
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def post_permalink_entry(path: Path) -> tuple:
    """(path, category_path, title, date, frozen permalink) for derived_permalinks."""
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    front_matter = match.group(1) if match else ""
    title = yaml_scalar(top_level_entry(front_matter, "title"))
    if title is None:
        title = DATE_PREFIX_RE.sub("", path.stem).replace("_", " ")
    date = path.name[:10] if DATE_PREFIX_RE.match(path.name) else fmt_date(created_ts(path.stat()))
    categories = list(path.parent.relative_to(POSTS_ROOT).parts)
    return path, categories, title, date, yaml_scalar(top_level_entry(front_matter, "permalink"))


def category_yaml(path: Path) -> list[str]:
    categories = path.parent.relative_to(POSTS_ROOT).parts

    if not categories:
        return ["category_path: []"]

    return ["category_path:", *[f"  - {category}" for category in categories]]


def recorded_created_ts(front_matter: str) -> float | None:
    for line in top_level_entry(front_matter, "created_at")[:1]:
        value = line.split(":", 1)[1].strip().strip("\"'")
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z").timestamp()
        except ValueError:
            return None
    return None


def desired_front_matter(path: Path, stat: os.stat_result, existing_front_matter: str | None,
                         permalink: str | None = None) -> str:
    date_prefix = path.name[:10]
    existing_front_matter = existing_front_matter or ""

    # git re-creates a file on checkout, clone or `rebase --autostash`, which resets its
    # birth time; the creation time already recorded is kept unless the file is older.
    created = created_ts(stat)
    recorded = recorded_created_ts(existing_front_matter)
    if recorded is not None:
        created = min(created, recorded)

    # An existing title is kept as written, so it may differ from the file
    # name; only a missing title is derived from the file name.
    title_lines = top_level_entry(existing_front_matter, "title")
    if not title_lines:
        title = DATE_PREFIX_RE.sub("", path.stem).replace("_", " ")
        title_lines = [f"title: {yaml_quote(title)}"]

    managed = [
        "layout: post",
        *title_lines,
        f"date: {date_prefix} 00:00:00 +0900",
        *category_yaml(path),
        f"created_at: {fmt_time(created)}",
        f"last_modified_at: {fmt_time(stat.st_mtime)}",
    ]

    extra = strip_managed_keys(existing_front_matter)
    if not has_top_level_key(existing_front_matter, "publish"):
        extra.append("publish: false")
    # Like the title, a permalink once written is kept as written: the URL a post was
    # published at stays its URL when the post is renamed or renumbered.
    if permalink and not has_top_level_key(existing_front_matter, "permalink"):
        extra.append(f"permalink: {permalink}")
    lines = managed + ([""] + extra if extra else [])

    return "---\n" + "\n".join(lines) + "\n---\n"


def sync_post(path: Path, permalink: str | None = None) -> tuple[Path, bool]:
    stat = path.stat()
    original_atime = stat.st_atime
    original_mtime = stat.st_mtime

    if not DATE_PREFIX_RE.match(path.name):
        date_prefix = fmt_date(created_ts(stat))
        new_path = path.with_name(f"{date_prefix}-{path.name}")

        if new_path.exists():
            print(f"Skipped rename, target already exists: {new_path.relative_to(ROOT)}")
            return path, False

        path.rename(new_path)
        os.utime(new_path, (original_atime, original_mtime))
        print(f"Renamed: {path.relative_to(ROOT)} -> {new_path.relative_to(ROOT)}")
        path = new_path
        stat = path.stat()

    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)

    if match:
        new_text = desired_front_matter(path, stat, match.group(1), permalink) + text[match.end() :]
    else:
        new_text = desired_front_matter(path, stat, None, permalink) + "\n" + text

    if new_text == text:
        return path, False

    path.write_text(new_text, encoding="utf-8")
    os.utime(path, (original_atime, original_mtime))
    print(f"Updated: {path.relative_to(ROOT)}")
    return path, True


def post_paths(posts_root: Path) -> list[Path]:
    return [
        path
        for path in sorted(posts_root.rglob("*"))
        if path.is_file() and path.suffix in {".md", ".markdown"} and "templates" not in path.parts
    ]


def sync_all_posts(freeze_permalinks: bool = False) -> bool:
    changed = False
    paths = post_paths(POSTS_ROOT)
    permalinks = derived_permalinks([post_permalink_entry(path) for path in paths]) if freeze_permalinks else {}

    for path in paths:
        _, did_change = sync_post(path, permalinks.get(path))
        changed = changed or did_change

    return changed


def stabilize_front_matter(freeze_permalinks: bool = False) -> int:
    # Editors can write an older in-memory buffer back immediately after an
    # external rewrite. Require a quiet window before the caller stages files.
    sync_all_posts(freeze_permalinks)
    quiet_checks = 0

    for check in range(1, MAX_STABILITY_CHECKS + 1):
        time.sleep(STABILITY_INTERVAL_SECONDS)

        if sync_all_posts(freeze_permalinks):
            quiet_checks = 0
            print(
                "Post front matter changed during stabilization; "
                f"retrying ({check}/{MAX_STABILITY_CHECKS})."
            )
            continue

        quiet_checks += 1
        if quiet_checks >= REQUIRED_QUIET_CHECKS:
            quiet_seconds = REQUIRED_QUIET_CHECKS * STABILITY_INTERVAL_SECONDS
            print(
                "Post front matter is stable; "
                f"no editor writes detected for {quiet_seconds:g} seconds."
            )
            return 0

    print(
        "Post front matter did not stabilize. "
        "Stop editing the open note and run the workflow again.",
        file=sys.stderr,
    )
    return 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize Jekyll post front matter with post paths."
    )
    parser.add_argument(
        "--stabilize",
        action="store_true",
        help="wait for editor write-backs to stop before returning",
    )
    parser.add_argument(
        "--freeze-permalinks",
        action="store_true",
        help="write each post's URL into its front matter as `permalink:` where there is none "
        "(site.zsh publish), so renaming or renumbering it later keeps the URL",
    )
    return parser.parse_args()


def main() -> int:
    if not POSTS_ROOT.exists():
        print("_posts directory does not exist.", file=sys.stderr)
        return 1

    args = parse_args()
    if args.stabilize:
        return stabilize_front_matter(args.freeze_permalinks)

    changed = sync_all_posts(args.freeze_permalinks)
    if not changed:
        print("No post front matter changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
