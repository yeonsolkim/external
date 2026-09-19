"""
Stage 1 — skeleton: a built Jekyll post (HTML) -> a deterministic, sectioned
prose+math stream that the script stage turns into narration.

No LLM here. Everything this module does is a pure function of the HTML, so a
section's `hash` is stable until the section itself changes, and that hash is what
every later stage keys on (script, audio).

Stream format, per section (compatible with the old extension's extract.js):

    ... prose ... [MATH n; TeX] <source> [/MATH] ... prose ...
    [MATH n; TeX display] <source> [/MATH]
    ... Proof. ... [END PROOF]

Math is numbered per SECTION, not per document, so inserting an equation in one
section does not renumber — and re-hash — every section after it.

Sectioning rule (this site): a section opens at every heading (h2–h6) and at every
numbered environment paragraph (`<strong>Theorem 2.2.16.</strong> ...`). The
environment's statement, its proof, display equations and lists belong to it. The
transitional prose the author writes between one result and the next is its own
`prose` section: after a proof, every paragraph that follows the QED; without a
proof, a paragraph that starts a new sentence in a new block (a paragraph that
finishes a display equation, or begins lowercase, still belongs to the statement).
Prose before the first section is "Introduction". A "References" heading is kept
but skipped.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Optional

from .htmltree import Node, parse_html

SKELETON_VERSION = 3

# Environment kinds this site writes as `**Kind N.N.N.**` at the start of a paragraph.
ENV_KINDS = {
    "definition", "theorem", "lemma", "corollary", "proposition", "remark", "example",
    "exercise", "notation", "convention", "axiom", "problem", "claim", "conjecture",
    "note", "observation", "fact", "question", "postulate",
}
ENV_RE = re.compile(r"^\s*([A-Z][a-z]+)\s+(\d+(?:\.\d+)*)\s*\.?\s*$")
ENV_UNNUMBERED_RE = re.compile(r"^\s*([A-Z][a-z]+)\s*\.\s*$")
# `**1. Trials and outcomes.**` — the site's main.js treats these as entries too, but only in
# the mathematics/physics domains (`data-post-domain` on .post-body); we follow suit.
NUMBERED_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.(?:\s+(\S.*?))?\s*$")
NUMBERED_DOMAINS = {"mathematics", "physics"}
PROOF_RE = re.compile(r"^\s*(?:proof|sketch of proof|proof sketch|solution)\b", re.I)
# "(Heine–Borel theorem)." right after the bold label
ENV_NAME_RE = re.compile(r"^\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*\.?")
REFERENCE_TITLES = {"references", "reference", "bibliography", "further reading"}

SPACES = re.compile(r"[ \t\r\n\u00a0\u2000-\u200b\u202f\u205f\u3000]+")
INLINE_MATH_SPAN = re.compile(r"\A\s*\\\((.*)\\\)(.*)\Z", re.S)
# QED inside a display equation's tag: \tag*{\(\square\)} / \tag*{$\blacksquare$}
QED_TAG = re.compile(r"\\tag\*?\{\s*(?:\\\(|\$)?\s*\\(black)?square\s*(?:\\\)|\$)?\s*\}")
TRAILING_PUNCT = re.compile(r"^(.*?[^\\\s])\s*([.,;:!?])\s*$", re.S)
TOKEN = re.compile(r"\x00(\d+)\x00")
CUE_WORDS = re.compile(r"\[(?:END (?:SUB)?PROOF|FIGURE[^\]]*|DIAGRAM[^\]]*|TABLE omitted|CODE omitted|UNREADABLE EQUATION)\]")


# ----------------------------------------------------------------------------- model
@dataclass
class Block:
    kind: str                      # p | display | list | heading | figure | table | code
    text: str                      # with \x00i\x00 math placeholders
    env: Optional[dict] = None     # {"kind","label","name"} when the block opens an environment
    proof: bool = False            # the block opens a proof
    ends: Optional[str] = None     # "proof" | "subproof" when the block closes one
    level: int = 0                 # headings
    id: str = ""                   # headings


@dataclass
class Section:
    id: str
    title: str
    kind: str                      # introduction | heading | definition | theorem | ...
    level: int = 2
    label: str = ""
    name: str = ""
    anchor: Optional[str] = None   # an id that exists in the HTML, if any
    skip: Optional[str] = None     # reason, when the section is not narrated
    text: str = ""
    hash: str = ""
    math: int = 0
    words: int = 0
    has_proof: bool = False
    blocks: list = field(default_factory=list, repr=False)


@dataclass
class Skeleton:
    url: str
    title: str
    lang: str
    scope: str
    published: str
    modified: str
    sections: list
    hash: str
    math: int
    words: int
    warnings: list
    version: int = SKELETON_VERSION
    description: str = ""
    published_at: str = ""
    narrate: bool = False          # front matter `publish: true` (the layout emits <meta name="narrate">)

    def to_dict(self) -> dict:
        data = asdict(self)
        for section in data["sections"]:
            section.pop("blocks", None)
        return data


class SkeletonError(Exception):
    pass


# ----------------------------------------------------------------------------- text
def normalize(text: str) -> str:
    """The one place whitespace and Unicode are normalised. Part of the cache key."""
    text = unicodedata.normalize("NFC", text)
    return SPACES.sub(" ", text).strip()


def clean_tex(tex: str) -> tuple:
    """Returns (tex, ended) where `ended` is "proof"/"subproof" if a QED tag was removed."""
    ended = None
    match = QED_TAG.search(tex)
    if match:
        ended = "subproof" if match.group(1) else "proof"
        tex = QED_TAG.sub("", tex)
    tex = normalize(tex)
    tex = re.sub(r"^\\(?:display|text|script)style\s+", "", tex)
    return tex, ended


def split_trailing_punct(tex: str) -> tuple:
    """`A\\subseteq M.` -> (`A\\subseteq M`, `.`) so sentence punctuation stays prose."""
    match = TRAILING_PUNCT.match(tex)
    if not match:
        return tex, ""
    return match.group(1), match.group(2)


def word_count(text: str) -> int:
    text = TOKEN.sub(" ", text)
    text = CUE_WORDS.sub(" ", text)
    return len([w for w in re.split(r"\s+", text) if re.search(r"\w", w)])


# ----------------------------------------------------------------------------- inline
class Renderer:
    """Turns inline content into text with math placeholders. One per document."""

    def __init__(self, numbered_labels: bool = False) -> None:
        self.math: list = []        # (tex, display)
        self.warnings: list = []
        self.ended: Optional[str] = None   # set when an environment-end marker was rendered
        self.numbered_labels = numbered_labels   # `**1. Name.**` opens a section

    # math ---------------------------------------------------------------------
    def token(self, tex: str, display: bool) -> str:
        tex, ended = clean_tex(tex)
        trailing = ""
        if not display:
            tex, trailing = split_trailing_punct(tex)
        if ended:
            self.ended = ended
        if not tex:
            return trailing
        self.math.append((tex, display))
        cue = ""
        if ended:
            cue = " [END SUBPROOF]" if ended == "subproof" else " [END PROOF]"
        return "\x00%d\x00%s%s" % (len(self.math) - 1, trailing, cue)

    def text(self, raw: str) -> str:
        """Bare text: may still carry \\(..\\), \\[..\\], $$..$$ or $..$ delimiters."""
        out = []
        i = 0
        n = len(raw)
        while i < n:
            ch = raw[i]
            if ch == "\\" and i + 1 < n:
                nxt = raw[i + 1]
                if nxt in "([":
                    close = "\\)" if nxt == "(" else "\\]"
                    j = raw.find(close, i + 2)
                    if j >= 0:
                        out.append(self.token(raw[i + 2:j], display=(nxt == "[")))
                        i = j + 2
                        continue
                if nxt == "$":
                    out.append("$")
                    i += 2
                    continue
            if ch == "$":
                if raw.startswith("$$", i):
                    j = raw.find("$$", i + 2)
                    if j >= 0:
                        out.append(self.token(raw[i + 2:j], display=True))
                        i = j + 2
                        continue
                elif i + 1 < n and not raw[i + 1].isspace():
                    j = self._closing_dollar(raw, i + 1)
                    if j >= 0:
                        out.append(self.token(raw[i + 1:j], display=False))
                        i = j + 1
                        continue
            out.append(ch)
            i += 1
        return "".join(out)

    @staticmethod
    def _closing_dollar(raw: str, start: int) -> int:
        i = start
        while i < len(raw):
            if raw[i] == "$" and not raw[i - 1].isspace() and raw[i - 1] != "\\":
                if i + 1 < len(raw) and raw[i + 1] == "$":
                    return -1
                return i
            if raw[i] == "\n" and i + 1 < len(raw) and raw[i + 1] == "\n":
                return -1
            i += 1
        return -1

    # elements -----------------------------------------------------------------
    def inline(self, node: Node) -> str:
        return "".join(self._inline_child(child) for child in node.children)

    def _inline_child(self, node: Node) -> str:
        if node.is_text:
            return self.text(node.text)
        tag = node.tag
        ended = node.get("data-environment-end")
        if ended:
            self.ended = "subproof" if ended == "subproof" else "proof"
            return " [END SUBPROOF]" if ended == "subproof" else " [END PROOF]"
        if tag in ("script", "style", "template", "noscript"):
            return ""
        if tag == "span" and node.has_class("math-inline"):
            match = INLINE_MATH_SPAN.match(node.text_content())
            if match:
                return self.token(match.group(1), display=False) + match.group(2)
            return self.inline(node)
        if tag == "br":
            return " "
        if tag == "img":
            alt = normalize(node.get("alt") or "")
            self.warnings.append("figure narrated as its caption only")
            return " [FIGURE: %s] " % alt if alt else " [FIGURE] "
        if tag == "svg":
            return " " + self.figure_cue(node) + " "
        if tag == "sup" and (node.get("id") or "").startswith("fnref"):
            return ""
        if tag == "a" and (node.has_class("footnote") or node.has_class("reversefootnote")):
            return ""
        if tag == "math":
            annotation = node.find(lambda n: n.tag == "annotation" and "tex" in (n.get("encoding") or ""))
            if annotation:
                return self.token(annotation.text_content(), display=(node.get("display") == "block"))
            self.warnings.append("MathML without a TeX annotation")
            return " [UNREADABLE EQUATION] "
        if tag in ("ol", "ul"):
            return " " + self.list_text(node) + " "
        if tag == "table":
            self.warnings.append("table omitted")
            return " [TABLE omitted] "
        return self.inline(node)

    def figure_cue(self, node: Node) -> str:
        caption = node.first("figcaption")
        if caption:
            self.warnings.append("figure narrated as its caption only")
            return "[FIGURE: %s]" % normalize(self.inline(caption))
        img = node.first("img")
        if img and img.get("alt"):
            self.warnings.append("figure narrated as its caption only")
            return "[FIGURE: %s]" % normalize(img.get("alt"))
        svg = node if node.tag == "svg" else node.first("svg")
        if svg:
            title = svg.first("title")
            label = normalize(title.text_content()) if title else ""
            self.warnings.append("diagram narrated as its title only")
            return "[DIAGRAM: %s]" % label if label else "[DIAGRAM]"
        self.warnings.append("figure without a caption")
        return "[FIGURE]"

    def list_text(self, node: Node, depth: int = 0) -> str:
        ordered = node.tag == "ol"
        try:
            number = int(node.get("start") or 1)
        except ValueError:
            number = 1
        items = []
        for child in node.children:
            if child.is_text or child.tag != "li":
                continue
            body = self.inline(child)
            marker = "(%d)" % number if ordered else "-"
            items.append("%s %s" % (marker, normalize(body)))
            number += 1
        return "\n".join(items)


# ----------------------------------------------------------------------------- blocks
def _lead_element(node: Node) -> Optional[Node]:
    """The <strong>/<em> that opens a paragraph, if nothing but whitespace precedes it."""
    for child in node.children:
        if child.is_text:
            if child.text.strip():
                return None
            continue
        return child if child.tag in ("strong", "b", "em", "i") else None
    return None


def _paragraph(node: Node, r: Renderer) -> Block:
    r.ended = None
    text = r.inline(node)
    block = Block("p", text, ends=r.ended)
    lead = _lead_element(node)
    if lead is not None:
        label = normalize(lead.text_content())
        if lead.tag in ("strong", "b"):
            match = ENV_RE.match(label)
            kind = None
            number = ""
            if match and match.group(1).lower() in ENV_KINDS:
                kind, number = match.group(1), match.group(2)
            else:
                match = ENV_UNNUMBERED_RE.match(label)
                if match and match.group(1).lower() in ENV_KINDS:
                    kind = match.group(1)
            if kind:
                rest = normalize(text)[len(label):] if normalize(text).startswith(label) else ""
                name_match = ENV_NAME_RE.match(rest)
                block.env = {
                    "kind": kind.lower(),
                    "label": number,
                    "name": normalize(name_match.group(1)) if name_match else "",
                }
            elif r.numbered_labels:
                match = NUMBERED_RE.match(label)
                if match:
                    block.env = {
                        "kind": "numbered",
                        "label": match.group(1),
                        "name": (match.group(2) or "").rstrip(".").strip(),
                    }
        elif PROOF_RE.match(label):
            block.proof = True
    return block


def _walk(node: Node, out: list, r: Renderer) -> None:
    for child in node.children:
        if child.is_text:
            if child.text.strip():
                r.ended = None
                text = r.text(child.text)
                only_math = TOKEN.sub("", text).strip() == "" and TOKEN.search(text)
                kind = "display" if only_math else "p"
                out.append(Block(kind, text, ends=r.ended))
            continue
        tag = child.tag
        if tag in ("script", "style", "template", "noscript"):
            continue
        if tag == "p":
            out.append(_paragraph(child, r))
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            out.append(Block("heading", r.inline(child), level=int(tag[1]), id=child.get("id") or ""))
        elif tag in ("ol", "ul"):
            r.ended = None
            out.append(Block("list", r.list_text(child), ends=r.ended))
        elif tag in ("figure", "img", "svg"):
            out.append(Block("figure", r.figure_cue(child)))
        elif tag == "table":
            r.warnings.append("table omitted")
            out.append(Block("table", "[TABLE omitted]"))
        elif tag == "pre":
            code = child.text_content().strip("\n")
            if code.count("\n") >= 3:
                r.warnings.append("code block omitted")
                out.append(Block("code", "[CODE omitted]"))
            else:
                out.append(Block("code", normalize(code)))
        elif tag == "div":
            ended = child.get("data-environment-end")
            if ended or child.has_class("math-environment-end"):
                # The QED lived in the display equation's \tag; token() already recorded it.
                if out and out[-1].ends is None:
                    out[-1].ends = "subproof" if ended == "subproof" else "proof"
                    out[-1].text += " [END SUBPROOF]" if ended == "subproof" else " [END PROOF]"
            elif child.has_class("footnotes"):
                r.warnings.append("footnotes omitted")
            elif child.has_class("post-explicit-entry-break") or child.has_class("post-structural-continuation"):
                continue
            else:
                _walk(child, out, r)
        elif tag in ("hr", "br"):
            continue
        elif tag in ("blockquote", "section", "article", "main", "aside", "details", "dl", "dd", "dt", "summary"):
            _walk(child, out, r)
        else:
            out.append(Block("p", r.inline(child)))


# ----------------------------------------------------------------------------- sections
def _env_id(env: dict, counter: dict) -> str:
    kind = env["kind"]
    if env["label"]:
        return "%s-%s" % (kind, env["label"].replace(".", "-"))
    counter[kind] = counter.get(kind, 0) + 1
    return "%s-%d" % (kind, counter[kind])


def _env_title(env: dict) -> str:
    if env["kind"] == "numbered":
        return env["label"] + "." + (" " + env["name"] if env["name"] else "")
    title = env["kind"].capitalize()
    if env["label"]:
        title += " " + env["label"]
    if env["name"]:
        title += " (%s)" % env["name"]
    return title


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def _prose_title(text: str, limit: int = 60) -> str:
    """First words of a transitional paragraph, for chapter lists."""
    plain = TOKEN.sub("…", text)      # placeholders carry no TeX here; keep titles plain
    plain = normalize(plain).replace(" …", " …")
    sentence = re.split(r"(?<=[.!?])\s", plain, 1)[0]
    if len(sentence) <= limit:
        return sentence
    cut = sentence[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def _split_prose(section: Section) -> list:
    """An environment section -> [statement(+proof) section, prose section?]."""
    blocks = section.blocks
    boundary = None
    last_end = -1
    for i, block in enumerate(blocks):
        if block.ends:
            last_end = i
    if last_end >= 0:
        # Everything after the QED is the author's transition to the next result.
        if last_end + 1 < len(blocks):
            boundary = last_end + 1
    elif not any(b.proof for b in blocks):
        for i in range(1, len(blocks)):
            block, prev = blocks[i], blocks[i - 1]
            if block.kind != "p":
                continue
            first = TOKEN.sub("", block.text).strip()[:1]
            if prev.kind == "display" or (first and first.islower()):
                continue          # finishes the statement's sentence
            boundary = i
            break
    if boundary is None:
        return [section]
    prose = Section(
        id="prose-after-%s" % section.id, title=_prose_title(blocks[boundary].text),
        kind="prose", level=section.level,
    )
    prose.blocks = blocks[boundary:]
    section.blocks = blocks[:boundary]
    return [section, prose]


def _assemble(blocks: list) -> list:
    sections: list = []
    current: Optional[Section] = None
    counter: dict = {}
    heading_level = 1

    for block in blocks:
        if block.kind == "heading":
            title = normalize(block.text)
            heading_level = block.level
            current = Section(
                id=block.id or _slug(title), title=title, kind="heading",
                level=block.level, anchor=block.id or None,
            )
            if title.lower().rstrip(".") in REFERENCE_TITLES or block.id == "references":
                current.skip = "reference list"
            sections.append(current)
        elif block.env:
            env_id = _env_id(block.env, counter)
            current = Section(
                id=env_id, title=_env_title(block.env),
                kind=block.env["kind"], level=heading_level + 1,
                label=block.env["label"], name=block.env["name"],
                # The site's assets/js/main.js (addAnchorTargets) gives every numbered label
                # this same id client-side, so `#theorem-2-2-3` resolves on the live page.
                anchor=env_id if block.env["label"] and block.env["kind"] != "numbered" else None,
            )
            sections.append(current)
        if current is None:
            current = Section(id="introduction", title="Introduction", kind="introduction", level=heading_level + 1)
            sections.append(current)
        if block.proof:
            current.has_proof = True
        current.blocks.append(block)

    out: list = []
    for section in sections:
        if section.kind in ("heading", "introduction", "numbered"):
            out.append(section)          # a numbered part runs until the next one
        else:
            out.extend(_split_prose(section))
    return out


def _finish(section: Section, math: list) -> None:
    """Number the section's math from 1, splice the TeX in, hash the result."""
    count = [0]

    def splice(match: "re.Match") -> str:
        tex, display = math[int(match.group(1))]
        count[0] += 1
        fmt = "TeX display" if display else "TeX"
        return "[MATH %d; %s] %s [/MATH]" % (count[0], fmt, tex)

    parts = []
    for block in section.blocks:
        text = block.text
        if block.kind == "list":
            text = "\n".join(normalize(line) for line in text.split("\n"))
        else:
            text = normalize(text)
        text = re.sub(r"\s+([,.;:!?)])", r"\1", text)
        text = re.sub(r"\(\s+", "(", text)
        if text:
            parts.append(text)
    body = "\n\n".join(parts)
    body = TOKEN.sub(splice, body)
    section.text = body
    section.math = count[0]
    section.words = word_count(body)
    section.hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    section.blocks = []


