"""
Stage 2 — script: skeleton sections -> a formal lecture script per section, as
editable Markdown files under `_narration/<post url>/`.

Files (one directory per post, keyed by the post's canonical URL path):

    _narration/2026/07/30/2.-Compact-Sets/
        index.json                 reading order + provenance (derived; rewritten each run)
        glossary.md                notation glossary for the whole document
        theorem-2-2-3.md           one script per narrated section
        prose-after-theorem-2-2-3.md

Each script file is front matter + the script. Provenance in the front matter decides
what a later run does:

    source   the section's skeleton hash. Different now -> the section changed.
    body     sha256 of the script as generated. Different now -> you edited it.
    prompt   PROMPT_VERSION it was generated with.

A section regenerates when `source` or `prompt` moved (or --force). An edited file is
never overwritten: the run writes the fresh draft next to it as `<id>.new.md`, marks the
file `stale: true`, and says so. The glossary is keyed by the document's set of distinct
equations, so prose edits leave it alone; a glossary change does NOT cascade into the
sections — a reviewed script does not get worse because an equation was added elsewhere.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from . import llm
from .prompts import (PROMPT_VERSION, GLOSSARY_SYSTEM, LECTURE_SYSTEM, glossary_user,
                      section_user, macros_from_mathjax_config)
from .skeleton import SKELETON_VERSION, Skeleton, Section, glossary_source

DEFAULT_MODEL = "gpt-5.5"
MATHJAX_CONFIG = os.path.join("assets", "js", "mathjax-config.js")


# ----------------------------------------------------------------------------- files
def post_dir(root: str, skel: Skeleton) -> str:
    key = re.sub(r"\.html?$", "", skel.url.strip("/"))
    return os.path.join(root, *key.split("/"))


def _sha(text: str) -> str:
    """Hash of a script body, insensitive to surrounding blank lines and trailing spaces."""
    canonical = "\n".join(line.rstrip() for line in text.strip().split("\n"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def read_md(path: str) -> tuple:
    """-> (front matter dict, body). Values are strings; missing file -> ({}, '')."""
    if not os.path.exists(path):
        return {}, ""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[4:end].split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"')
    return meta, text[end + 5:].lstrip("\n")


def write_md(path: str, meta: dict, body: str) -> None:
    lines = ["---"]
    for key, value in meta.items():
        value = str(value)
        if re.search(r"[:#\"]", value) or value != value.strip():
            value = '"%s"' % value.replace('"', '\\"')
        lines.append("%s: %s" % (key, value))
    lines.append("---")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n\n" + body.rstrip("\n") + "\n")


def _today() -> str:
    return _dt.date.today().isoformat()


# ----------------------------------------------------------------------------- planning
class Plan:
    """What one run will do, before it spends anything."""

    def __init__(self) -> None:
        self.glossary: Optional[str] = None      # reason, when it will be generated
        self.generate: list = []                 # (section, reason)
        self.stale: list = []                    # (section, path) edited files whose source moved
        self.current: list = []                  # sections already up to date
        self.skipped: list = []                  # (section, reason)

    def summary(self) -> str:
        parts = []
        if self.glossary:
            parts.append("glossary (%s)" % self.glossary)
        parts.append("%d section(s) to generate" % len(self.generate))
        if self.stale:
            parts.append("%d edited & stale" % len(self.stale))
        parts.append("%d current" % len(self.current))
        if self.skipped:
            parts.append("%d skipped" % len(self.skipped))
        return ", ".join(parts)


def plan(skel: Skeleton, out_dir: str, force: bool = False, only: Optional[set] = None) -> Plan:
    p = Plan()
    gmeta, gbody = read_md(os.path.join(out_dir, "glossary.md"))
    gsource = glossary_key(skel)
    if force or not gbody:
        p.glossary = "forced" if gbody else "new"
    elif gmeta.get("source") != gsource:
        if gmeta.get("body") and gmeta.get("body") != _sha(gbody):
            p.stale.append((None, os.path.join(out_dir, "glossary.md")))
        else:
            p.glossary = "equations changed"

    for section in skel.sections:
        if section.skip:
            p.skipped.append((section, section.skip))
            continue
        if section.words == 0 and section.math == 0:
            p.skipped.append((section, "empty"))
            continue
        if only and section.id not in only:
            p.skipped.append((section, "not selected"))
            continue
        path = os.path.join(out_dir, section.id + ".md")
        meta, body = read_md(path)
        edited = bool(body) and meta.get("body") not in ("", None) and meta.get("body") != _sha(body)
        if force:
            if edited:
                p.stale.append((section, path))
            else:
                p.generate.append((section, "forced"))
        elif not body:
            p.generate.append((section, "new"))
        elif meta.get("source") != section.hash:
            if edited:
                p.stale.append((section, path))
            else:
                p.generate.append((section, "section changed"))
        elif meta.get("prompt") != PROMPT_VERSION:
            if edited:
                p.current.append(section)      # your words beat a prompt bump
            else:
                p.generate.append((section, "prompt %s -> %s" % (meta.get("prompt"), PROMPT_VERSION)))
        else:
            p.current.append(section)
    return p


def glossary_key(skel: Skeleton) -> str:
    """Distinct equations of the narrated document, sorted — prose edits don't move it."""
    equations = set()
    for section in skel.sections:
        if section.skip:
            continue
        for match in re.finditer(r"\[MATH \d+; TeX(?: display)?\] (.*?) \[/MATH\]", section.text, re.S):
            equations.add(match.group(1))
    return _sha("\n".join(sorted(equations)))


