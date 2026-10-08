#!/usr/bin/env python3
"""
Spell-check the posts (file names, titles and text) against the macOS spelling dictionary.

    python3 scripts/check_spelling.py               every word the dictionary lacks
    python3 scripts/check_spelling.py --state FILE  only the words FILE has not recorded for
                                                    that post, which it then records
    ... --report PAGE [--note TEXT]                 the same, also as an HTML page: by post,
                                                    each word in its sentence (written only
                                                    when there is something to show)

Only prose is read: math (with what is attached to it: $n$th, $n$-ary), code, HTML, Liquid,
link targets and pronunciations (between slashes, /mi/, or written in IPA) are left out.
scripts/site.zsh runs it with --state and --report, so a word is reported once per post:
while the post keeps it, later runs pass. A renamed file counts as a new post. Words in the
macOS user dictionary (Learn Spelling; scripts/learn_spelling.py teaches it a list) always
pass.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
import html
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable
from urllib.parse import quote
import unicodedata

from sync_posts_front_matter import DATE_PREFIX_RE, FRONT_MATTER_RE, POSTS_ROOT, post_paths, top_level_entry


# What is not prose, blanked out in this order before the words are taken.
NOT_PROSE = [
    re.compile(r"^(`{3,}|~{3,}).*?^\1", re.M | re.S),  # fenced code
    re.compile(r"<!--.*?-->", re.S),
    re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)", re.S),  # display math, and LaTeX's delimiters
    re.compile(r"\\begin\{([A-Za-z*]+)\}.*?\\end\{\1\}", re.S),
    re.compile(r"\$[^$\n]*\$(?:-?[*_]*[^\W\d_]+)?"),  # inline math with what is attached: $n$th, $n$-*th*
    re.compile(r"`[^`\n]*`"),
    re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.S),  # Liquid
    re.compile(r"</?[A-Za-z][^<>\n]*>"),  # HTML tags; the text between them stays
    re.compile(r"\]\([^)\n]*\)|https?://\S+|\{:[^}\n]*\}"),  # link targets, URLs, kramdown attributes
    re.compile(r"\\[A-Za-z]+|&#?\w+;"),  # LaTeX commands, HTML entities
    re.compile(r"(?<![\w/])/(?=[^\s/])[^/\n]{1,80}?(?<=[^\s/])/(?![\w/])"),  # /mi/, but not and/or
    re.compile(r"[^\s|]*[\u0250-\u02ff][^\s|]*"),  # anything written in IPA, up to a space or table pipe
]
NOT_NEWLINE_RE = re.compile(r"[^\n]")
WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*")
MARKUP_RE = re.compile(r"</?[A-Za-z][^<>\n]*>|\*+|^#+\s*")  # left out of the lines the page quotes

# NSSpellChecker through JavaScript for Automation: prints each word that neither US nor
# British English accepts, followed by the checker's guesses, tab-separated.
SPELL_CHECK_JS = r"""
ObjC.import('AppKit');
function run(words) {
  const checker = $.NSSpellChecker.sharedSpellChecker;
  const rejected = word => ['en', 'en_GB'].every(language =>
    checker.checkSpellingOfStringStartingAtLanguageWrapInSpellDocumentWithTagWordCount(
      $(word), 0, language, false, 0, null).length > 0);
  const guesses = word => {
    const found = checker.guessesForWordRangeInStringLanguageInSpellDocumentWithTag(
      $.NSMakeRange(0, word.length), $(word), 'en', 0);
    return Array.from({length: (found && found.count) || 0}, (_, i) => ObjC.unwrap(found.objectAtIndex(i)));
  };
  return words.filter(rejected).map(word => [word, ...guesses(word)].join('\t')).join('\n');
}
"""

PAGE_STYLE = """
:root { color-scheme: light dark; --text: #1d1d1f; --muted: #6e6e73; --page: #ffffff; --card: #f5f5f7;
        --rule: #e3e3e8; --link: #0066cc; --typo: #d70015; }
@media (prefers-color-scheme: dark) {
  :root { --text: #f5f5f7; --muted: #a1a1a6; --page: #1c1c1e; --card: #2c2c2e; --rule: #3a3a3c;
          --link: #4ea2ff; --typo: #ff6961; }
}
body { margin: 0; background: var(--page); color: var(--text);
       font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif; }
main { max-width: 760px; margin: 0 auto; padding: 32px 20px 48px; }
h1 { font-size: 22px; margin: 0; }
.meta { color: var(--muted); margin: 2px 0 0; }
.note { margin: 14px 0 22px; }
section { background: var(--card); border-radius: 12px; padding: 14px 18px; margin: 12px 0; }
section header { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; }
h2 { font-size: 17px; margin: 0; }
section header a { color: var(--link); font-size: 13px; text-decoration: none; white-space: nowrap; }
.path { color: var(--muted); font-size: 12px; margin: 2px 0 8px; }
ul { list-style: none; margin: 0; padding: 0; }
li { padding: 8px 0; border-top: 1px solid var(--rule); }
li:first-child { border-top: 0; }
.word { font-weight: 600; text-decoration: underline wavy var(--typo); text-underline-offset: 3px; }
.guesses { color: var(--muted); }
.where { color: var(--muted); font-size: 12px; }
.context { margin: 3px 0 0; color: var(--muted); font-size: 13px; overflow-wrap: anywhere; }
.context mark { background: none; color: var(--text); font-weight: 600; }
footer { color: var(--muted); font-size: 12px; margin-top: 24px; }
code { font: 12px ui-monospace, Menlo, monospace; }
"""


def prose(text: str) -> str:
    """text in NFC with everything that is not prose blanked out, so offsets stay where they were."""
    text = unicodedata.normalize("NFC", text)
    for pattern in NOT_PROSE:
        text = pattern.sub(lambda match: NOT_NEWLINE_RE.sub(" ", match.group()), text)
    return text


def is_word(token: str) -> bool:
    """Latin script, two letters or more, and nothing with a digit (2, 62nd)."""
    return len(token) > 1 and all(ch in "'’" or (ch.isalpha() and ord(ch) < 0x250) for ch in token)


def words_in(text: str) -> list[str]:
    """The words of the prose in text, in order."""
    return list(dict.fromkeys(token for token in WORD_RE.findall(prose(text)) if is_word(token)))


def title_and_body(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return "", text

    return " ".join(top_level_entry(match.group(1), "title")).partition(":")[2], text[match.end():]


def system_misspelled(words: list[str]) -> dict[str, list[str]]:
    if not words:
        return {}

    result = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", "-", *words],
        input=SPELL_CHECK_JS,
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=True,
    )
    misspelled: dict[str, list[str]] = {}
    for line in result.stdout.splitlines():
        if line:
            word, *guesses = line.split("\t")
            misspelled[word] = guesses

    return misspelled


def likely(guesses: list[str]) -> list[str]:
    return [guess for guess in guesses if "'" not in guess][:2]  # "Sequence's" is no help


def describe(word: str, guesses: list[str]) -> str:
    return word + (f" ({' '.join(guess + '?' for guess in likely(guesses))})" if likely(guesses) else "")


@dataclass
class Finding:
    """A post, with its words that the dictionary lacks and that were not reported before."""

    key: str  # the path under _posts
    path: Path
    name: str  # the file name without its date
    title: str
    body: str
    words: dict[str, list[str]] = field(default_factory=dict)  # each word with the checker's guesses

    def line(self) -> str:
        return ", ".join(describe(word, guesses) for word, guesses in self.words.items()) + f" in {self.name}"


def check(
    posts_root: Path,
    seen: dict[str, list[str]] | None,
    misspelled: Callable[[list[str]], dict[str, list[str]]] = system_misspelled,
) -> tuple[list[Finding], dict[str, list[str]]]:
    """Return the findings and the record: each post's words the dictionary lacks.

    Without seen every such word is found; with it, only those not recorded for the post."""
    posts: list[tuple[Finding, list[str]]] = []
    for path in post_paths(posts_root):
        key = unicodedata.normalize("NFC", path.relative_to(posts_root).as_posix())
        name = DATE_PREFIX_RE.sub("", Path(key).stem)
        title, body = title_and_body(path)
        words = list(dict.fromkeys(words_in(name) + words_in(title) + words_in(body)))
        posts.append((Finding(key, path, name, title, body), words))

    rejected = misspelled(sorted({word for _, words in posts for word in words}))
    findings: list[Finding] = []
    record: dict[str, list[str]] = {}
    for finding, words in posts:
        flagged = [word for word in words if word in rejected]
        if not flagged:
            continue

        record[finding.key] = flagged
        finding.words = {word: rejected[word] for word in flagged if word not in (seen or {}).get(finding.key, [])}
        if finding.words:
            findings.append(finding)

    return findings, record


# -- the page --------------------------------------------------------------------------------------
def in_context(text: str, match: re.Match, reach: int = 70) -> str:
    """The line around match, at most reach characters on either side, with the word marked."""
    line_start = text.rfind("\n", 0, match.start()) + 1
    line_end = text.find("\n", match.end())
    if line_end < 0:
        line_end = len(text)
    start = max(line_start, match.start() - reach)
    end = min(line_end, match.end() + reach)
    if start > line_start:  # cut between words, not inside one
        space = text.find(" ", start, match.start())
        if space >= 0:
            start = space + 1
    if end < line_end:
        space = text.rfind(" ", match.end(), end)
        if space >= 0:
            end = space
    before = ("…" if start > line_start else "") + text[start:match.start()]
    after = text[match.end():end] + ("…" if end < line_end else "")
    return f"{plain(before)}<mark>{html.escape(match.group())}</mark>{plain(after)}"


def plain(text: str) -> str:
    return html.escape(re.sub(r"\s+", " ", MARKUP_RE.sub("", text)))


def page_item(finding: Finding, word: str, guesses: list[str]) -> str:
    """A word: the checker's guesses, where it occurs, and the first line of the text that has it."""
    places, context = [], ""
    sources = (
        ("file name", finding.name),
        ("title", finding.title.strip().strip("'\"")),
        ("text", unicodedata.normalize("NFC", finding.body)),
    )
    for place, text in sources:
        hits = [match for match in WORD_RE.finditer(prose(text)) if match.group() == word]
        if not hits:
            continue

        places.append(place if len(hits) == 1 else f"{place}, {len(hits)} times")
        if place == "text" or not context:  # a line of the text says the most
            context = in_context(text, hits[0])

    guessed = f' <span class="guesses">→ {html.escape(" ".join(g + "?" for g in likely(guesses)))}</span>'
    return (
        f'<li><span class="word">{html.escape(word)}</span>{guessed if likely(guesses) else ""}'
        f' <span class="where">· {html.escape(", ".join(places))}</span>'
        f'<p class="context">{context}</p></li>'
    )


def page_section(finding: Finding) -> str:
    obsidian = "obsidian://open?path=" + quote(str(finding.path), safe="")
    folders = " › ".join(html.escape(folder) for folder in Path(finding.key).parent.parts)
    items = "\n".join(page_item(finding, word, guesses) for word, guesses in finding.words.items())
    return (
        f'<section>\n<header><h2>{html.escape(finding.name)}</h2>'
        f'<a href="{html.escape(obsidian)}">Open in Obsidian</a></header>\n'
        f'<p class="path">{folders}</p>\n<ul>\n{items}\n</ul>\n</section>'
    )


def report_page(findings: list[Finding], note: str = "") -> str:
    words = sum(len(finding.words) for finding in findings)
    meta = (
        f"{words} word{'' if words == 1 else 's'} in {len(findings)} post{'' if len(findings) == 1 else 's'}"
        f" · {datetime.now():%Y-%m-%d %H:%M}"
    )
    sections = "\n".join(page_section(finding) for finding in findings)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spelling</title>
<style>{PAGE_STYLE}</style>
</head>
<body>
<main>
<h1>Spelling</h1>
<p class="meta">{meta}</p>
{f'<p class="note">{html.escape(note)}</p>' if note else ''}
{sections}
<footer>A word that should pass everywhere belongs in the macOS user dictionary: use Learn
Spelling in any app, or add it to <code>scripts/spelling_words.txt</code> and run
<code>python3 scripts/learn_spelling.py</code>.</footer>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Spell-check the posts: file names, titles and text.")
    parser.add_argument(
        "--state",
        type=Path,
        help="report only the words this file has not recorded for a post, then record them",
    )
    parser.add_argument("--report", type=Path, help="also write what is found as this HTML page")
    parser.add_argument("--note", default="", help="a sentence for the top of the page")
    args = parser.parse_args()

    seen = None
    if args.state:
        try:
            seen = json.loads(args.state.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            seen = {}
        if not isinstance(seen, dict):
            seen = {}

    try:
        findings, record = check(POSTS_ROOT, seen)
    except subprocess.CalledProcessError as error:
        print(f"spelling check failed: {error.stderr.strip()}", file=sys.stderr)
        return 1
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"spelling check failed: {error}", file=sys.stderr)
        return 1

    if args.report and findings:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report_page(findings, args.note), encoding="utf-8")
    if args.state:
        args.state.parent.mkdir(parents=True, exist_ok=True)
        args.state.write_text(
            json.dumps(record, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
    if findings:
        print("\n".join(finding.line() for finding in findings))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
