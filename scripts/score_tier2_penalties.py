#!/usr/bin/env python3
"""Apply Stage 4 penalties and audit multi-sense ranking consistency.

The script preserves the 100-point pre-penalty score from Stages 2 and 3,
records every deduction separately, and produces an adjusted ranking. It does
not create the final 500-entry Markdown document.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "tmp" / "tier2-selection" / "semantic-scores.jsonl"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp" / "tier2-selection"
DEFAULT_OVERRIDES = REPO_ROOT / "scripts" / "tier2-penalty-overrides.json"

NON_LEXICAL_POS = {
    "comb. form",
    "det.",
    "excl.",
    "p.",
    "pron.",
    "suff.",
    "unknown",
}
SCIENTIFIC_CONCRETE_LEXNAMES = {
    "noun.animal",
    "noun.body",
    "noun.plant",
    "noun.shape",
    "noun.substance",
}
TECHNICAL_CUE_PATTERNS = {
    "biomedical": re.compile(
        r"\b(?:anatomical|bacteria|bacterial|blood vessel|cell|disease|enzyme|"
        r"fetus|organ|protein|surgery|syndrome|tissue|virus)\b",
        re.IGNORECASE,
    ),
    "formal-science": re.compile(
        r"\b(?:atom|atomic|chemical|electron|equation|formula|molecule|neutron|"
        r"numerical quantity|proton|solid|theorem)\b",
        re.IGNORECASE,
    ),
    "language-science": re.compile(
        r"\b(?:grammatical|linguistic|phonetic|syllable|syntax)\b",
        re.IGNORECASE,
    ),
    "measurement-geometry": re.compile(
        r"\b(?:angle|axis|coordinate|diameter|measurement|radius|unit of)\b",
        re.IGNORECASE,
    ),
    "taxonomy": re.compile(r"\b(?:genus|species)\b", re.IGNORECASE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_overrides(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", {})
    if not isinstance(entries, dict):
        raise ValueError("Penalty override 'entries' must be an object")
    for entry_id, override in entries.items():
        if not isinstance(override, dict):
            raise ValueError(f"Override for {entry_id} must be an object")
        adjustment = override.get("adjustment")
        reason = override.get("reason")
        if not isinstance(adjustment, (int, float)) or not -30 <= adjustment <= 30:
            raise ValueError(f"Override for {entry_id} has invalid adjustment")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"Override for {entry_id} needs a reason")
    return entries


def sense_multiplier(sense_number: int | None) -> float:
    return {None: 1.0, 1: 1.0, 2: 0.65, 3: 0.45, 4: 0.35}.get(
        sense_number, 0.25
    )


def tier1_penalty(row: dict[str, Any]) -> tuple[float, list[str]]:
    rank = row["ngsl_rank"]
    zipf = float(row["wordfreq_zipf"])
    flags: list[str] = []
    base = 0.0

    if rank is not None:
        if rank <= 500:
            base = 16.0
            flags.append("NGSL-1-500")
        elif rank <= 1000:
            base = 12.0
            flags.append("NGSL-501-1000")
        elif rank <= 1500:
            base = 8.0
            flags.append("NGSL-1001-1500")
        elif rank <= 2000:
            base = 4.0
            flags.append("NGSL-1501-2000")

        if zipf >= 5.5:
            base += 4.0
            flags.append("zipf>=5.5")
        elif zipf >= 5.0:
            base += 3.0
            flags.append("zipf>=5.0")
        elif zipf >= 4.6:
            base += 2.0
            flags.append("zipf>=4.6")
    else:
        if zipf >= 5.5:
            base = 12.0
            flags.extend(["outside-NGSL", "zipf>=5.5"])
        elif zipf >= 5.0:
            base = 8.0
            flags.extend(["outside-NGSL", "zipf>=5.0"])
        elif zipf >= 4.6:
            base = 4.0
            flags.extend(["outside-NGSL", "zipf>=4.6"])

    multiplier = sense_multiplier(row["sense_number"])
    if base and multiplier < 1.0:
        flags.append(f"later-sense-x{multiplier:.2f}")
    return round(min(20.0, base * multiplier), 2), flags


def technical_cues(definition: str) -> list[str]:
    return [
        label for label, pattern in TECHNICAL_CUE_PATTERNS.items() if pattern.search(definition)
    ]


def specialization_penalty(
    row: dict[str, Any], cue_flags: list[str]
) -> tuple[float, list[str]]:
    explicit = set(row["domain_flags"])
    weak = set(row["weak_domain_flags"])
    penalty = 0.0
    flags: list[str] = []

    if "academic-discipline" in explicit:
        penalty = max(penalty, 14.0)
        flags.append("named-academic-discipline")
    other_explicit = explicit - {"academic-discipline"}
    if other_explicit:
        penalty = max(penalty, 10.0)
        flags.append("explicit-domain:" + ",".join(sorted(other_explicit)))
    if "technical" in weak:
        penalty = max(penalty, 6.0)
        flags.append("technical-register")
    if "law-government" in weak:
        penalty = max(penalty, 4.0)
        flags.append("legal-government-context")
    if "measurement" in weak:
        penalty = max(penalty, 6.0)
        flags.append("specialized-measurement")
    if cue_flags and (row["nawl_member"] or len(cue_flags) >= 2):
        penalty = max(penalty, 6.0)
        flags.append("technical-cues:" + ",".join(cue_flags))
    if (
        row["nawl_member"]
        and row["wordnet_lexname"] in SCIENTIFIC_CONCRETE_LEXNAMES
    ):
        penalty = max(penalty, 6.0)
        flags.append("NAWL-concrete-science")
    return penalty, flags


def register_penalty(row: dict[str, Any]) -> tuple[float, list[str]]:
    label = row["register_label"]
    if label == "historic-or-dialect":
        return 18.0, [label]
    if label == "marked-register":
        return 8.0, [label]
    if label == "formal-register":
        return 4.0, [label]
    return 0.0, []


def secondary_sense_penalty(row: dict[str, Any]) -> tuple[float, list[str]]:
    sense_number = row["sense_number"]
    penalty = {None: 0.0, 1: 0.0, 2: 3.0, 3: 7.0, 4: 10.0}.get(
        sense_number, 12.0
    )
    return penalty, ([f"source-sense-{sense_number}"] if penalty else [])


def data_quality_penalty(row: dict[str, Any]) -> tuple[float, list[str]]:
    if not row["resolved"]:
        return 100.0, ["unresolved-definition"]
    if row["part_of_speech"] in NON_LEXICAL_POS:
        return 15.0, [f"non-core-pos:{row['part_of_speech']}"]
    return 0.0, []


def apply_penalties(
    rows: list[dict[str, Any]], overrides: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    seen_overrides: set[str] = set()
    for source_row in rows:
        row = dict(source_row)
        cue_flags = technical_cues(row["definition"])
        tier1, tier1_flags = tier1_penalty(row)
        specialized, specialized_flags = specialization_penalty(row, cue_flags)
        register, register_flags = register_penalty(row)
        secondary, secondary_flags = secondary_sense_penalty(row)
        data_quality, data_flags = data_quality_penalty(row)

        override = overrides.get(row["entry_id"])
        manual_adjustment = 0.0
        manual_reason = None
        if override:
            seen_overrides.add(row["entry_id"])
            manual_adjustment = float(override["adjustment"])
            manual_reason = override["reason"].strip()

        components = {
            "tier1_basic": tier1,
            "specialized": specialized,
            "register": register,
            "secondary_sense": secondary,
            "data_quality": data_quality,
            "manual_adjustment": manual_adjustment,
        }
        total_penalty = round(
            min(100.0, max(0.0, sum(components.values()))), 2
        )
        adjusted = round(max(0.0, row["pre_penalty_total"] - total_penalty), 2)
        all_flags = [
            *tier1_flags,
            *specialized_flags,
            *register_flags,
            *secondary_flags,
            *data_flags,
        ]
        if manual_reason:
            all_flags.append("manual:" + manual_reason)

        row.update(
            {
                "technical_cue_flags": cue_flags,
                "penalty_components": components,
                "tier1_penalty": tier1,
                "specialization_penalty": specialized,
                "register_penalty": register,
                "secondary_sense_penalty": secondary,
                "data_quality_penalty": data_quality,
                "manual_penalty_adjustment": manual_adjustment,
                "manual_penalty_reason": manual_reason,
                "total_penalty": total_penalty,
                "adjusted_score": adjusted,
                "penalty_rationale_flags": all_flags,
            }
        )
        scored.append(row)

    unused = sorted(set(overrides) - seen_overrides)
    if unused:
        raise ValueError("Overrides reference unknown entry IDs: " + ", ".join(unused))
    return scored


def rank_entries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            -row["adjusted_score"],
            -row["pre_penalty_total"],
            row["entry_index"],
        ),
    )
    for rank, row in enumerate(ranked, start=1):
        row["adjusted_rank"] = rank

    by_headword: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_headword[row["headword"].casefold()].append(row)
    for headword_rows in by_headword.values():
        ordered = sorted(
            headword_rows,
            key=lambda row: (
                -row["adjusted_score"],
                -row["pre_penalty_total"],
                row["entry_index"],
            ),
        )
        for within_rank, row in enumerate(ordered, start=1):
            row["within_headword_rank"] = within_rank
            row["preferred_headword_entry"] = within_rank == 1
            row["headword_entry_count"] = len(ordered)
    return ranked


def quantiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    quartiles = statistics.quantiles(ordered, n=4, method="inclusive")
    return {
        "min": ordered[0],
        "q1": quartiles[0],
        "median": statistics.median(ordered),
        "q3": quartiles[2],
        "max": ordered[-1],
    }


def report_table(
    rows: Iterable[dict[str, Any]], start_rank: int = 1
) -> list[str]:
    lines = [
        "| Rank | Entry | POS | Raw | Tier 1 | Specialized | Register | Secondary | Other | Adjusted | Flags |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for rank, row in enumerate(rows, start=start_rank):
        sense = "" if row["sense_number"] is None else f"^{row['sense_number']}"
        other = row["data_quality_penalty"] + row["manual_penalty_adjustment"]
        flags = "; ".join(row["penalty_rationale_flags"])
        lines.append(
            f"| {rank} | {row['headword']}{sense} | {row['part_of_speech']} | "
            f"{row['pre_penalty_total']:.2f} | {row['tier1_penalty']:.2f} | "
            f"{row['specialization_penalty']:.2f} | {row['register_penalty']:.2f} | "
            f"{row['secondary_sense_penalty']:.2f} | {other:.2f} | "
            f"{row['adjusted_score']:.2f} | {flags} |"
        )
    return lines


def manual_adjustment_table(rows: Iterable[dict[str, Any]]) -> list[str]:
    lines = [
        "| Adjusted rank | Entry | POS | Adjustment | Total penalty | Adjusted score | Reason |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        sense = "" if row["sense_number"] is None else f"^{row['sense_number']}"
        reason = row["manual_penalty_reason"].replace("|", "\\|")
        lines.append(
            f"| {row['adjusted_rank']} | {row['headword']}{sense} | "
            f"{row['part_of_speech']} | {row['manual_penalty_adjustment']:+.2f} | "
            f"{row['total_penalty']:.2f} | {row['adjusted_score']:.2f} | {reason} |"
        )
    return lines


def sense_order_inversions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_headword: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["sense_number"] is not None:
            by_headword[row["headword"].casefold()].append(row)

    inversions: list[dict[str, Any]] = []
    for headword, headword_rows in by_headword.items():
        ordered_by_sense = sorted(headword_rows, key=lambda row: row["sense_number"])
        for earlier, later in zip(ordered_by_sense, ordered_by_sense[1:]):
            if later["adjusted_score"] > earlier["adjusted_score"]:
                inversions.append(
                    {
                        "headword": headword,
                        "earlier_entry_id": earlier["entry_id"],
                        "earlier_sense": earlier["sense_number"],
                        "earlier_score": earlier["adjusted_score"],
                        "later_entry_id": later["entry_id"],
                        "later_sense": later["sense_number"],
                        "later_score": later["adjusted_score"],
                        "difference": round(
                            later["adjusted_score"] - earlier["adjusted_score"], 2
                        ),
                    }
                )
    return sorted(inversions, key=lambda item: (-item["difference"], item["headword"]))


def build_report(rows: list[dict[str, Any]], ranked: list[dict[str, Any]]) -> str:
    resolved = [row for row in rows if row["resolved"]]
    adjusted_dist = quantiles([row["adjusted_score"] for row in resolved])
    pre_top500 = {
        row["entry_id"]
        for row in sorted(
            resolved,
            key=lambda row: (-row["pre_penalty_total"], row["entry_index"]),
        )[:500]
    }
    adjusted_top500 = {row["entry_id"] for row in ranked[:500]}
    displaced = pre_top500 - adjusted_top500
    promoted = adjusted_top500 - pre_top500
    inversions = sense_order_inversions(rows)
    top650_by_headword: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ranked[:650]:
        top650_by_headword[row["headword"].casefold()].append(row)
    repeated_top650 = {
        key: value for key, value in top650_by_headword.items() if len(value) > 1
    }

    component_counts = {
        field: sum(row[field] > 0 for row in rows)
        for field in (
            "tier1_penalty",
            "specialization_penalty",
            "register_penalty",
            "secondary_sense_penalty",
            "data_quality_penalty",
        )
    }
    manual_count = sum(row["manual_penalty_adjustment"] != 0 for row in rows)
    manual_rows = sorted(
        (row for row in rows if row["manual_penalty_adjustment"] != 0),
        key=lambda row: row["adjusted_rank"],
    )

    report = [
        "# Tier 2 Words: Stage 4 Penalty and Consistency Report",
        "",
        "Stage 4 subtracts explicit penalties from the 100-point pre-penalty score.",
        "This produces a review ranking but does **not** yet create the final 500-entry",
        "Markdown document.",
        "",
        "## Penalty rules",
        "",
        "- Tier 1/basic (0–20): NGSL rank bands plus a wordfreq boost. The penalty",
        "  is reduced for later senses because a basic headword may have a less-basic sense.",
        "- Specialized (0–14): named academic disciplines, explicit subject labels,",
        "  legal/technical contexts, and NAWL concrete-science signals.",
        "- Register (0, 4, 8, or 18): formal, marked, or historical/dialectal usage.",
        "- Secondary sense (0, 3, 7, or 10): source senses 1–4 respectively.",
        "- Data quality (0, 15, or 100): non-core lexical POS or unresolved definition.",
        "- Manual adjustment (-30 to +30): reasoned exceptions in the override file.",
        "",
        "## Validation summary",
        "",
        f"- Input/ranked entries: {len(rows):,}",
        f"- Resolved entries: {len(resolved):,}",
        f"- Tier 1/basic penalties: {component_counts['tier1_penalty']:,}",
        f"- Specialized penalties: {component_counts['specialization_penalty']:,}",
        f"- Register penalties: {component_counts['register_penalty']:,}",
        f"- Secondary-sense penalties: {component_counts['secondary_sense_penalty']:,}",
        f"- Data-quality penalties: {component_counts['data_quality_penalty']:,}",
        f"- Manual adjustments: {manual_count:,}",
        "- Adjusted-score distribution: "
        + ", ".join(f"{key}={value:.2f}" for key, value in adjusted_dist.items()),
        f"- Entries displaced from the pre-penalty top 500: {len(displaced):,}",
        f"- Entries promoted into the adjusted top 500: {len(promoted):,}",
        f"- Headwords represented more than once in adjusted top 650: {len(repeated_top650):,}",
        f"- Adjacent source-sense score inversions: {len(inversions):,}",
        "",
        "## Manual adjustments after direct review",
        "",
        "Positive adjustments add a penalty; negative adjustments reduce an automatic",
        "penalty where the source definition is broader than the heuristic signal.",
        "Every exception remains in the separate override file with its reason.",
        "",
        *manual_adjustment_table(manual_rows),
        "",
        "## Adjusted top 40 (audit view)",
        "",
        *report_table(ranked[:40]),
        "",
        "## Adjusted ranks 490–510 (final-stage boundary audit)",
        "",
        *report_table(ranked[489:510], start_rank=490),
        "",
        "## Largest sense-order inversions",
        "",
        "A later source sense can legitimately outrank an earlier sense when its POS is",
        "more frequent or broadly distributed. These rows are surfaced for human review,",
        "not automatically forced into source order.",
        "",
        "| Headword | Earlier sense | Earlier score | Later sense | Later score | Difference |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in inversions[:30]:
        report.append(
            f"| {item['headword']} | {item['earlier_sense']} | {item['earlier_score']:.2f} | "
            f"{item['later_sense']} | {item['later_score']:.2f} | {item['difference']:.2f} |"
        )
    report.extend(
        [
            "",
            "## Stage 5 handoff",
            "",
            "The final stage should review the adjusted high-score pool, enforce the chosen",
            "policy for repeated headwords, select exactly 500 entries, and render the new",
            "Markdown document together with a selection audit.",
            "",
        ]
    )
    return "\n".join(report)


def write_duplicate_audit(rows: list[dict[str, Any]], output_dir: Path) -> None:
    by_headword: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_headword[row["headword"].casefold()].append(row)

    path = output_dir / "duplicate-sense-audit.csv"
    fields = [
        "headword",
        "headword_entry_count",
        "entry_id",
        "sense_number",
        "part_of_speech",
        "definition",
        "adjusted_rank",
        "within_headword_rank",
        "preferred_headword_entry",
        "pre_penalty_total",
        "total_penalty",
        "adjusted_score",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for headword in sorted(by_headword):
            headword_rows = by_headword[headword]
            if len(headword_rows) < 2:
                continue
            for row in sorted(headword_rows, key=lambda item: item["within_headword_rank"]):
                writer.writerow({field: row.get(field) for field in fields})


def write_outputs(
    rows: list[dict[str, Any]], ranked: list[dict[str, Any]], output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "penalized-scores.jsonl"
    csv_path = output_dir / "penalized-scores.csv"
    report_path = output_dir / "penalty-report.md"

    with jsonl_path.open("w", encoding="utf-8") as stream:
        for row in sorted(rows, key=lambda item: item["entry_index"]):
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    fields = [
        "adjusted_rank",
        "entry_index",
        "entry_id",
        "headword",
        "sense_number",
        "part_of_speech",
        "definition",
        "source_line",
        "resolved",
        "objective_score",
        "semantic_score",
        "pre_penalty_total",
        "ngsl_rank",
        "nawl_member",
        "technical_cue_flags",
        "tier1_penalty",
        "specialization_penalty",
        "register_penalty",
        "secondary_sense_penalty",
        "data_quality_penalty",
        "manual_penalty_adjustment",
        "manual_penalty_reason",
        "total_penalty",
        "adjusted_score",
        "within_headword_rank",
        "preferred_headword_entry",
        "headword_entry_count",
        "penalty_rationale_flags",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in ranked:
            flat = dict(row)
            for field in ("technical_cue_flags", "penalty_rationale_flags"):
                flat[field] = json.dumps(flat[field], ensure_ascii=False)
            writer.writerow(flat)

    report_path.write_text(build_report(rows, ranked), encoding="utf-8")
    write_duplicate_audit(rows, output_dir)


def validate(rows: list[dict[str, Any]], ranked: list[dict[str, Any]]) -> None:
    if len(rows) != 2529 or len(ranked) != 2529:
        raise ValueError("Expected 2,529 Stage 4 rows")
    if len({row["entry_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate entry IDs in Stage 4 output")
    if {row["adjusted_rank"] for row in ranked} != set(range(1, 2530)):
        raise ValueError("Adjusted ranks are not a complete 1–2,529 sequence")
    for row in rows:
        if not 0.0 <= row["total_penalty"] <= 100.0:
            raise ValueError(f"{row['entry_id']}: total penalty out of range")
        if not 0.0 <= row["adjusted_score"] <= 100.0:
            raise ValueError(f"{row['entry_id']}: adjusted score out of range")
        expected = round(max(0.0, row["pre_penalty_total"] - row["total_penalty"]), 2)
        if row["adjusted_score"] != expected:
            raise ValueError(f"{row['entry_id']}: adjusted score mismatch")
        if not row["resolved"] and row["adjusted_score"] != 0.0:
            raise ValueError(f"{row['entry_id']}: unresolved entry survived")


def main() -> None:
    args = parse_args()
    rows = load_jsonl(args.input)
    overrides = load_overrides(args.overrides)
    penalized = apply_penalties(rows, overrides)
    ranked = rank_entries(penalized)
    validate(penalized, ranked)
    write_outputs(penalized, ranked, args.output_dir)
    print(f"Penalized and ranked {len(ranked):,} entries; outputs in {args.output_dir}")


if __name__ == "__main__":
    main()