# ----------------------------------------------------------------------------- running
def run(skel: Skeleton, out_dir: str, model: str = DEFAULT_MODEL, force: bool = False,
        only: Optional[set] = None, dry_run: bool = False, workers: int = 4,
        reasoning: str = "medium", log=print) -> Plan:
    p = plan(skel, out_dir, force=force, only=only)
    log("%s -> %s" % (skel.title, out_dir))
    log("plan: " + p.summary())
    for section, reason in p.generate:
        log("  generate  %-40s %s" % (section.id, reason))
    for section, path in p.stale:
        log("  STALE     %-40s edited by hand, source changed -> draft goes to .new.md" % (
            section.id if section else "glossary"))
    if dry_run:
        return p

    macros = macros_from_mathjax_config(MATHJAX_CONFIG)
    gpath = os.path.join(out_dir, "glossary.md")
    gmeta, glossary = read_md(gpath)
    if p.glossary:
        log("glossary: generating (%s)" % p.glossary)
        glossary = llm.chat(GLOSSARY_SYSTEM, glossary_user(skel.title, glossary_source(skel), macros),
                            model=model, max_tokens=4000, reasoning="low")
        write_md(gpath, {
            "document": skel.title, "url": skel.url, "source": glossary_key(skel),
            "prompt": PROMPT_VERSION, "model": model, "generated": _today(), "body": _sha(glossary),
        }, glossary)
    total = len([s for s in skel.sections if not s.skip])
    order = {s.id: i for i, s in enumerate([s for s in skel.sections if not s.skip], 1)}

    def generate(item: tuple) -> tuple:
        section, reason = item
        user = section_user(skel.title, order[section.id], total, section, glossary, macros)
        script = llm.chat(LECTURE_SYSTEM, user, model=model, max_tokens=8000, reasoning=reasoning)
        return section, script

    def draft_is_current(section: Section) -> bool:
        meta, body = read_md(os.path.join(out_dir, section.id + ".new.md"))
        return bool(body) and meta.get("source") == section.hash and meta.get("prompt") == PROMPT_VERSION

    targets = [(s, r) for s, r in p.generate]
    for s, _path in p.stale:
        if s is None:
            continue
        if draft_is_current(s):
            log("  stale     %-40s edited by hand; fresh draft already in %s.new.md" % (s.id, s.id))
        else:
            targets.append((s, "stale"))
    if targets:
        log("generating %d section(s) with %s, %d at a time" % (len(targets), model, workers))
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for section, script in pool.map(generate, targets):
            meta = {
                "section": section.id, "title": section.title, "kind": section.kind,
                "document": skel.title, "url": skel.url,
                "source": section.hash, "skeleton": SKELETON_VERSION,
                "prompt": PROMPT_VERSION, "model": model, "generated": _today(),
                "body": _sha(script), "words": len(script.split()),
            }
            path = os.path.join(out_dir, section.id + ".md")
            if any(s is section for s, _ in p.stale):
                write_md(os.path.join(out_dir, section.id + ".new.md"), meta, script)
                old_meta, old_body = read_md(path)
                old_meta["stale"] = "true"
                write_md(path, old_meta, old_body)
                log("  stale     %-40s kept your edit; fresh draft in %s.new.md" % (section.id, section.id))
            else:
                write_md(path, meta, script)
                log("  wrote     %-40s %d words" % (section.id, meta["words"]))

    write_index(skel, out_dir, model)
    log("tokens: %d in, %d out, %d calls" % (llm.USAGE["prompt"], llm.USAGE["completion"], llm.USAGE["calls"]))
    return p


