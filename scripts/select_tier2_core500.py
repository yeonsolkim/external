#!/usr/bin/env python3
"""Select and render the final Tier 2 Core 500 vocabulary document."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("tmp/tier2-selection/penalized-scores.jsonl")
DEFAULT_OVERRIDES = Path("scripts/tier2-final-selection-overrides.json")
DEFAULT_SOURCE = Path(
    "_posts/3. English/2. Vocabulary/2026-04-22-Tier 2 Words.md"
)
DEFAULT_POST = Path(
    "_posts/3. English/2. Vocabulary/2026-04-22-Tier 2 Words Core 500.md"
)
DEFAULT_OUTPUT_DIR = Path("tmp/tier2-selection")
TARGET_SIZE = 500


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-post", type=Path, default=DEFAULT_POST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_overrides(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    excluded = {
        headword.casefold(): item["reason"]
        for headword, item in payload.get("exclude_headwords", {}).items()
    }
    included = {
        entry_id: item["reason"]
        for entry_id, item in payload.get("include_entries", {}).items()
    }
    if not excluded or not included:
        raise ValueError("Stage 5 requires explicit exclusion and inclusion reviews")
    if any(not reason.strip() for reason in (*excluded.values(), *included.values())):
        raise ValueError("Every Stage 5 override requires a reason")
    return excluded, included


def ranked_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: row["adjusted_rank"])


def baseline_selection(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in ranked:
        key = row["headword"].casefold()
        if not row["resolved"] or row["adjusted_score"] <= 0 or key in seen:
            continue
        selected.append(row)
        seen.add(key)
        if len(selected) == TARGET_SIZE:
            break
    return selected


def final_selection(
    ranked: list[dict[str, Any]],
    excluded: dict[str, str],
    included: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    by_id = {row["entry_id"]: row for row in ranked}
    missing = sorted(set(included) - set(by_id))
    if missing:
        raise ValueError("Unknown forced-inclusion entry IDs: " + ", ".join(missing))

    selected_by_id: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    for entry_id, reason in included.items():
        row = by_id[entry_id]
        key = row["headword"].casefold()
        if not row["resolved"] or row["adjusted_score"] <= 0:
            raise ValueError(f"Ineligible forced inclusion: {entry_id}")
        if key in excluded:
            raise ValueError(f"Headword both included and excluded: {key}")
        if key in seen:
            raise ValueError(f"Forced inclusions repeat headword: {key}")
        enriched = dict(row)
        enriched["selection_reason"] = "editorial promotion"
        enriched["editorial_reason"] = reason
        selected_by_id[entry_id] = enriched
        seen.add(key)

    skipped_duplicates: list[dict[str, Any]] = []
    automatic_cutoff = 0
    for row in ranked:
        if len(selected_by_id) == TARGET_SIZE:
            break
        entry_id = row["entry_id"]
        key = row["headword"].casefold()
        if entry_id in selected_by_id:
            continue
        if not row["resolved"] or row["adjusted_score"] <= 0 or key in excluded:
            continue
        if key in seen:
            skipped_duplicates.append(row)
            continue
        enriched = dict(row)
        enriched["selection_reason"] = "adjusted score + unique headword"
        enriched["editorial_reason"] = ""
        selected_by_id[entry_id] = enriched
        seen.add(key)
        automatic_cutoff = row["adjusted_rank"]

    selected = sorted(selected_by_id.values(), key=lambda row: row["adjusted_rank"])
    for final_rank, row in enumerate(selected, start=1):
        row["final_rank"] = final_rank
    return selected, skipped_duplicates, automatic_cutoff


def validate(
    rows: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    excluded: dict[str, str],
    included: dict[str, str],
) -> None:
    if len(rows) != 2529:
        raise ValueError("Expected 2,529 scored source entries")
    if len(baseline) != TARGET_SIZE or len(selected) != TARGET_SIZE:
        raise ValueError("Both baseline and final selections must contain exactly 500 entries")
    if len({row["entry_id"] for row in selected}) != TARGET_SIZE:
        raise ValueError("Final selection contains duplicate entry IDs")
    if len({row["headword"].casefold() for row in selected}) != TARGET_SIZE:
        raise ValueError("Final selection must contain 500 unique headwords")
    if not all(row["resolved"] and row["adjusted_score"] > 0 for row in selected):
        raise ValueError("Final selection contains an unresolved or zero-score entry")
    if [row["final_rank"] for row in selected] != list(range(1, TARGET_SIZE + 1)):
        raise ValueError("Final ranks are not a complete 1-500 sequence")

    baseline_ids = {row["entry_id"] for row in baseline}
    selected_ids = {row["entry_id"] for row in selected}
    added = selected_ids - baseline_ids
    removed = baseline_ids - selected_ids
    if added != set(included):
        raise ValueError("Editorial inclusions do not exactly match additions to baseline")
    removed_headwords = {
        row["headword"].casefold() for row in baseline if row["entry_id"] in removed
    }
    if removed_headwords != set(excluded):
        raise ValueError("Editorial exclusions do not exactly match removals from baseline")
    if len(added) != len(removed):
        raise ValueError("Editorial swaps must preserve the target size")


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def entry_label(row: dict[str, Any]) -> str:
    sense = "" if row["sense_number"] is None else f"<sup>{row['sense_number']}</sup>"
    return f"<b>{row['headword_html']}</b>{sense}"


def render_post(selected: list[dict[str, Any]]) -> str:
    lines = [
        "---",
        "layout: post",
        'title: "Tier 2 Words: Core 500"',
        "date: 2026-04-22 00:00:00 +0900",
        "category_path:",
        "  - 3. English",
        "  - 2. Vocabulary",
        "created_at: 2026-08-11 00:00:00 +0900",
        "last_modified_at: 2026-08-11 00:00:00 +0900",
        "---",
        "",
        "> Selected from *Tier 2 Words* for B2-C1 general and academic reading.",
        "> The list is ordered by final importance rank and contains one representative meaning per headword.",
        "",
    ]
    for start in range(1, TARGET_SIZE + 1, 100):
        end = start + 99
        list_open = "<ol>" if start == 1 else f'<ol start="{start}">'
        lines.extend([f"## {start}-{end}", "", list_open])
        for row in selected[start - 1 : end]:
            lines.append(
                f"<li>{entry_label(row)} ({row['part_of_speech']}): "
                f"{row['definition_html']}</li>"
            )
        lines.extend(["</ol>", ""])
    return "\n".join(lines)


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_audit(
    rows: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    skipped_duplicates: list[dict[str, Any]],
    automatic_cutoff: int,
    excluded: dict[str, str],
    included: dict[str, str],
    source: Path,
    input_path: Path,
    override_path: Path,
    output_post: Path,
) -> str:
    by_id = {row["entry_id"]: row for row in rows}
    baseline_by_headword = {row["headword"].casefold(): row for row in baseline}
    scores = [row["adjusted_score"] for row in selected]
    pos_counts = Counter(row["part_of_speech"] for row in selected)
    promoted = [row for row in selected if row["entry_id"] in included]
    baseline_ids = {row["entry_id"] for row in baseline}
    selected_ids = {row["entry_id"] for row in selected}

    lines = [
        "# Tier 2 Words: Stage 5 Final Core 500 Audit",
        "",
        "## Outcome",
        "",
        f"- Final entries: {len(selected):,}",
        f"- Unique headwords: {len({row['headword'].casefold() for row in selected}):,}",
        f"- Resolved positive-score entries: {sum(row['resolved'] and row['adjusted_score'] > 0 for row in selected):,}",
        f"- Baseline/final overlap: {len(baseline_ids & selected_ids):,}",
        f"- Direct editorial swaps: {len(selected_ids - baseline_ids):,} promoted / {len(baseline_ids - selected_ids):,} removed",
        f"- Automatic adjusted-rank cutoff: {automatic_cutoff:,}",
        f"- Highest adjusted rank admitted by editorial promotion: {max(row['adjusted_rank'] for row in selected):,}",
        f"- Adjusted-score range: {min(scores):.2f}-{max(scores):.2f}; median={statistics.median(scores):.2f}",
        "- POS distribution: " + ", ".join(f"{pos}={count}" for pos, count in sorted(pos_counts.items())),
        f"- Duplicate candidates skipped during final automatic fill: {len(skipped_duplicates):,}",
        "",
        "## Selection policy",
        "",
        "1. Keep only resolved entries with a positive adjusted Stage 4 score.",
        "2. Reserve the directly reviewed high-transfer promotions.",
        "3. Fill remaining places in adjusted-score order, allowing one representative meaning per case-insensitive headword.",
        "4. Remove directly reviewed foundational, concrete, or narrow headwords across all of their source senses.",
        "5. Preserve adjusted-rank order in the final learning document and assign a new contiguous final rank 1-500.",
        "",
        "No duplicate-headword exception was used: the high-ranking duplicates were close",
        "part-of-speech conversions or meanings from the same teachable word family.",
        "",
        "## Provenance",
        "",
        f"- Source Markdown SHA-256: `{file_hash(source)}`",
        f"- Stage 4 JSONL SHA-256: `{file_hash(input_path)}`",
        f"- Stage 5 override SHA-256: `{file_hash(override_path)}`",
        f"- Final Core 500 Markdown SHA-256: `{file_hash(output_post)}`",
        "",
        "## Directly excluded headwords",
        "",
        "| Headword | Baseline entry | Adjusted rank | Score | Reason |",
        "|---|---|---:|---:|---|",
    ]
    for headword, reason in sorted(excluded.items()):
        row = baseline_by_headword[headword]
        lines.append(
            f"| {escape_cell(headword)} | {escape_cell(row['entry_id'])} | "
            f"{row['adjusted_rank']} | {row['adjusted_score']:.2f} | {escape_cell(reason)} |"
        )

    lines.extend(
        [
            "",
            "## Directly promoted entries",
            "",
            "| Entry | Adjusted rank | Score | Reason |",
            "|---|---:|---:|---|",
        ]
    )
    for row in promoted:
        lines.append(
            f"| {escape_cell(row['entry_id'])} | {row['adjusted_rank']} | "
            f"{row['adjusted_score']:.2f} | {escape_cell(included[row['entry_id']])} |"
        )

    lines.extend(
        [
            "",
            "## Automatic-fill duplicate skips",
            "",
            "| Skipped entry | Adjusted rank | Score | Retained entry |",
            "|---|---:|---:|---|",
        ]
    )
    retained_by_headword = {row["headword"].casefold(): row for row in selected}
    for row in skipped_duplicates:
        retained = retained_by_headword[row["headword"].casefold()]
        lines.append(
            f"| {escape_cell(row['entry_id'])} | {row['adjusted_rank']} | "
            f"{row['adjusted_score']:.2f} | {escape_cell(retained['entry_id'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_selection_data(selected: list[dict[str, Any]], output_dir: Path) -> None:
    jsonl_path = output_dir / "final-core500.jsonl"
    csv_path = output_dir / "final-core500.csv"
    with jsonl_path.open("w", encoding="utf-8") as stream:
        for row in selected:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    fields = [
        "final_rank",
        "adjusted_rank",
        "entry_id",
        "headword",
        "sense_number",
        "part_of_speech",
        "definition",
        "frequency_score",
        "genre_range_score",
        "tier2_fit_score",
        "learning_leverage_score",
        "sense_centrality_score",
        "pre_penalty_total",
        "total_penalty",
        "adjusted_score",
        "selection_reason",
        "editorial_reason",
        "source_line",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(selected)


def main() -> None:
    args = parse_args()
    rows = load_jsonl(args.input)
    ranked = ranked_rows(rows)
    excluded, included = load_overrides(args.overrides)
    baseline = baseline_selection(ranked)
    selected, skipped_duplicates, automatic_cutoff = final_selection(
        ranked, excluded, included
    )
    validate(rows, baseline, selected, excluded, included)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.output_post.parent.mkdir(parents=True, exist_ok=True)
    args.output_post.write_text(render_post(selected), encoding="utf-8")
    write_selection_data(selected, args.output_dir)
    audit = render_audit(
        rows,
        baseline,
        selected,
        skipped_duplicates,
        automatic_cutoff,
        excluded,
        included,
        args.source,
        args.input,
        args.overrides,
        args.output_post,
    )
    (args.output_dir / "final-selection-audit.md").write_text(
        audit, encoding="utf-8"
    )
    print(
        f"Selected {len(selected):,} unique Tier 2 entries; "
        f"wrote {args.output_post}"
    )


if __name__ == "__main__":
    main()
