#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import re
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
POSTS_ROOT = ROOT / "_posts"
KST = timezone(timedelta(hours=9))
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", flags=re.DOTALL)
MANAGED_KEYS = {"layout", "title", "date", "category_path", "created_at", "last_modified_at"}
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


def sync_all_posts() -> bool:
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

    return changed


def stabilize_front_matter() -> int:
    # Editors can write an older in-memory buffer back immediately after an
    # external rewrite. Require a quiet window before the caller stages files.
    sync_all_posts()
    quiet_checks = 0

    for check in range(1, MAX_STABILITY_CHECKS + 1):
        time.sleep(STABILITY_INTERVAL_SECONDS)

        if sync_all_posts():
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
        "Stop editing the open note and run Git Stage again.",
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
    return parser.parse_args()


def main() -> int:
    if not POSTS_ROOT.exists():
        print("_posts directory does not exist.", file=sys.stderr)
        return 1

    args = parse_args()
    if args.stabilize:
        return stabilize_front_matter()

    changed = sync_all_posts()
    if not changed:
        print("No post front matter changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
