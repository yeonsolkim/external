#!/usr/bin/env python3
"""Score Tier 2 fit, learning leverage, and sense centrality.

This is Stage 3 of the Tier 2 vocabulary selection workflow. It creates a
transparent semantic baseline; it does not apply the Stage 4 exclusion
penalties and does not make the final 500-word selection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

try:
    import nltk
    from nltk.corpus import wordnet as wn
except ImportError as error:  # pragma: no cover - environment setup guard
    raise SystemExit(
        "Missing scoring dependencies. Install scripts/requirements-tier2.txt "
        "in a virtual environment before running this script."
    ) from error


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "tmp" / "tier2-selection" / "objective-scores.jsonl"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp" / "tier2-selection"
DEFAULT_NLTK_DATA = DEFAULT_OUTPUT_DIR / "nltk_data"
DEFAULT_NGSL = DEFAULT_OUTPUT_DIR / "reference-data" / "NGSL_1.2_stats.csv"
DEFAULT_NAWL = (
    DEFAULT_OUTPUT_DIR
    / "reference-data"
    / "NAWL_1.2_lemmatized_for_research.csv"
)

POS_TO_WORDNET = {
    "n.": wn.NOUN,
    "v.": wn.VERB,
    "adj.": wn.ADJ,
    "adv.": wn.ADV,
}

ABSTRACT_LEXNAMES = {
    "noun.act",
    "noun.attribute",
    "noun.cognition",
    "noun.communication",
    "noun.event",
    "noun.feeling",
    "noun.group",
    "noun.motive",
    "noun.possession",
    "noun.quantity",
    "noun.relation",
    "noun.state",
    "noun.time",
    "verb.change",
    "verb.cognition",
    "verb.communication",
    "verb.creation",
    "verb.emotion",
    "verb.social",
    "verb.stative",
}
CONCRETE_LEXNAMES = {
    "noun.animal",
    "noun.artifact",
    "noun.body",
    "noun.food",
    "noun.location",
    "noun.object",
    "noun.person",
    "noun.plant",
    "noun.shape",
    "noun.substance",
}
ACTION_LEXNAMES = {
    "verb.body",
    "verb.competition",
    "verb.consumption",
    "verb.contact",
    "verb.motion",
    "verb.perception",
    "verb.possession",
    "verb.weather",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "one",
    "or",
    "someone",
    "something",
    "that",
    "the",
    "their",
    "to",
    "used",
    "with",
}

EXPLICIT_DOMAIN_PATTERNS = {
    "academic-discipline": r"\b(?:the study of|a branch of|the science of)\b",
    "anatomy": r"\b(?:anatomy|anatomical)\b",
    "astronomy": r"\b(?:astronomy|astronomical)\b",
    "biology": r"\b(?:biology|biological|botany|zoology)\b",
    "chemistry": r"\b(?:chemistry|chemical element|chemical compound)\b",
    "computing": r"\b(?:computing|computer programming|computer science)\b",
    "geology": r"\b(?:geology|geological)\b",
    "grammar": r"\b(?:grammar|grammatical|linguistics|linguistic)\b",
    "medicine": r"\b(?:medicine|medical|surgery|surgical)\b",
    "mathematics": r"\b(?:mathematics|mathematical|in maths?|in geometry|in algebra)\b",
    "physics": r"\b(?:physics|in mechanics|in electronics)\b",
    "specialist-sport": r"\b(?:baseball|cricket|golf|heraldry|hunting)\b",
    "taxonomy": r"\b(?:a species of|a genus of)\b",
}
WEAK_DOMAIN_PATTERNS = {
    "law-government": r"\b(?:law|legal|legislation|treaty|court)\b",
    "measurement": r"\b(?:unit of measurement|unit of weight|unit of length)\b",
    "technical": r"\b(?:technical|specialized)\b",
}
HISTORIC_REGISTER_RE = re.compile(
    r"(?:"
    r"^(?:archaic|dated|dialect|historical|obsolete|"
    r"(?:Irish|Scottish|West Indian) English)\b"
    r"|(?:^|[.;]\s*)\d+\s+(?:archaic|dated|dialect|historical|obsolete)\b"
    r")",
    re.IGNORECASE,
)
MARKED_REGISTER_RE = re.compile(
    r"(?:"
    r"^(?:informal|literary|humorous)\b"
    r"|\b(?:often\s+)?used\b[^.;)]{0,60}"
    r"\b(?:informally|humorously|humorous|literary)\b"
    r")",
    re.IGNORECASE,
)
TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--nltk-data", type=Path, default=DEFAULT_NLTK_DATA)
    parser.add_argument("--ngsl", type=Path, default=DEFAULT_NGSL)
    parser.add_argument("--nawl", type=Path, default=DEFAULT_NAWL)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_ngsl(path: Path) -> dict[str, int]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        ranks = {
            row["Lemma"].strip().casefold(): int(row["SFI Rank"])
            for row in reader
            if row.get("Lemma") and row.get("SFI Rank")
        }
    if len(ranks) != 2809:
        raise ValueError(f"Expected 2,809 NGSL lemmas, found {len(ranks):,}")
    return ranks


def decode_reference_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def load_nawl(path: Path) -> set[str]:
    lemmas: set[str] = set()
    for row in csv.reader(decode_reference_text(path).splitlines()):
        if row and row[0].strip():
            lemmas.add(row[0].strip().casefold())
    if not 950 <= len(lemmas) <= 970:
        raise ValueError(f"Expected roughly 957 NAWL lemmas, found {len(lemmas):,}")
    return lemmas


def normalize_wordnet_query(headword: str) -> str:
    return re.sub(r"[ -]+", "_", headword.casefold().strip())


def lookup_candidates(headword: str, wordnet_pos: str | None) -> list[str]:
    direct = headword.casefold().strip()
    candidates = [direct]
    query = normalize_wordnet_query(headword)
    if wordnet_pos:
        lemma = wn.morphy(query, wordnet_pos)
        if lemma:
            candidates.append(lemma.replace("_", " "))
    return list(dict.fromkeys(candidates))


def tokens(text: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(text.casefold()) if token not in STOPWORDS}


def synset_similarity(definition: str, synset: Any) -> float:
    source = tokens(definition)
    gloss = tokens(
        " ".join(
            [
                synset.definition(),
                *synset.examples(),
                *(lemma.name().replace("_", " ") for lemma in synset.lemmas()),
            ]
        )
    )
    if not source or not gloss:
        return 0.0
    return len(source & gloss) / math.sqrt(len(source) * len(gloss))


def wordnet_features(entry: dict[str, Any]) -> dict[str, Any]:
    wordnet_pos = POS_TO_WORDNET.get(entry["part_of_speech"])
    query = normalize_wordnet_query(entry["headword"])
    synsets = wn.synsets(query, pos=wordnet_pos) if wordnet_pos else []
    if not synsets and wordnet_pos:
        morphy = wn.morphy(query, wordnet_pos)
        if morphy:
            synsets = wn.synsets(morphy, pos=wordnet_pos)

    best_synset = None
    best_index = None
    best_similarity = 0.0
    for index, synset in enumerate(synsets, start=1):
        similarity = synset_similarity(entry["definition"], synset)
        if best_synset is None or similarity > best_similarity:
            best_synset = synset
            best_index = index
            best_similarity = similarity

    synonyms: set[str] = set()
    derivations: set[str] = set()
    normalized_headword = entry["headword"].casefold()
    for synset in synsets:
        for lemma in synset.lemmas():
            lemma_name = lemma.name().replace("_", " ").casefold()
            if lemma_name != normalized_headword:
                synonyms.add(lemma_name)
            for related in lemma.derivationally_related_forms():
                related_name = related.name().replace("_", " ").casefold()
                if related_name != normalized_headword:
                    derivations.add(related_name)

    return {
        "wordnet_pos": wordnet_pos,
        "wordnet_synset_count": len(synsets),
        "wordnet_best_synset": best_synset.name() if best_synset else None,
        "wordnet_best_sense_index": best_index,
        "wordnet_definition_similarity": round(best_similarity, 4),
        "wordnet_lexname": best_synset.lexname() if best_synset else None,
        "wordnet_synonym_count": len(synonyms),
        "wordnet_derivation_count": len(derivations),
        "wordnet_synonyms": sorted(synonyms),
        "wordnet_derivations": sorted(derivations),
    }


def list_band_score(
    ngsl_rank: int | None,
    nawl_member: bool,
    zipf: float,
    sense_number: int | None,
) -> float:
    if nawl_member:
        score = 8.0
    elif ngsl_rank is not None:
        if ngsl_rank <= 800:
            score = 2.0
        elif ngsl_rank <= 1200:
            score = 3.0
        elif ngsl_rank <= 1800:
            score = 5.0
        elif ngsl_rank <= 2400:
            score = 7.0
        else:
            score = 8.0
    elif zipf >= 5.0:
        score = 2.5
    elif zipf >= 3.2:
        score = 7.0
    elif zipf >= 2.6:
        score = 5.5
    elif zipf >= 2.0:
        score = 3.5
    else:
        score = 2.0

    if sense_number and sense_number > 1:
        score += min(2.0, 1.25 * (sense_number - 1))
    return min(8.0, score)


def conceptual_utility_score(part_of_speech: str, lexname: str | None) -> float:
    if lexname in ABSTRACT_LEXNAMES:
        return 6.0
    if lexname in CONCRETE_LEXNAMES:
        return 2.5
    if lexname in ACTION_LEXNAMES:
        return 4.0
    if lexname and (lexname.startswith("adj.") or lexname.startswith("adv.")):
        return 5.5
    return {
        "v.": 5.0,
        "adj.": 5.5,
        "adv.": 5.0,
        "n.": 4.0,
    }.get(part_of_speech, 1.0)


def domain_flags(definition: str) -> tuple[list[str], list[str]]:
    explicit = [
        label
        for label, pattern in EXPLICIT_DOMAIN_PATTERNS.items()
        if re.search(pattern, definition, re.IGNORECASE)
    ]
    weak = [
        label
        for label, pattern in WEAK_DOMAIN_PATTERNS.items()
        if re.search(pattern, definition, re.IGNORECASE)
    ]
    return explicit, weak


def non_specialization_score(explicit: list[str], weak: list[str]) -> float:
    if explicit:
        return 1.0
    if weak:
        return 2.5
    return 4.0


def register_features(definition: str) -> tuple[str, float]:
    if HISTORIC_REGISTER_RE.search(definition):
        return "historic-or-dialect", 0.0
    if MARKED_REGISTER_RE.search(definition):
        return "marked-register", 1.0
    if re.search(r"\bformal (?:effect|term|word|usage)\b", definition, re.IGNORECASE):
        return "formal-register", 1.5
    return "contemporary-neutral", 2.0


def learning_leverage(
    wn_features: dict[str, Any],
    group_size: int,
    source_pos_count: int,
    source_entry_count: int,
) -> tuple[float, dict[str, float]]:
    def scaled(count: int, maximum_count: int, points: float) -> float:
        if count <= 0:
            return 0.0
        return points * min(1.0, math.log1p(count) / math.log1p(maximum_count))

    components = {
        "derivational_family": scaled(
            int(wn_features["wordnet_derivation_count"]), 8, 8.0
        ),
        "synonym_network": scaled(int(wn_features["wordnet_synonym_count"]), 8, 4.0),
        "wordnet_polysemy": scaled(int(wn_features["wordnet_synset_count"]), 8, 3.0),
        "source_synonym_group": scaled(max(0, group_size - 1), 5, 2.0),
        "part_of_speech_breadth": scaled(max(0, source_pos_count - 1), 3, 2.0),
        "source_sense_breadth": scaled(max(0, source_entry_count - 1), 3, 1.0),
    }
    rounded = {key: round(value, 2) for key, value in components.items()}
    return round(min(20.0, sum(components.values())), 2), rounded


def sense_centrality(
    sense_number: int | None, register_label: str, resolved: bool
) -> float:
    if not resolved:
        return 0.0
    score = {
        None: 10.0,
        1: 10.0,
        2: 7.0,
        3: 4.5,
        4: 2.5,
    }.get(sense_number, 1.0)
    if register_label == "historic-or-dialect":
        score -= 3.0
    elif register_label == "marked-register":
        score -= 1.0
    elif register_label == "formal-register":
        score -= 0.5
    return round(max(0.0, score), 2)


def score_entries(
    entries: list[dict[str, Any]], ngsl: dict[str, int], nawl: set[str]
) -> list[dict[str, Any]]:
    group_sizes = Counter(entry["group_index"] for entry in entries)
    source_pos: dict[str, set[str]] = defaultdict(set)
    source_entries = Counter()
    for entry in entries:
        key = entry["headword"].casefold()
        source_pos[key].add(entry["part_of_speech"])
        source_entries[key] += 1

    scored: list[dict[str, Any]] = []
    for entry in entries:
        row = dict(entry)
        if not entry["resolved"]:
            row.update(
                {
                    "reference_lookup_lemma": None,
                    "ngsl_rank": None,
                    "nawl_member": False,
                    "wordnet_pos": None,
                    "wordnet_synset_count": 0,
                    "wordnet_best_synset": None,
                    "wordnet_best_sense_index": None,
                    "wordnet_definition_similarity": 0.0,
                    "wordnet_lexname": None,
                    "wordnet_synonym_count": 0,
                    "wordnet_derivation_count": 0,
                    "wordnet_synonyms": [],
                    "wordnet_derivations": [],
                    "domain_flags": [],
                    "weak_domain_flags": [],
                    "register_label": "unresolved",
                    "tier2_fit_components": {},
                    "tier2_fit_score": 0.0,
                    "learning_leverage_components": {},
                    "learning_leverage_score": 0.0,
                    "sense_centrality_score": 0.0,
                    "semantic_score": 0.0,
                    "pre_penalty_total": float(entry["objective_score"]),
                    "semantic_rationale_flags": ["unresolved"],
                }
            )
            scored.append(row)
            continue

        wn_features = wordnet_features(entry)
        candidates = lookup_candidates(entry["headword"], wn_features["wordnet_pos"])
        reference_lemma = next(
            (candidate for candidate in candidates if candidate in ngsl or candidate in nawl),
            candidates[0],
        )
        ngsl_rank = ngsl.get(reference_lemma)
        nawl_member = reference_lemma in nawl
        explicit_domains, weak_domains = domain_flags(entry["definition"])
        register_label, register_score = register_features(entry["definition"])

        tier2_components = {
            "list_register_band": list_band_score(
                ngsl_rank,
                nawl_member,
                float(entry["wordfreq_zipf"]),
                entry["sense_number"],
            ),
            "conceptual_utility": conceptual_utility_score(
                entry["part_of_speech"], wn_features["wordnet_lexname"]
            ),
            "non_specialization": non_specialization_score(
                explicit_domains, weak_domains
            ),
            "contemporary_register": register_score,
        }
        tier2_components = {
            key: round(value, 2) for key, value in tier2_components.items()
        }
        tier2_score = round(min(20.0, sum(tier2_components.values())), 2)

        headword_key = entry["headword"].casefold()
        leverage_score, leverage_components = learning_leverage(
            wn_features,
            group_sizes[entry["group_index"]],
            len(source_pos[headword_key]),
            source_entries[headword_key],
        )
        centrality_score = sense_centrality(
            entry["sense_number"], register_label, entry["resolved"]
        )
        semantic_score = round(tier2_score + leverage_score + centrality_score, 2)

        rationale: list[str] = []
        if nawl_member:
            rationale.append("NAWL-1.2")
        if ngsl_rank is not None:
            rationale.append(f"NGSL-rank-{ngsl_rank}")
        if explicit_domains:
            rationale.append("explicit-domain:" + ",".join(explicit_domains))
        if weak_domains:
            rationale.append("domain-context:" + ",".join(weak_domains))
        if register_label != "contemporary-neutral":
            rationale.append(register_label)
        if wn_features["wordnet_derivation_count"] >= 4:
            rationale.append("productive-word-family")
        if wn_features["wordnet_synset_count"] >= 4:
            rationale.append("polysemous")
        if wn_features["wordnet_best_synset"] is None:
            rationale.append("no-WordNet-synset")

        row.update(
            {
                "reference_lookup_lemma": reference_lemma,
                "ngsl_rank": ngsl_rank,
                "nawl_member": nawl_member,
                **wn_features,
                "source_group_size": group_sizes[entry["group_index"]],
                "source_pos_count": len(source_pos[headword_key]),
                "source_entry_count": source_entries[headword_key],
                "domain_flags": explicit_domains,
                "weak_domain_flags": weak_domains,
                "register_label": register_label,
                "tier2_fit_components": tier2_components,
                "tier2_fit_score": tier2_score,
                "learning_leverage_components": leverage_components,
                "learning_leverage_score": leverage_score,
                "sense_centrality_score": centrality_score,
                "semantic_score": semantic_score,
                "pre_penalty_total": round(
                    float(entry["objective_score"]) + semantic_score, 2
                ),
                "semantic_rationale_flags": rationale,
            }
        )
        scored.append(row)

    return scored


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


def table_rows(
    rows: Iterable[dict[str, Any]], start_rank: int = 1
) -> list[str]:
    result = [
        "| Rank | Entry | POS | Obj. /50 | Tier 2 /20 | Leverage /20 | Sense /10 | Pre-penalty /100 | Flags |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for rank, row in enumerate(rows, start=start_rank):
        sense = "" if row["sense_number"] is None else f"^{row['sense_number']}"
        flags = "; ".join(row["semantic_rationale_flags"])
        result.append(
            f"| {rank} | {row['headword']}{sense} | {row['part_of_speech']} | "
            f"{row['objective_score']:.2f} | {row['tier2_fit_score']:.2f} | "
            f"{row['learning_leverage_score']:.2f} | "
            f"{row['sense_centrality_score']:.2f} | "
            f"{row['pre_penalty_total']:.2f} | {flags} |"
        )
    return result


def build_report(
    scored: list[dict[str, Any]], ngsl_path: Path, nawl_path: Path
) -> str:
    eligible = [row for row in scored if row["resolved"]]
    ranked = sorted(
        eligible,
        key=lambda row: (-row["pre_penalty_total"], row["entry_index"]),
    )
    semantic_dist = quantiles([row["semantic_score"] for row in eligible])
    total_dist = quantiles([row["pre_penalty_total"] for row in eligible])
    no_wordnet = [row for row in eligible if row["wordnet_best_synset"] is None]
    domain_flagged = [row for row in eligible if row["domain_flags"]]
    register_flagged = [
        row
        for row in eligible
        if row["register_label"] != "contemporary-neutral"
    ]
    boundary_start = 489
    boundary_end = min(510, len(ranked))
    boundary = ranked[boundary_start:boundary_end]

    report = [
        "# Tier 2 Words: Stage 3 Semantic Scoring Report",
        "",
        "Stage 3 adds a 50-point semantic baseline to the 50 objective points from",
        "Stage 2. It does **not** apply exclusion penalties or select the final 500.",
        "The apparent 500th-place boundary below is an audit target for Stage 4.",
        "",
        "## Reference lists",
        "",
        "- NGSL 1.2: general-English rank signal (2,809 lemmas).",
        "  Source: https://www.newgeneralservicelist.com/new-general-service-list",
        "- NAWL 1.2: cross-disciplinary academic-English membership signal.",
        "  Source: https://www.newgeneralservicelist.com/new-academic-word-list",
        "- WordNet: sense, synonym, polysemy, and derivational-relation signal.",
        "  Source: https://wordnet.princeton.edu/",
        f"- NGSL SHA-256: `{file_sha256(ngsl_path)}`",
        f"- NAWL SHA-256: `{file_sha256(nawl_path)}`",
        "",
        "Only membership/rank annotations derived from the reference lists are written",
        "to the scoring output; the downloaded reference files remain under `tmp/`.",
        "",
        "## Scoring formula (50 points)",
        "",
        "### Tier 2 fit (20)",
        "",
        "- list/register band: 8 points (NAWL membership, NGSL rank band, or a",
        "  wordfreq fallback; later senses of basic headwords receive a small bonus)",
        "- conceptual utility: 6 points (WordNet lexical class, with abstract and",
        "  cross-context meanings favored over concrete object labels)",
        "- non-specialization: 4 points (explicit technical-domain definitions score lower)",
        "- contemporary neutral register: 2 points",
        "",
        "### Learning leverage (20)",
        "",
        "- derivational family: 8 points",
        "- synonym network: 4 points",
        "- WordNet polysemy: 3 points",
        "- source synonym group: 2 points",
        "- part-of-speech breadth: 2 points",
        "- source sense breadth: 1 point",
        "",
        "All count-based components use capped logarithmic scaling so a single very",
        "large family cannot dominate the score.",
        "",
        "### Sense centrality (10)",
        "",
        "- unnumbered or sense 1: 10 points",
        "- sense 2: 7 points; sense 3: 4.5; sense 4: 2.5",
        "- historical/dialect and marked-register definitions receive transparent",
        "  reductions. These do not replace the stronger Stage 4 penalties.",
        "",
        "## Validation summary",
        "",
        f"- Input entries: {len(scored):,}",
        f"- Resolved/scored entries: {len(eligible):,}",
        f"- NAWL matches: {sum(row['nawl_member'] for row in eligible):,}",
        f"- NGSL matches: {sum(row['ngsl_rank'] is not None for row in eligible):,}",
        f"- Entries without a POS-matched WordNet synset: {len(no_wordnet):,}",
        f"- Explicit technical-domain flags: {len(domain_flagged):,}",
        f"- Historical/dialect/marked-register flags: {len(register_flagged):,}",
        "- Semantic score distribution: "
        + ", ".join(f"{key}={value:.2f}" for key, value in semantic_dist.items()),
        "- Pre-penalty total distribution: "
        + ", ".join(f"{key}={value:.2f}" for key, value in total_dist.items()),
        "",
        "## Provisional top 40 (audit view only)",
        "",
        *table_rows(ranked[:40]),
        "",
        "## Provisional ranks 490–510 (Stage 4 boundary audit)",
        "",
        *table_rows(boundary, start_rank=boundary_start + 1),
        "",
        "## Stage 4 handoff",
        "",
        "Stage 4 should apply explicit penalties for Tier 1/basic vocabulary, narrow",
        "technical vocabulary, archaic/dialectal usage, non-central senses, and unresolved",
        "entries. It should then directly review the high-score pool and at least the",
        "entries around the final inclusion boundary.",
        "",
    ]
    return "\n".join(report)


def write_outputs(
    scored: list[dict[str, Any]], output_dir: Path, ngsl_path: Path, nawl_path: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "semantic-scores.jsonl"
    csv_path = output_dir / "semantic-scores.csv"
    report_path = output_dir / "semantic-report.md"

    with jsonl_path.open("w", encoding="utf-8") as stream:
        for row in scored:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    csv_fields = [
        "entry_index",
        "entry_id",
        "headword",
        "sense_number",
        "part_of_speech",
        "definition",
        "source_line",
        "resolved",
        "wordfreq_zipf",
        "frequency_score",
        "genre_range_score",
        "objective_score",
        "reference_lookup_lemma",
        "ngsl_rank",
        "nawl_member",
        "wordnet_best_synset",
        "wordnet_best_sense_index",
        "wordnet_definition_similarity",
        "wordnet_lexname",
        "wordnet_synset_count",
        "wordnet_synonym_count",
        "wordnet_derivation_count",
        "source_group_size",
        "source_pos_count",
        "source_entry_count",
        "domain_flags",
        "weak_domain_flags",
        "register_label",
        "tier2_fit_components",
        "tier2_fit_score",
        "learning_leverage_components",
        "learning_leverage_score",
        "sense_centrality_score",
        "semantic_score",
        "pre_penalty_total",
        "semantic_rationale_flags",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        for row in scored:
            flat = dict(row)
            for key in (
                "domain_flags",
                "weak_domain_flags",
                "tier2_fit_components",
                "learning_leverage_components",
                "semantic_rationale_flags",
            ):
                flat[key] = json.dumps(flat[key], ensure_ascii=False, sort_keys=True)
            writer.writerow(flat)

    report_path.write_text(build_report(scored, ngsl_path, nawl_path), encoding="utf-8")


def validate(scored: list[dict[str, Any]]) -> None:
    if len(scored) != 2529:
        raise ValueError(f"Expected 2,529 entries, found {len(scored):,}")
    if len({row["entry_id"] for row in scored}) != len(scored):
        raise ValueError("Duplicate entry IDs after semantic scoring")
    for row in scored:
        bounds = (
            ("tier2_fit_score", 0.0, 20.0),
            ("learning_leverage_score", 0.0, 20.0),
            ("sense_centrality_score", 0.0, 10.0),
            ("semantic_score", 0.0, 50.0),
            ("pre_penalty_total", 0.0, 100.0),
        )
        for field, low, high in bounds:
            value = float(row[field])
            if not low <= value <= high:
                raise ValueError(f"{row['entry_id']}: {field}={value} out of bounds")
        expected_semantic = round(
            row["tier2_fit_score"]
            + row["learning_leverage_score"]
            + row["sense_centrality_score"],
            2,
        )
        if row["semantic_score"] != expected_semantic:
            raise ValueError(f"{row['entry_id']}: semantic sum mismatch")
        expected_total = round(row["objective_score"] + row["semantic_score"], 2)
        if row["pre_penalty_total"] != expected_total:
            raise ValueError(f"{row['entry_id']}: pre-penalty sum mismatch")
        if not row["resolved"] and row["semantic_score"] != 0.0:
            raise ValueError(f"{row['entry_id']}: unresolved entry has semantic points")


def main() -> None:
    args = parse_args()
    nltk.data.path.insert(0, str(args.nltk_data))
    entries = load_jsonl(args.input)
    ngsl = load_ngsl(args.ngsl)
    nawl = load_nawl(args.nawl)
    scored = score_entries(entries, ngsl, nawl)
    validate(scored)
    write_outputs(scored, args.output_dir, args.ngsl, args.nawl)
    print(f"Scored {len(scored):,} entries; outputs written to {args.output_dir}")


if __name__ == "__main__":
    main()
