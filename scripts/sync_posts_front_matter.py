#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
POSTS_ROOT = ROOT / "_posts"
KST = timezone(timedelta(hours=9))
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", flags=re.DOTALL)
MANAGED_KEYS = {"layout", "title", "date", "category_path", "created_at", "last_modified_at"}


def fmt_time(ts: float) -> str:
    return datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d %H:%M:%S %z")


def fmt_date(ts: float) -> str:
    return datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d")


def created_ts(stat: os.stat_result) -> float:
    return getattr(stat, "st_birthtime", stat.st_mtime)


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def strip_managed_keys(front_matter: str) -> list[str]:
    lines = front_matter.splitlines()
    kept: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s.*)?$", line)

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


def category_yaml(path: Path) -> list[str]:
    categories = path.parent.relative_to(POSTS_ROOT).parts

    if not categories:
        return ["category_path: []"]

    return ["category_path:", *[f"  - {category}" for category in categories]]


def desired_front_matter(path: Path, stat: os.stat_result, existing_front_matter: str | None) -> str:
    date_prefix = path.name[:10]
    title = DATE_PREFIX_RE.sub("", path.stem).replace("_", " ")

    managed = [
        "layout: post",
        f"title: {yaml_quote(title)}",
        f"date: {date_prefix} 00:00:00 +0900",
        *category_yaml(path),
        f"created_at: {fmt_time(created_ts(stat))}",
        f"last_modified_at: {fmt_time(stat.st_mtime)}",
    ]

    extra = strip_managed_keys(existing_front_matter or "")
    lines = managed + ([""] + extra if extra else [])

    return "---\n" + "\n".join(lines) + "\n---\n"


def sync_post(path: Path) -> tuple[Path, bool]:
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
        new_text = desired_front_matter(path, stat, match.group(1)) + text[match.end() :]
    else:
        new_text = desired_front_matter(path, stat, None) + "\n" + text

    if new_text == text:
        return path, False

    path.write_text(new_text, encoding="utf-8")
    os.utime(path, (original_atime, original_mtime))
    print(f"Updated: {path.relative_to(ROOT)}")
    return path, True


def main() -> int:
    if not POSTS_ROOT.exists():
        print("_posts directory does not exist.", file=sys.stderr)
        return 1

    changed = False

    for path in sorted(POSTS_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".markdown"}:
            continue
        if "templates" in path.parts:
            continue

        _, did_change = sync_post(path)
        changed = changed or did_change

    if not changed:
        print("No post front matter changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
