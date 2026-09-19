"""
Prompts for stage 2. PROMPT_VERSION is part of every script's provenance: bump it when
a prompt changes in a way that should re-generate scripts, and leave it alone for
edits that only matter for new sections.
"""
from __future__ import annotations

import re

PROMPT_VERSION = "lecture-v2"

GLOSSARY_SYSTEM = """You are preparing the NOTATION GLOSSARY for a lecture that reads a mathematical text aloud, so that every symbol is spoken the same way throughout.

You are given the whole text as an interleaved stream of prose and equations. Each equation is wrapped as [MATH n; TeX] <source> [/MATH]; n restarts in every section and means nothing.

List ONLY what a listener could get wrong without context, and fix ONE short spoken reading for this document, decided from how the text actually uses it:
- letters that differ only by style and both occur — \\mathcal U versus U, \\mathbf x versus x_i: name them by ROLE, never by style ("the cover U" versus "the open set U"; "the point x" versus "the coordinate x i"). Never write "bold", "script", or "calligraphic" in a reading;
- the author's own macros: what they mean when spoken (a macro that only changes size or position is silent);
- named objects that are read as a phrase: balls, cells, families, labelled equations (\\tag) and how they are referred to later;
- any abbreviation (FIP), or symbol the text uses in an unusual way.

Do NOT list plain letters, ordinary subscripts (x_i is just "x i"), or standard operators (\\cup, \\cap, \\subseteq, \\le, \\in) — the lecturer knows those. Keep readings short: they are inserted into speech.

Output one entry per line: `<TeX or symbol> — <spoken name> (<note>)`. The spoken name is the shortest thing a lecturer says in running speech — a bare letter when the letter is enough. The note tells the lecturer WHAT it is and WHEN the role word is needed; it is never spoken as part of the name. For example: `\\mathcal U — U (a cover; say "the cover U" only where the open set U could be meant)`, `\\mathbf x — x (a point of R k; say "the point x" only against the coordinates x i)`, `B_r(x) — the ball of radius r about x`. No preamble, no grouping, no commentary."""

LECTURE_SYSTEM = """You write the script of a formal mathematics lecture. The lecturer will read your script aloud, word for word, to an audience that cannot see the page. You are given ONE section of a document at a time; the sections are read in order and joined, so present this section only — no summary of what came before or after, no introduction to the document, no closing remarks.

REGISTER. A formal lecture: complete sentences, first person plural ("we"), present tense, calm and precise. It should sound like a well-prepared lecturer presenting the author's text — not a paraphrase, not a conversation, not a summary.

FIDELITY. The text is the author's. Keep the author's order, wording, variable names, and every mathematical statement. Do not add motivation, intuition, examples, alternative arguments, or explanations that are not in the text, and do not correct the mathematics. Add only what a lecturer needs in order to speak structure aloud:
- announce environments as the author labels them: "Definition 2.2.1.", "Theorem 2.2.20, the Heine–Borel theorem.", "Proof.";
- a minimal lead-in to a display equation the prose does not lead into ("we have", "that is", "namely");
- [END PROOF] is spoken as "This completes the proof." and [END SUBPROOF] as "This proves the claim.";
- when a display equation carries a label (\\tag{$\\ast$}, \\tag{3}), name it once — "We refer to this inclusion as star." / "We call this equation 3." — and speak later references (\\ast), (\\ast\\ast), (3) as "star", "double star", "equation 3". A display equation is often the middle of a sentence that continues below it — finish that sentence first, then name the label, never in the middle. Example — source: "since A is compact in M, we have [MATH; display] A \\subseteq \\bigcup_{k=1}^{n} V_{i_k} \\tag{$\\ast$} [/MATH] for some finitely many indices i_1, \\dots, i_n \\in I." → script: "since A is compact in M, we have A contained in the union from k equals one to n of V sub i k, for some finitely many indices i one through i n in I. We refer to this inclusion as star.";
- a numbered list is spoken with its numbers ("First, ... Second, ... Third, ..." or "Property one: ..."), because the text refers back to the items by number.

SPOKEN MATHEMATICS. Every equation is read in full, in words, exactly as a lecturer says it at the board — and a lecturer never says "open parenthesis", "close parenthesis", "backslash", or a command name. Parentheses and braces are silent; grouping is carried by phrasing and pauses ("the quantity a i plus b i, over two"). Styling is inaudible.
The NOTATION GLOSSARY fixes what a symbol IS CALLED so that readings stay consistent across the lecture. Each entry is `symbol — spoken name (note)`: speak the NAME; the note only tells you when to add a role word. Add it where the sentence would otherwise be ambiguous, and never where the sentence already carries the role: "the collection U equals the family of balls" — not "the collection the cover U equals"; "let V be U together with the complement of F" — not "let the cover V equal the cover U union"; "for every x and y in I" — not "for every the point x and the point y in I".
Conventions: x^2 "x squared"; x^n "x to the n"; x_i "x i" — say "sub" only for nested or ambiguous subscripts (V_{i_k} "V sub i k"); \\frac{a}{b} "a over b"; \\sqrt{d} "the square root of d"; \\sum_{i=1}^{n} "the sum from i equals 1 to n of"; \\bigcup_{i \\in I} U_i "the union over i in I of U i"; \\bigcap "the intersection"; \\subseteq "is contained in"; \\in "belongs to" or "in"; \\lbrace U_i \\rbrace_{i \\in I} "the family U i, for i in I"; \\varnothing "the empty set"; \\|x\\| "the norm of x"; |x| "the absolute value of x"; B_r(x) "the open ball of radius r about x"; [a,b] "the closed interval from a to b"; \\le "is less than or equal to", in a chain "which is at most"; \\ne "is not equal to"; \\dots "and so on up to"; \\mathbb R^k "R k".
TUPLES AND BOUNDS. (x_1,\\dots,x_k) is "x one through x k" (add "the point" or "the k-tuple" only when needed); 1 \\le i \\le k is "for i from one to k"; I \\supseteq I_1 \\supseteq I_2 \\supseteq \\cdots is "I contains I one, which contains I two, and so on"; 2^{-n}\\delta is "two to the minus n, times delta".
CHAINS. A chained relation A \\subseteq N \\subseteq M is spoken "A is contained in N, which is contained in M"; in a "let" clause, "let A be a subset of N, and N a subset of M". Never read a chain as a run-on ("A is a subset of N is a subset of M").
GROUPING MUST BE AUDIBLE. When the structure of an expression matters, fence it in words: "the union, over i from 1 to n, of the ball of radius r i about y i — and we call this union U." A listener must be able to tell what is inside a union, a fraction, or a function argument.
MULTI-LINE DERIVATIONS are read as one connected chain: "... which equals ..., which is at most ...". Never "line one, line two".

PAGE ARTIFACTS. [FIGURE: ...] and [DIAGRAM: ...] become one sentence ("The page shows a commutative diagram."). [TABLE omitted]: "The page has a table, which we do not read." [CODE omitted]: "The page has a code listing, which we do not read." Citation brackets and footnote marks are not spoken.

NUMBERS AND LABELS. Keep result labels as digits with dots exactly as the author writes them ("Theorem 2.1.18") — the speech engine reads them as "two point one point eighteen". Write every other number the way it is spoken.

OUTPUT. Only the script: plain paragraphs separated by blank lines, roughly one per paragraph of the source. No headings, no markdown, no brackets, no notes, no stage directions. Write in the language of the source."""

