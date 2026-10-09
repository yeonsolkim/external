"""
A deterministic check on lecture scripts, for the rules a script can break in a way a
pattern can see:

- the lecture is heard, not seen, so a script never speaks a typographical mark or carries
  TeX (principle 1 in prompts.LECTURE_SYSTEM);
- a paragraph never ends inside a sentence. The voice stage synthesises one paragraph per
  call with a pause between, so "… is defined by ¶ n factorial equals …" would be spoken
  as two utterances, the first with a falling, final intonation;
- a sentence that introduces a notation says the notation, not its term a second time:
  "the zero matrix, denoted by the zero matrix" leaves the listener without the symbol on
  the page. It shows as words after "denoted by", "denotes", "defined by", "is called" or
  "we write" that already occur earlier in the sentence, within one phrase, and hold a word
  other than the name of a mark: "the set B bar r of a, defined by B bar r of a" repeats a
  notation on purpose. ACCEPTED lists the repetitions that were heard and kept.

The model keeps to them almost always; this catches the rest, so that a slip is regenerated
(script.run retries a section once) or reported, instead of being synthesised.

Ambiguous grouping ("n times n minus one") is principle 2's job: it cannot be told apart
from a correct reading by pattern, so it is not checked here. Neither is a symbol read as the
concept it stands for without repeating words ("Let closure be a closure operator", "denoted
by A then B"): only its meaning tells it apart.

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
# A sentence that introduces a notation: the words after the trigger are the notation.
INTRODUCES = re.compile(r"\b(?:denoted by|denotes|defined by|is called|are called|we call|we write)\b", re.I)
PHRASE_BREAK = re.compile(r"[,;:()“”\"]")
# Words that do not make a repetition on their own: function words, numbers, and the names of
# the marks on a symbol ("A prime", "B bar r of a"). "The" is dropped before comparing.
NOT_CONTENT = frozenset((
    "a an and as at be by for in is of on or to with "
    "zero one two three four five six seven eight nine ten eleven twelve "
    "bar star prime hat tilde sub capital").split())
# Repetitions heard and kept on purpose, by a fragment of their sentence.
ACCEPTED = (
    # 1.1 Vector Spaces, Example 1.1.4: an equation for the zero function's values; "the zero
    # function of x" is the function applied to x, not a second name for it.
    "the zero function is defined by the zero function of x",
    # 1.3 Linear Combinations and Spans, Definition 1.3.2: span(S) is the word "span" itself,
    # so its notation cannot sound unlike its term.
    "the span of S is the set span of S, defined by span of S",
)


def _words(text: str) -> List[str]:
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w != "the"]


def _occurs(run: List[str], words: List[str]) -> bool:
    return any(words[i:i + len(run)] == run for i in range(len(words) - len(run) + 1))


def repeated_terms(script: str) -> List[Tuple[str, str]]:
    """(the words said again, context) for each sentence that says its term a second time
    where it introduces a notation; [] when none does."""
    found = []
    for sentence in re.split(r"(?<=[.!?])\s+", " ".join(script.split())):
        if any(fragment in sentence for fragment in ACCEPTED):
            continue
        for match in INTRODUCES.finditer(sentence):
            phrases = [_words(p) for p in PHRASE_BREAK.split(sentence[:match.start()])]
            after = _words(PHRASE_BREAK.split(sentence[match.end():])[0])
            for k in range(min(8, len(after)), 1, -1):
                run = after[:k]
                if all(len(w) < 3 or w in NOT_CONTENT for w in run):
                    continue
                if any(_occurs(run, words) for words in phrases):
                    context = sentence[max(0, match.start() - 80):match.end() + 40]
                    found.append(("%s %s" % (match.group(0), " ".join(run)), context))
                    break
    return found


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
    for said, context in repeated_terms(script):
        found.append('term said again for its notation, "%s", in "…%s…"' % (said, context))
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