# ----------------------------------------------------------------------------- document
def _meta(root: Node, prop: str) -> str:
    node = root.find(lambda n: n.tag == "meta" and (n.get("property") == prop or n.get("name") == prop))
    return (node.get("content") or "") if node else ""


def build(html: str, source: str = "") -> Skeleton:
    root = parse_html(html)
    article = root.find(lambda n: n.tag == "article" and n.has_class("post"))
    body = root.find(lambda n: n.tag == "div" and n.has_class("post-body"))
    if article is None or body is None:
        raise SkeletonError("not a post: no <article class=\"post\"> with a .post-body (%s)" % source)

    html_node = root.first("html")
    canonical = root.find(lambda n: n.tag == "link" and n.get("rel") == "canonical")
    url = (canonical.get("href") or "") if canonical else ""
    url = re.sub(r"^https?://[^/]+", "", url) or source
    h1 = article.first("h1")
    title = normalize(h1.text_content()) if h1 else normalize((root.first("title") or Node()).text_content() or "")
    modified = ""
    ld = root.find(lambda n: n.tag == "script" and n.get("type") == "application/ld+json")
    if ld:
        try:
            modified = json.loads(ld.text_content()).get("dateModified", "") or ""
        except (ValueError, AttributeError):
            modified = ""

    domain = (body.get("data-post-domain") or "").strip().lower()
    r = Renderer(numbered_labels=domain in NUMBERED_DOMAINS)
    blocks: list = []
    _walk(body, blocks, r)
    sections = _assemble(blocks)
    for section in sections:
        _finish(section, r.math)

    narrated = [s for s in sections if not s.skip]
    doc_hash = hashlib.sha256("\n".join(s.hash for s in narrated).encode("ascii")).hexdigest()
    warnings = sorted(set(r.warnings))
    return Skeleton(
        url=url, title=title,
        lang=(html_node.get("lang") if html_node else "") or "",
        scope=article.get("data-reference-scope") or "",
        published=_meta(root, "article:published_time")[:10],
        published_at=_meta(root, "article:published_time"),
        modified=modified[:10],
        description=normalize(_meta(root, "description")),
        narrate=_meta(root, "narrate").strip().lower() == "true",
        sections=sections, hash=doc_hash,
        math=sum(s.math for s in narrated), words=sum(s.words for s in narrated),
        warnings=warnings,
    )


