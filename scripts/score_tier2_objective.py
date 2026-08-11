#!/usr/bin/env python3
"""Add reproducible frequency and genre-range scores to Tier 2 entries.

Stage 2 intentionally does not judge whether a sense is Tier 1, Tier 2,
specialized, archaic, or central. Those semantic decisions belong to Stage 3.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterable

try:
    import nltk
    from nltk.corpus import brown
    from nltk.stem import WordNetLemmatizer
    from wordfreq import zipf_frequency
except ImportError as error:  # pragma: no cover - exercised by environment setup
    raise SystemExit(
        "Missing scoring dependencies. Install scripts/requirements-tier2.txt "
        "in a virtual environment before running this script."
    ) from error


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "tmp" / "tier2-selection" / "entries.jsonl"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp" / "tier2-selection"
DEFAULT_NLTK_DATA = DEFAULT_OUTPUT_DIR / "nltk_data"

BROWN_CATEGORIES = (
    "adventure",
    "belles_lettres",
    "editorial",
    "fiction",
    "government",
    "hobbies",
    "humor",
    "learned",
    "lore",
    "mystery",
    "news",
    "religion",
    "reviews",
    "romance",
    "science_fiction",
)
UNIVERSAL_TO_WORDNET = {
    "NOUN": "n",
    "VERB": "v",
    "ADJ": "a",
    "ADV": "r",
}
ENTRY_POS_TO_UNIVERSAL = {
    "n.": "NOUN",
    "v.": "VERB",
    "adj.": "ADJ",
    "adv.": "ADV",
}
ALL_POS = "ALL"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help="Stage 1 entries.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for objective score outputs",
    )
    parser.add_argument(
        "--nltk-data",
        type=Path,
        default=DEFAULT_NLTK_DATA,
        help="Directory containing Brown, WordNet, and universal tagset data",
    )
    return parser.parse_args()


def load_entries(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def empirical_percentiles(values_by_key: dict[str, float]) -> dict[str, float]:
    """Return tie-adjusted percentiles, with missing/zero values fixed at zero."""
    positive = sorted(value for value in values_by_key.values() if value > 0)
    if len(positive) < 2:
        return {key: 0.0 for key in values_by_key}

    bounds: dict[float, tuple[int, int]] = {}
    for index, value in enumerate(positive):
        if value not in bounds:
            bounds[value] = (index, index)
        else:
            bounds[value] = (bounds[value][0], index)

    result: dict[str, float] = {}
    denominator = len(positive) - 1
    for key, value in values_by_key.items():
        if value <= 0:
            result[key] = 0.0
            continue
        low, high = bounds[value]
        result[key] = ((low + high) / 2) / denominator
    return result


def candidate_lookups(entries: Iterable[dict[str, Any]]) -> set[tuple[str, str]]:
    lookups: set[tuple[str, str]] = set()
    for entry in entries:
        headword = entry["headword"].casefold()
        pos = ENTRY_POS_TO_UNIVERSAL.get(entry["part_of_speech"], ALL_POS)
        lookups.add((headword, pos))
    return lookups


def split_phrase(text: str) -> tuple[str, ...]:
    return tuple(part for part in text.casefold().replace("-", " ").split() if part)


def build_brown_index(
    entries: list[dict[str, Any]],
) -> tuple[
    dict[tuple[str, str], dict[str, int]],
    dict[str, dict[str, int]],
]:
    """Count candidate lemmas by Brown genre and matching lexical POS."""
    lookups = candidate_lookups(entries)
    single_lookups = {lookup for lookup in lookups if len(split_phrase(lookup[0])) == 1}
    phrase_lookups = {lookup for lookup in lookups if len(split_phrase(lookup[0])) > 1}
    counts: dict[tuple[str, str], dict[str, int]] = {
        lookup: {category: 0 for category in BROWN_CATEGORIES} for lookup in lookups
    }
    denominators: dict[str, dict[str, int]] = {
        pos: {category: 0 for category in BROWN_CATEGORIES}
        for pos in (*UNIVERSAL_TO_WORDNET, ALL_POS)
    }
    lemmatizer = WordNetLemmatizer()

    @lru_cache(maxsize=100_000)
    def lemmatize(token: str, universal_pos: str) -> str:
        wordnet_pos = UNIVERSAL_TO_WORDNET[universal_pos]
        return lemmatizer.lemmatize(token, wordnet_pos)

    for category in BROWN_CATEGORIES:
        tagged_sentences = brown.tagged_sents(categories=category, tagset="universal")
        for sentence in tagged_sentences:
            normalized_tokens = [token.casefold() for token, _ in sentence]
            for token, universal_pos in ((word.casefold(), pos) for word, pos in sentence):
                denominators[ALL_POS][category] += 1
                if universal_pos in UNIVERSAL_TO_WORDNET:
                    denominators[universal_pos][category] += 1
                    lemma = lemmatize(token, universal_pos)
                    lookup = (lemma, universal_pos)
                    if lookup in single_lookups:
                        counts[lookup][category] += 1

                fallback_lookup = (token, ALL_POS)
                if fallback_lookup in single_lookups:
                    counts[fallback_lookup][category] += 1

            for headword, pos in phrase_lookups:
                phrase = split_phrase(headword)
                width = len(phrase)
                occurrences = sum(
                    tuple(normalized_tokens[index : index + width]) == phrase
                    for index in range(len(normalized_tokens) - width + 1)
                )
                counts[(headword, pos)][category] += occurrences

    return counts, denominators


def dispersion_dp(counts: dict[str, int], denominators: dict[str, int]) -> float | None:
    """Compute deviation of proportions (DP); zero is perfectly even."""
    total_observed = sum(counts.values())
    total_denominator = sum(denominators.values())
    if total_observed == 0 or total_denominator == 0:
        return None
    return 0.5 * sum(
        abs((counts[category] / total_observed) - (denominators[category] / total_denominator))
        for category in BROWN_CATEGORIES
    )


def genre_metrics(
    counts: dict[str, int], denominators: dict[str, int]
) -> dict[str, float | int | None]:
    total = sum(counts.values())
    genres_present = sum(count > 0 for count in counts.values())
    coverage = genres_present / len(BROWN_CATEGORIES)
    dp = dispersion_dp(counts, denominators)
    evenness = 0.0 if dp is None else max(0.0, 1.0 - dp)
    reliability = min(1.0, math.log1p(total) / math.log1p(10)) if total else 0.0
    score = (15.0 * coverage) + (10.0 * evenness * reliability)
    return {
        "brown_total_occurrences": total,
        "brown_genres_present": genres_present,
        "brown_genre_coverage": round(coverage, 6),
        "brown_dispersion_dp": None if dp is None else round(dp, 6),
        "brown_genre_evenness": round(evenness, 6),
        "brown_sample_reliability": round(reliability, 6),
        "genre_range_score": round(score, 2),
    }


def score_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    all_headwords = sorted({entry["headword"].casefold() for entry in entries})
    resolved_headwords = {
        entry["headword"].casefold() for entry in entries if entry["resolved"]
    }
    zipf_by_headword = {
        headword: float(zipf_frequency(headword, "en", wordlist="large"))
        for headword in all_headwords
    }
    frequency_percentiles = empirical_percentiles(
        {headword: zipf_by_headword[headword] for headword in resolved_headwords}
    )
    brown_counts, brown_denominators = build_brown_index(entries)

    scored: list[dict[str, Any]] = []
    for entry in entries:
        row = dict(entry)
        headword = entry["headword"].casefold()
        universal_pos = ENTRY_POS_TO_UNIVERSAL.get(entry["part_of_speech"], ALL_POS)
        lookup = (headword, universal_pos)
        zipf = zipf_by_headword.get(headword, 0.0)
        percentile = frequency_percentiles.get(headword, 0.0)
        frequency_score = round(25.0 * percentile, 2) if entry["resolved"] else 0.0
        metrics = genre_metrics(brown_counts[lookup], brown_denominators[universal_pos])
        if not entry["resolved"]:
            metrics["genre_range_score"] = 0.0
        genre_score = float(metrics["genre_range_score"])

        row.update(
            {
                "objective_eligible": bool(entry["resolved"]),
                "wordfreq_zipf": round(zipf, 2),
                "frequency_percentile": round(percentile, 6),
                "frequency_score": frequency_score,
                "brown_lookup_pos": universal_pos,
                "brown_genre_counts": brown_counts[lookup],
                **metrics,
                "objective_score": round(frequency_score + genre_score, 2),
            }
        )
        scored.append(row)
    return scored


def quantile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def build_report(scored: list[dict[str, Any]]) -> str:
    resolved = [row for row in scored if row["objective_eligible"]]
    unique_for_ranking: dict[tuple[str, str], dict[str, Any]] = {}
    for row in resolved:
        key = (row["headword"].casefold(), row["part_of_speech"])
        unique_for_ranking.setdefault(key, row)
    ranked = sorted(
        unique_for_ranking.values(),
        key=lambda row: (-row["objective_score"], row["headword"], row["part_of_speech"]),
    )
    objective_values = [float(row["objective_score"]) for row in resolved]
    zero_zipf = {row["headword"].casefold() for row in resolved if row["wordfreq_zipf"] == 0}
    zero_brown = sum(row["brown_total_occurrences"] == 0 for row in resolved)
    pos_scores: dict[str, list[float]] = defaultdict(list)
    for row in resolved:
        pos_scores[row["part_of_speech"]].append(float(row["objective_score"]))

    lines = [
        "# Tier 2 Words: Stage 2 Objective Score Report",
        "",
        "This report covers the 50 objective points only. It does not yet decide whether",
        "an entry is Tier 1, Tier 2, specialized, archaic, or a secondary sense.",
        "",
        "## Data sources",
        "",
        f"- `wordfreq` {version('wordfreq')}: blended English Zipf frequency from seven text domains.",
        f"- NLTK {nltk.__version__} Brown Corpus: 1,161,192 tokens in 15 labeled genres.",
        "- NLTK WordNet lemmatization and universal POS mapping for nouns, verbs, adjectives, and adverbs.",
        "",
        "## Scoring formula",
        "",
        "- Frequency (0–25): tie-adjusted empirical percentile of `wordfreq` Zipf frequency × 25.",
        "- Genre coverage (0–15): number of Brown genres containing the POS-matched lemma ÷ 15 × 15.",
        "- Genre evenness (0–10): `(1 − DP) × sample reliability × 10`.",
        "- Objective score (0–50): frequency + genre range.",
        "- Unresolved entries remain in the audit data but receive 0 objective points.",
        "",
        "The sample reliability factor is `min(1, log(1 + occurrences) / log(11))`,",
        "which prevents a word seen only once or twice from receiving a large evenness score.",
        "",
        "## Coverage and distribution",
        "",
        f"- Scored entries: {len(resolved)}",
        f"- Distinct scored headword/POS pairs: {len(unique_for_ranking)}",
        f"- Headwords absent from `wordfreq`: {len(zero_zipf)}",
        f"- Entries absent from the Brown Corpus after POS matching: {zero_brown}",
        f"- Objective score minimum: {min(objective_values):.2f}",
        f"- Objective score Q1: {quantile(objective_values, 0.25):.2f}",
        f"- Objective score median: {statistics.median(objective_values):.2f}",
        f"- Objective score Q3: {quantile(objective_values, 0.75):.2f}",
        f"- Objective score maximum: {max(objective_values):.2f}",
        "",
        "## Mean objective score by part of speech",
        "",
    ]
    lines.extend(
        f"- `{pos}`: {statistics.mean(values):.2f} ({len(values)} entries)"
        for pos, values in sorted(pos_scores.items(), key=lambda item: (-len(item[1]), item[0]))
    )

    lines.extend(
        [
            "",
            "## Highest objective scores (not final selections)",
            "",
            "| Rank | Entry | POS | Zipf | Genres | Frequency | Range | Total |",
            "|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for rank, row in enumerate(ranked[:30], start=1):
        lines.append(
            f"| {rank} | {row['headword']} | {row['part_of_speech']} | "
            f"{row['wordfreq_zipf']:.2f} | {row['brown_genres_present']}/15 | "
            f"{row['frequency_score']:.2f} | {row['genre_range_score']:.2f} | "
            f"{row['objective_score']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Brown is small and historically dated, so rare modern words may receive a low range score.",
            "- `wordfreq` is contemporary through approximately 2021 but does not expose separate source scores.",
            "- `wordfreq` is word-form based and does not distinguish parts of speech or senses.",
            "- Multiword frequency estimates can be noisy; these entries require semantic review.",
            "- High objective scores naturally favor Tier 1 words. Stage 3 and later penalties must correct this.",
            "",
            "## Attribution",
            "",
            "- Robyn Speer, `wordfreq` 3.0, Zenodo DOI 10.5281/zenodo.7199437.",
            "- Brown University Standard Corpus of Present-Day American English, distributed through NLTK Data.",
            "",
        ]
    )
    return "\n".join(lines)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            stream.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "entry_index",
        "entry_id",
        "headword",
        "sense_number",
        "part_of_speech",
        "definition",
        "resolved",
        "objective_eligible",
        "wordfreq_zipf",
        "frequency_percentile",
        "frequency_score",
        "brown_lookup_pos",
        "brown_total_occurrences",
        "brown_genres_present",
        "brown_genre_coverage",
        "brown_dispersion_dp",
        "brown_genre_evenness",
        "brown_sample_reliability",
        "genre_range_score",
        "objective_score",
        *[f"brown_{category}" for category in BROWN_CATEGORIES],
        "source_line",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            flat = {key: row.get(key) for key in fields}
            for category in BROWN_CATEGORIES:
                flat[f"brown_{category}"] = row["brown_genre_counts"][category]
            writer.writerow(flat)


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    nltk_data = args.nltk_data.resolve()
    os.environ["NLTK_DATA"] = str(nltk_data)
    if str(nltk_data) not in nltk.data.path:
        nltk.data.path.insert(0, str(nltk_data))

    output_dir.mkdir(parents=True, exist_ok=True)
    entries = load_entries(input_path)
    scored = score_entries(entries)
    jsonl_path = output_dir / "objective-scores.jsonl"
    csv_path = output_dir / "objective-scores.csv"
    report_path = output_dir / "objective-report.md"
    write_jsonl(jsonl_path, scored)
    write_csv(csv_path, scored)
    report_path.write_text(build_report(scored), encoding="utf-8")

    print(f"Scored {sum(row['objective_eligible'] for row in scored)} entries")
    print(f"JSONL: {jsonl_path}")
    print(f"CSV: {csv_path}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
