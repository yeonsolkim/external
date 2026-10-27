#!/usr/bin/env python3
"""
Carry over what hangs on a post's URL when the URL changes, and name the posts whose title no
longer gives the URL they keep.

    python3 scripts/move_post_urls.py           what Publish would move, and the posts whose
                                                title would give another URL
    python3 scripts/move_post_urls.py --apply   move it (scripts/site.zsh publish, right after
                                                the front matter is frozen)

A post's URL changes when its `permalink:` is deleted or emptied, so that Publish freezes the
URL of its current title (scripts/sync_posts_front_matter.py), or when it is edited by hand.
The URL it had is the one it has in HEAD, which is what the last Publish put online; the post
is found there at its path, or, when it was moved or renamed, by its `created_at` or its URL.
For each post whose URL changed, --apply

- sends the old URL on to the new one in `_data/redirects.yml`. A redirect to the old URL
  leads to the new one instead, so none takes two steps, and one from the new URL goes: the
  post is back there.
- moves `_narration/<old>/` to `_narration/<new>/`, so its scripts are not written again
  (_narrator/README.md, Moving a page).
- keeps the guid of the post's podcast episode: `_narration/podcast-guids.json` maps the new
  URL to the guid the episode was first published with.

Running it again changes nothing.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys

from sync_posts_front_matter import (DATE_PREFIX_RE, FRONT_MATTER_RE, POSTS_ROOT, ROOT, derived_permalinks,
                                     post_paths, top_level_entry, yaml_quote, yaml_scalar)

sys.path.insert(0, str(ROOT))
from _narrator import siteconfig  # noqa: E402

REDIRECTS = ROOT / "_data" / "redirects.yml"
NARRATION = ROOT / "_narration"
GUIDS = NARRATION / "podcast-guids.json"
AUDIO = ROOT / "audio"
REDIRECT_RE = re.compile(r'^("(?:[^"\\]|\\.)*"):\s*("(?:[^"\\]|\\.)*")\s*$')


@dataclass
class Post:
    path: str                   # from the repository's root, as git names it
    category_path: list[str]
    title: str
    date: str                   # the file name's YYYY-MM-DD
    permalink: str              # "" when there is none
    created_at: str


def read_post(path: str, text: str) -> Post:
    match = FRONT_MATTER_RE.match(text)
    front_matter = match.group(1) if match else ""
    name = Path(path).name
    title = yaml_scalar(top_level_entry(front_matter, "title"))
    if title is None:
        title = DATE_PREFIX_RE.sub("", Path(path).stem).replace("_", " ")
    return Post(path, list(Path(path).parent.relative_to("_posts").parts), title,
                name[:10] if DATE_PREFIX_RE.match(name) else "",
                (yaml_scalar(top_level_entry(front_matter, "permalink")) or "").strip(),
                yaml_scalar(top_level_entry(front_matter, "created_at")) or "")


def is_post(path: str) -> bool:
    """What post_paths takes for a post."""
    return Path(path).suffix in {".md", ".markdown"} and "templates" not in Path(path).parts


def committed_posts(root: Path = ROOT) -> list[Post]:
    """The posts as HEAD has them: what the last Publish put online."""
    listing = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", "_posts"],
                             cwd=root, capture_output=True)
    if listing.returncode:
        return []                                   # no commit yet: nothing was published
    paths = [path for path in listing.stdout.decode("utf-8").split("\0") if path and is_post(path)]
    batch = subprocess.run(["git", "cat-file", "--batch"], cwd=root, capture_output=True, check=True,
                           input="".join(f"HEAD:{path}\n" for path in paths).encode("utf-8")).stdout
    posts, at = [], 0
    for path in paths:                              # "<id> blob <size>\n<content>\n" each
        header_end = batch.index(b"\n", at)
        start, size = header_end + 1, int(batch[at:header_end].split()[2])
        posts.append(read_post(path, batch[start:start + size].decode("utf-8")))
        at = start + size + 1
    return posts


def working_posts() -> list[Post]:
    return [read_post(path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8"))
            for path in post_paths(POSTS_ROOT)]


def entries(posts: list[Post]) -> list[tuple]:
    """The posts as derived_permalinks takes them."""
    return [(post.path, post.category_path, post.title, post.date, post.permalink or None) for post in posts]


def served_urls(posts: list[Post]) -> dict[str, str]:
    """{path: URL}: the frozen permalink, or else the URL _plugins/permalinks.rb derives."""
    derived = derived_permalinks(entries(posts))
    return {post.path: post.permalink or derived[post.path] for post in posts}


def title_urls(posts: list[Post]) -> dict[str, str]:
    """{path: the URL its title gives}: the one it would take were no URL frozen, so that two
    posts of one title both carry their section's name, as the scheme has it."""
    return derived_permalinks([entry[:4] + (None,) for entry in entries(posts)])


def counterparts(before: list[Post], after: list[Post], old_urls: dict, new_urls: dict) -> dict[str, Post]:
    """{path now: the post as it was}. A post is the one at its path; one moved or renamed is the
    one with its created_at, or else the one at its URL. created_at alone is no identity (a fresh
    checkout stamped many posts with one time), so a match counts only when nothing else shares
    it, and the file name's date tells such posts apart."""
    left = {post.path: post for post in before}
    found = {post.path: left.pop(post.path) for post in after if post.path in left}

    def pair(key_now, key_then) -> None:
        rest = [post for post in after if post.path not in found]
        now, then = Counter(map(key_now, rest)), Counter(map(key_then, left.values()))
        for post in rest:
            key = key_now(post)
            if key and now[key] == 1 and then[key] == 1:
                old = next(old for old in left.values() if key_then(old) == key)
                found[post.path] = left.pop(old.path)

    def stamp_and_date(post: Post):
        return post.created_at and (post.created_at, post.date)

    pair(lambda post: post.created_at, lambda post: post.created_at)
    pair(stamp_and_date, stamp_and_date)
    pair(lambda post: new_urls[post.path], lambda post: old_urls[post.path])
    return found


