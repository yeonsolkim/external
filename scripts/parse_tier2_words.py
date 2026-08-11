#!/usr/bin/env python3
"""Parse the Tier 2 vocabulary post into auditable structured data.

This script performs no ranking or selection. It preserves each dictionary
entry, its source line, its sense number, and the synonym-group boundaries in
the Markdown source so later scoring steps can be reproduced.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    REPO_ROOT
    / "_posts"
    / "3. English"
    / "2. Vocabulary"
    / "2026-04-22-Tier 2 Words.md"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp" / "tier2-selection"

DEFINED_ENTRY_RE = re.compile(
    r"^<b>(?P<headword>.+?)</b>"
    r"(?:<sup>(?P<sense>\d+)</sup>)? "
    r"\((?P<pos>[^)]+)\): (?P<definition>.*?)<br>$"
)
UNRESOLVED_ENTRY_RE = re.compile(
    r"^<b>(?P<headword>.+?)</b>"
    r"(?:<sup>(?P<sense>\d+)</sup>)? "
    r"\((?P<pos>[^)]+)\)\.<br>$"
)
UNRESOLVED_HEADING = "<b>Unresolved entries (blank definitions)</b><br>"


@dataclass(frozen=True)
class Entry:
    entry_index: int
    entry_id: str
    headword: str
    headword_html: str
    sense_number: int | None
    part_of_speech: str
    definition: str
    definition_html: str
    resolved: bool
    group_index: int
    source_line: int
    raw_html: str


@dataclass(frozen=True)
class ParseResult:
    entries: list[Entry]
    unexpected_lines: list[tuple[int, str]]
    front_matter_lines: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Tier 2 Markdown source (default: repository vocabulary post)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for entries.jsonl and parse-report.md",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero if any non-entry body line is not recognized",
    )
    return parser.parse_args()


def split_front_matter(lines: list[str]) -> tuple[int, list[tuple[int, str]]]:
    """Return the front-matter line count and numbered body lines."""
    if not lines or lines[0].strip() != "---":
        return 0, list(enumerate(lines, start=1))

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start = index + 1
            return body_start, list(enumerate(lines[body_start:], start=body_start + 1))

    raise ValueError("Opening YAML front matter has no closing '---' delimiter")


def make_entry_id(headword: str, sense_number: int | None, part_of_speech: str) -> str:
    sense = str(sense_number) if sense_number is not None else "0"
    normalized = re.sub(r"[^a-z0-9]+", "-", headword.casefold()).strip("-")
    pos = re.sub(r"[^a-z0-9]+", "-", part_of_speech.casefold()).strip("-")
    return f"{normalized}--{sense}--{pos}"


def parse_source(source: Path) -> ParseResult:
    lines = source.read_text(encoding="utf-8").splitlines()
    front_matter_lines, body_lines = split_front_matter(lines)

    entries: list[Entry] = []
    unexpected_lines: list[tuple[int, str]] = []
    group_index = 1
    group_has_entry = False

    for line_number, raw_line in body_lines:
        line = raw_line.strip()
        if not line:
            continue
        if line == "<br>":
            if group_has_entry:
                group_index += 1
                group_has_entry = False
            continue
        if line == UNRESOLVED_HEADING:
            continue

        match = DEFINED_ENTRY_RE.fullmatch(line)
        resolved = True
        if match is None:
            match = UNRESOLVED_ENTRY_RE.fullmatch(line)
            resolved = False
        if match is None:
            unexpected_lines.append((line_number, raw_line))
            continue

        headword_html = match.group("headword")
        sense_text = match.group("sense")
        part_of_speech = match.group("pos").strip()
        definition_html = match.groupdict().get("definition") or ""
        headword = html.unescape(headword_html).strip()
        definition = html.unescape(definition_html).strip()
        sense_number = int(sense_text) if sense_text is not None else None

        entries.append(
            Entry(
                entry_index=len(entries) + 1,
                entry_id=make_entry_id(headword, sense_number, part_of_speech),
                headword=headword,
                headword_html=headword_html,
                sense_number=sense_number,
                part_of_speech=part_of_speech,
                definition=definition,
                definition_html=definition_html,
                resolved=resolved,
                group_index=group_index,
                source_line=line_number,
                raw_html=line,
            )
        )
        group_has_entry = True

    return ParseResult(entries, unexpected_lines, front_matter_lines)


def duplicate_ids(entries: Iterable[Entry]) -> dict[str, list[int]]:
    lines_by_id: dict[str, list[int]] = defaultdict(list)
    for entry in entries:
        lines_by_id[entry.entry_id].append(entry.source_line)
    return {key: lines for key, lines in lines_by_id.items() if len(lines) > 1}


def numbered_sense_anomalies(entries: Iterable[Entry]) -> tuple[list[str], list[str]]:
    senses_by_headword: dict[str, set[int]] = defaultdict(set)
    has_unnumbered: set[str] = set()
    for entry in entries:
        key = entry.headword.casefold()
        if entry.sense_number is None:
            has_unnumbered.add(key)
        else:
            senses_by_headword[key].add(entry.sense_number)

    gaps: list[str] = []
    for headword, senses in sorted(senses_by_headword.items()):
        expected = set(range(1, max(senses) + 1))
        if senses != expected:
            gaps.append(f"{headword}: {sorted(senses)}")

    mixed = sorted(set(senses_by_headword) & has_unnumbered)
    return gaps, mixed


def format_list(items: list[str], empty_message: str = "None") -> list[str]:
    if not items:
        return [f"- {empty_message}"]
    return [f"- {item}" for item in items]


def build_report(source: Path, source_hash: str, result: ParseResult) -> str:
    entries = result.entries
    resolved = [entry for entry in entries if entry.resolved]
    unresolved = [entry for entry in entries if not entry.resolved]
    unique_headwords = {entry.headword.casefold() for entry in entries}
    numbered = [entry for entry in entries if entry.sense_number is not None]
    pos_counts = Counter(entry.part_of_speech for entry in entries)
    duplicates = duplicate_ids(entries)
    gaps, mixed = numbered_sense_anomalies(entries)

    report = [
        "# Tier 2 Words: Stage 1 Parse Report",
        "",
        "This report describes parsing and source-data quality only. No importance scores",
        "or vocabulary selections have been applied.",
        "",
        "## Source",
        "",
        f"- Path: `{source}`",
        f"- SHA-256: `{source_hash}`",
        f"- YAML front-matter lines: {result.front_matter_lines}",
        "",
        "## Counts",
        "",
        f"- Parsed entries: {len(entries)}",
        f"- Entries with definitions: {len(resolved)}",
        f"- Unresolved entries: {len(unresolved)}",
        f"- Unique headwords: {len(unique_headwords)}",
        f"- Entries with numbered senses: {len(numbered)}",
        f"- Synonym groups: {max((entry.group_index for entry in entries), default=0)}",
        f"- Unexpected nonblank body lines: {len(result.unexpected_lines)}",
        f"- Duplicate entry IDs: {len(duplicates)}",
        "",
        "## Parts of speech",
        "",
    ]
    report.extend(f"- `{pos}`: {count}" for pos, count in pos_counts.most_common())

    report.extend(["", "## Unresolved entries", ""])
    report.extend(
        format_list(
            [
                f"`{entry.headword}` (`{entry.part_of_speech}`), source line {entry.source_line}"
                for entry in unresolved
            ]
        )
    )

    report.extend(["", "## Duplicate entry IDs", ""])
    report.extend(
        format_list(
            [f"`{entry_id}`: source lines {', '.join(map(str, lines))}" for entry_id, lines in sorted(duplicates.items())]
        )
    )

    report.extend(["", "## Numbered-sense gaps", ""])
    report.append(
        "A gap is informational, not necessarily an error: the source may intentionally include only a selected dictionary sense."
    )
    report.append("")
    report.extend(format_list(gaps))

    report.extend(["", "## Mixed numbered and unnumbered headwords", ""])
    report.extend(format_list([f"`{headword}`" for headword in mixed]))

    report.extend(["", "## Unexpected body lines", ""])
    report.extend(
        format_list(
            [f"Line {line_number}: `{line}`" for line_number, line in result.unexpected_lines]
        )
    )
    report.append("")
    return "\n".join(report)


def write_outputs(source: Path, output_dir: Path, result: ParseResult) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    entries_path = output_dir / "entries.jsonl"
    report_path = output_dir / "parse-report.md"

    with entries_path.open("w", encoding="utf-8") as stream:
        for entry in result.entries:
            stream.write(json.dumps(asdict(entry), ensure_ascii=False, sort_keys=True))
            stream.write("\n")

    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    report_path.write_text(build_report(source, source_hash, result), encoding="utf-8")

    print(f"Parsed {len(result.entries)} entries")
    print(f"Structured data: {entries_path}")
    print(f"Parse report: {report_path}")


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output_dir = args.output_dir.resolve()
    result = parse_source(source)
    write_outputs(source, output_dir, result)
    if args.strict and result.unexpected_lines:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
