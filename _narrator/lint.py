"""
A deterministic check on lecture scripts, for the two rules a script can break in a way a
pattern can see:

- the lecture is heard, not seen, so a script never speaks a typographical mark or carries
  TeX (principle 1 in prompts.LECTURE_SYSTEM);
- a paragraph never ends inside a sentence. The voice stage synthesises one paragraph per
  call with a pause between, so "… is defined by ¶ n factorial equals …" would be spoken
  as two utterances, the first with a falling, final intonation.

The model keeps to both almost always; this catches the rest, so that a slip is regenerated
(script.run retries a section once) or reported, instead of being synthesised.

Ambiguous grouping ("n times n minus one") is principle 2's job: it cannot be told apart
from a correct reading by pattern, so it is not checked here.

    python3 -m _narrator lint [_narration]     # every script; exit status 1 when anything is found
"""
from __future__ import annotations

import json
import os
import re
from typing import List, Tuple

SPOKEN_MARKS = re.compile(
    r"\b(dot dot dot|ellipsis|(?:open|close|left|right) (?:paren|parenthesis|bracket|brace)"
    r"|parenthes[ie]s|square brackets?|curly braces?|backslash|caret|underscore"
    r"|vertical bars?|comma|semicolon)\b", re.I)
TEX = re.compile(r"\\[A-Za-z]+|[\\^_{}$]")
SENTENCE_END = re.compile(r"[.!?][\"”’)\]]*$")


def problems(script: str) -> List[str]:
    """What a script gets wrong, each with a little context; [] when clean."""
    found = []
    for pattern, what in ((SPOKEN_MARKS, "spoken mark"), (TEX, "TeX")):
        for match in pattern.finditer(script):
            start, end = max(0, match.start() - 30), min(len(script), match.end() + 20)
            context = " ".join(script[start:end].split())
            found.append('%s "%s" in "…%s…"' % (what, match.group(0), context))
    paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n", script.strip()) if p.strip()]
    for paragraph, following in zip(paragraphs, paragraphs[1:]):
        if not SENTENCE_END.search(paragraph):
            found.append('paragraph ends inside a sentence: "…%s ¶ %s…"' % (paragraph[-30:], following[:25]))
    return found


def body_of(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end >= 0:
            return text[end + 5:]
    return text


def check_tree(root: str) -> List[Tuple[str, str]]:
    """(path, problem) for every section script under root that a post still reads — not
    glossaries, drafts, or files an index.json no longer lists (left from an old section id)."""
    out = []
    for directory, _dirs, files in os.walk(root):
        listed = None
        if "index.json" in files:
            with open(os.path.join(directory, "index.json"), encoding="utf-8") as handle:
                listed = {s["file"] for s in json.load(handle).get("sections", []) if s.get("file")}
        for name in sorted(files):
            if not name.endswith(".md") or name.endswith(".new.md") or name == "glossary.md":
                continue
            if listed is not None and name not in listed:
                continue
            path = os.path.join(directory, name)
            out.extend((path, problem) for problem in problems(body_of(path)))
    return out