def url_changes(before: list[Post], after: list[Post]) -> list[tuple[Post, str, str]]:
    """(post, the URL it had, the URL it has) for each post whose URL changed since HEAD."""
    old_urls, new_urls = served_urls(before), served_urls(after)
    found = counterparts(before, after, old_urls, new_urls)
    return [(post, old_urls[found[post.path].path], new_urls[post.path]) for post in after
            if post.path in found and old_urls[found[post.path].path] != new_urls[post.path]]


def title_mismatches(before: list[Post], after: list[Post]) -> list[tuple[Post, str, str, bool]]:
    """(post, its URL, the URL its title gives, whether that changed since HEAD) for each post
    that keeps a URL its title no longer gives."""
    old_urls, urls, wanted = served_urls(before), served_urls(after), title_urls(after)
    found, then = counterparts(before, after, old_urls, urls), title_urls(before)
    return [(post, urls[post.path], wanted[post.path],
             post.path not in found or then[found[post.path].path] != wanted[post.path])
            for post in after if urls[post.path] != wanted[post.path]]


def unquote(text: str) -> str:
    return re.sub(r"\\(.)", r"\1", text[1:-1])


def redirected(lines: list[str], old: str, new: str) -> list[str]:
    """The lines of redirects.yml, with `old` sent on to `new`."""
    kept, sent = [], False
    for line in lines:
        match = REDIRECT_RE.match(line)
        if match:
            source, target = unquote(match.group(1)), unquote(match.group(2))
            if source == new:
                continue                            # the post is back at a URL it once left
            if source == old or target == old:      # one step, never two
                sent = sent or source == old
                if target != new:
                    line = f"{yaml_quote(source)}: {yaml_quote(new)}"
        kept.append(line)
    if not sent:
        kept.append(f"{yaml_quote(old)}: {yaml_quote(new)}")
    return kept


def url_path(url: str) -> str:
    """The URL as _narrator/publish.py's url_key puts it in paths: no slashes at the ends, no .html."""
    return re.sub(r"\.html?$", "", url.strip("/"))


def move_narration(old: str, new: str) -> str | None:
    """Move the post's narration scripts to its new URL; what happened, or None with none to move."""
    source, target = NARRATION / url_path(old), NARRATION / url_path(new)
    if not source.is_dir():
        return None
    if target.exists():
        return f"left {source.relative_to(ROOT)}/ alone: {target.relative_to(ROOT)}/ is there already"
    target.parent.mkdir(parents=True, exist_ok=True)
    source.rename(target)
    parent = source.parent
    while parent != NARRATION and not any(parent.iterdir()):     # an old URL's date folders
        parent.rmdir()
        parent = parent.parent
    return f"moved {source.relative_to(ROOT)}/ to {target.relative_to(ROOT)}/"


def keep_guid(guids: dict, old: str, new: str, site_url: str) -> bool:
    """Give the post's podcast episode, if it has one, the guid it had at `old`
    (_narrator/publish.py takes guids[URL], or else the URL). False when there is nothing to do."""
    if new in guids or not (old in guids or (AUDIO / f"{url_path(old)}.json").is_file()):
        return False
    guids[new] = guids.pop(old, None) or site_url + old
    return True


def apply(changes: list[tuple[Post, str, str]]) -> dict[str, list[str]]:
    """Carry each change over; {new URL: what was done for it}."""
    if not changes:
        return {}
    done = {new: [f"{old} redirects to {new}"] for _, old, new in changes}

    text = REDIRECTS.read_text(encoding="utf-8") if REDIRECTS.exists() else ""
    lines = text.splitlines()
    for _, old, new in changes:
        lines = redirected(lines, old, new)
    if "\n".join(lines) + "\n" != text:
        REDIRECTS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for _, old, new in changes:
        moved = move_narration(old, new)
        if moved:
            done[new].append(moved)

    guids = json.loads(GUIDS.read_text(encoding="utf-8")) if GUIDS.exists() else {}
    site_url = siteconfig.load(str(ROOT / "_config.yml"))["site_url"]
    kept = [new for _, old, new in changes if keep_guid(guids, old, new, site_url)]
    if kept:
        GUIDS.write_text(json.dumps(guids, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                         encoding="utf-8")
    for new in kept:
        done[new].append("its podcast episode keeps its guid")
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description="Carry over what hangs on a post's URL when it changes.")
    parser.add_argument("--apply", action="store_true",
                        help="redirect the old URLs, move the narration, keep the podcast guids (Publish)")
    args = parser.parse_args()

    before, after = committed_posts(), working_posts()
    changes = url_changes(before, after)
    done = apply(changes) if args.apply else {}
    for post, old, new in changes:
        print(f"{'Moved' if args.apply else 'Will move'} {old} to {new} ({post.title})")
        for line in done.get(new, []):
            print(f"  {line}")
    for post, url, wanted, retitled in title_mismatches(before, after):
        print(f"{'New title, same URL' if retitled else 'Title and URL differ'}: {url} "
              f"(the title {post.title!r} gives {wanted}; delete its permalink: to move it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