# ----------------------------------------------------------------------------- views
def render_text(skel: Skeleton) -> str:
    lines = [
        "# %s" % skel.title,
        "url: %s   lang: %s   scope: %s   published: %s   modified: %s" % (
            skel.url, skel.lang or "-", skel.scope or "-", skel.published or "-", skel.modified or "-"),
        "sections: %d (%d narrated)   math: %d   words: %d   hash: %s" % (
            len(skel.sections), sum(1 for s in skel.sections if not s.skip), skel.math, skel.words, skel.hash[:12]),
    ]
    if skel.warnings:
        lines.append("warnings: " + "; ".join(skel.warnings))
    for i, s in enumerate(skel.sections, 1):
        lines.append("")
        head = "## [%d] %s" % (i, s.title)
        meta = "id=%s  hash=%s  math=%d  words=%d" % (s.id, s.hash[:12], s.math, s.words)
        if s.has_proof:
            meta += "  proof"
        if s.skip:
            meta += "  SKIPPED (%s)" % s.skip
        lines.append(head)
        lines.append("   " + meta)
        lines.append("")
        lines.append(s.text)
    return "\n".join(lines) + "\n"


def glossary_source(skel: Skeleton) -> str:
    """The whole narrated document as one stream — what the notation pass reads."""
    return "\n\n".join(s.text for s in skel.sections if not s.skip)