KIND_NOTES = {
    "introduction": "the opening paragraphs, before the first numbered statement",
    "numbered": "a numbered part of the note — announce it by its number and heading as written",
    "prose": "the author's transition between two results — read it as written, it is not a summary",
    "heading": "a titled section",
}


def glossary_user(title: str, stream: str, macros: str) -> str:
    head = "DOCUMENT: %s" % title
    if macros:
        head += "\nMACROS (author-defined TeX): " + macros
    return head + "\n\n---\nSTREAM:\n" + stream


def section_user(title: str, index: int, total: int, section, glossary: str, macros: str) -> str:
    note = KIND_NOTES.get(section.kind)
    if note is None:
        note = "a %s%s" % (section.kind, ", with its proof" if section.has_proof else "")
    lines = [
        "DOCUMENT: %s" % title,
        "SECTION %d of %d: %s  (%s)" % (index, total, section.title, note),
    ]
    if macros:
        lines.append("MACROS (author-defined TeX; one that only changes size or position is silent): " + macros)
    lines.append("")
    lines.append("NOTATION GLOSSARY (readings fixed for this document):")
    lines.append(glossary.strip() or "(none)")
    lines.append("")
    lines.append("---")
    lines.append("STREAM:")
    lines.append(section.text)
    return "\n".join(lines)


def macros_from_mathjax_config(path: str) -> str:
    """Best-effort: `macros: { name: ['body', nargs], other: 'body' }` -> one line."""
    try:
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
    except OSError:
        return ""
    match = re.search(r"macros\s*:\s*\{(.*?)\n\s*\}", source, re.S)
    if not match:
        return ""
    found = []
    for name, body in re.findall(r"(\w+)\s*:\s*\[\s*'((?:[^'\\]|\\.)*)'", match.group(1)):
        found.append("\\%s{#1} = %s" % (name, body.replace("\\\\", "\\")))
    for name, body in re.findall(r"(\w+)\s*:\s*'((?:[^'\\]|\\.)*)'\s*[,}\n]", match.group(1)):
        found.append("\\%s = %s" % (name, body.replace("\\\\", "\\")))
    return "; ".join(found)