def accept(skel: Skeleton, out_dir: str, ids: set, log=print) -> int:
    """Declare hand-edited scripts current for the page as it is now.

    Used after the page changed under a script you had edited: `source` is stamped with the
    section's current hash, `stale` is dropped, the `.new.md` draft is deleted. Your text is
    kept exactly, and stays protected (its body hash still differs from the generated one).
    """
    done = 0
    for section in skel.sections:
        if section.id not in ids:
            continue
        path = os.path.join(out_dir, section.id + ".md")
        meta, body = read_md(path)
        if not body:
            log("  %-40s no script to accept" % section.id)
            continue
        meta["source"] = section.hash
        meta["skeleton"] = SKELETON_VERSION
        meta.pop("stale", None)
        meta["accepted"] = _today()
        write_md(path, meta, body)
        draft = os.path.join(out_dir, section.id + ".new.md")
        if os.path.exists(draft):
            os.remove(draft)
        log("  accepted  %-40s now current for the page" % section.id)
        done += 1
    missing = ids - {s.id for s in skel.sections}
    for name in sorted(missing):
        log("  %-40s no such section" % name)
    write_index(skel, out_dir, meta.get("model", "") if done else "")
    return done


def write_index(skel: Skeleton, out_dir: str, model: str) -> None:
    entries = []
    for section in skel.sections:
        path = os.path.join(out_dir, section.id + ".md")
        meta, body = read_md(path)
        entries.append({
            "id": section.id, "title": section.title, "kind": section.kind, "level": section.level,
            "source": section.hash, "skip": section.skip,
            "file": section.id + ".md" if body else None,
            "current": bool(body) and meta.get("source") == section.hash and meta.get("stale") != "true",
            "edited": bool(body) and meta.get("body") not in ("", None) and meta.get("body") != _sha(body),
            "words": section.words, "math": section.math,
        })
    index = {
        "url": skel.url, "title": skel.title, "lang": skel.lang, "hash": skel.hash,
        "skeleton": SKELETON_VERSION, "prompt": PROMPT_VERSION, "model": model,
        "updated": _today(), "sections": entries,
    }
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2)


def assemble(skel: Skeleton, out_dir: str) -> str:
    """The whole lecture in reading order, from whatever scripts exist — for review."""
    parts = []
    for section in skel.sections:
        if section.skip:
            continue
        meta, body = read_md(os.path.join(out_dir, section.id + ".md"))
        flag = ""
        if not body:
            flag = " (no script yet)"
        elif meta.get("stale") == "true":
            flag = " (STALE — edited, source changed)"
        elif meta.get("source") != section.hash:
            flag = " (out of date)"
        parts.append("## %s%s\n\n%s" % (section.title, flag, body.strip() if body else ""))
    return "\n\n".join(parts) + "\n"
