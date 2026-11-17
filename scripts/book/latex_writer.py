"""
A built post (the HTML _docs/STRUCTURE.md describes) -> the LaTeX it mirrors.

document_structure.rb has already given each post the shape of a LaTeX document: a
statement, a proof or a run-in heading arrives as a <section data-doc="..."> unit, with
the number the author typed. This module walks that tree and writes the LaTeX back out.
It never works out again where a unit ends, and it never numbers anything: a head is
printed as its label reads.

What the browser adds on top of the HTML (assets/js/main.js, mathjax-config.js) is
mirrored here, since it is part of how a post reads:

- a source soft line in a paragraph of the body or of a unit is a paragraph of its own;
- one blank line after display math continues the paragraph, two start a new one
  (the `post-structural-continuation` marker);
- ordered lists are labelled (1), (a), (i), (A) by depth, with their `marker-prefix`;
- `Theorem 2.1.6` in prose links to that statement when the book has it, and a bare
  `2.1.6` when exactly one statement has that number (main.js's referencePattern).

MathJax sets `align` and its kin without numbers (the site gives it no `tags`), so they
come out starred. Diagrams stay TikZ: the book's site build turns the renderer off
(`tikzcd: enabled: false`), so `$$ \\begin{tikzcd} ... $$` arrives as the display math it
was written as.

Stdlib only, Python 3.9+ (scripts/ run on macOS's /usr/bin/python3).
"""
from __future__ import annotations

import re
from typing import Callable, Dict, List, Optional, Tuple

from _narrator.htmltree import Node

# main.js's referencePattern: a statement number, with or without its kind before it.
REFERENCE_KINDS = ("Definition", "Theorem", "Lemma", "Corollary", "Proposition", "Remark",
                   "Example", "Principle", "Exercise")
REFERENCE_RE = re.compile(r"\b(?:(%s)\s+)?(\d+(?:\.\d+)+)\b" % "|".join(REFERENCE_KINDS))
LABEL_RE = re.compile(r"^(%s)\s+(\d+(?:\.\d+)+)$" % "|".join(REFERENCE_KINDS))

BLOCK_TAGS = {"p", "ol", "ul", "section", "div", "figure", "pre", "blockquote", "table",
              "h1", "h2", "h3", "h4", "h5", "h6", "hr"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

# Math as kramdown leaves it in text: span math `\(…\)` (kept with the text around it),
# display math `\[…\]` or `$$…$$`, or a bare amsmath environment.
MATH_TOKEN_RE = re.compile(
    r"(?P<inline>\\\((?P<span>.*?)\\\))"
    r"|\\\[(?P<bracket>.*?)\\\]"
    r"|\$\$(?P<dollars>.*?)\$\$"
    r"|(?P<environment>\\begin\{(?P<name>[A-Za-z]+\*?)\}.*?\\end\{(?P=name)\})",
    re.S,
)
# amsmath's display environments, which LaTeX will not take inside \[ \] as MathJax does.
DISPLAY_ENVIRONMENT_RE = re.compile(
    r"^\s*\\begin\{(align|alignat|gather|multline|flalign|equation)\*?\}(.*)"
    r"\\end\{\1\*?\}\s*(.*?)\s*$",
    re.S,
)
# The QED written as an equation tag: `\tag*{\(\square\)}`, `\tag*{$\blacksquare$}`.
TAG_QED_RE = re.compile(
    r"\\tag\*\{\s*(?:\\\(|\$)\s*\\(?:square|blacksquare)\s*(?:\\\)|\$)\s*\}")

SOFT_BREAK = "\x00"  # a soft line inside a paragraph: a paragraph of its own

TEXT_SPECIALS = {
    "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#",
    "%": r"\%", "_": r"\_", "^": r"\^{}", "~": r"\textasciitilde{}", "\u00a0": "~",
}


def escape_text(text: str) -> str:
    return "".join(TEXT_SPECIALS.get(char, char) for char in text)


def collapse_space(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def top_level_math_commas(tex: str) -> int:
    """Count literal commas outside TeX groups; control symbols such as \\, and
    escaped braces are single tokens, not punctuation or grouping instructions."""
    depth = 0
    commas = 0
    escaped = False
    for char in tex:
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            commas += 1
    return commas


def display_math(tex: str, in_proof: bool) -> str:
    """One display formula: \\[ \\] around it, or the amsmath environment it already is."""
    tex = re.sub(r"\n\s*\n", "\n", tex.strip())  # TeX ends a formula at a blank line
    if in_proof:
        tex = TAG_QED_RE.sub(lambda _match: r"\qedhere", tex)
    environment = DISPLAY_ENVIRONMENT_RE.match(tex)
    if environment:
        name, body, trailing = environment.groups()
        body = body.rstrip()
        if trailing:  # `\end{align}.` — the period belongs to the last line
            body += trailing
        return "\\begin{%s*}%s\n\\end{%s*}" % (name, body, name)
    return "\\[\n%s\n\\]" % tex


def ancestors(node: Node, stop: Optional[Node] = None):
    parent = node.parent
    while parent is not None and parent is not stop:
        yield parent
        parent = parent.parent


def first_element(node: Node) -> Optional[Node]:
    for child in node.children:
        if child.is_text:
            if child.text.strip():
                return None
            continue
        return child
    return None


def without(node: Node, removed: Node) -> Node:
    """A copy of `node`, one level deep, without the child `removed`."""
    copy = Node(node.tag, dict(node.attrs), parent=node.parent)
    copy.children = [child for child in node.children if child is not removed]
    return copy


def has_content(node: Node) -> bool:
    return any(not child.is_text or child.text.strip() for child in node.children)


def label_text(label: Node) -> str:
    """A label's words without its statement name or final period: `Theorem 4.2.4`,
    `Proof`, `1`."""
    parts = []
    for node in label.iter():
        if node.is_text and not any(a.tag == "span" and a.has_class("math-statement-name")
                                    for a in ancestors(node, label)):
            parts.append(node.text)
    return collapse_space("".join(parts)).strip().rstrip(".").strip()


def is_statement_label(node: Node) -> bool:
    return node.tag in ("strong", "b") and node.has_class("math-label-anchor")


def reference_targets(posts: List[Tuple[str, Node]]) -> Dict[str, Optional[str]]:
    """{`Theorem 2.1.6` or `2.1.6`: LaTeX label}, over the whole book as
    reference_label_targets.rb builds it over a textbook. A bare number counts only when a
    single statement has it; one that several share maps to None."""
    labelled: Dict[str, Optional[str]] = {}
    numbers: Dict[str, Optional[str]] = {}
    for key, body in posts:
        for label in body.find_all(is_statement_label):
            match = LABEL_RE.match(label_text(label))
            if not match or not label.get("id"):
                continue
            target = "%s:%s" % (key, label.get("id"))
            for table, name in ((labelled, "%s %s" % match.groups()), (numbers, match.group(2))):
                table[name] = None if name in table and table[name] != target else target
    for number, target in numbers.items():
        labelled.setdefault(number, target)
    return labelled


class PostWriter:
    """One post's body as LaTeX.

    `key` prefixes the post's labels (`vector-spaces:theorem-2-1-6`); `targets` resolves
    references in prose (reference_targets); `resolve_link` turns a site URL into a label
    of the book, or None for a page the book does not hold."""

    def __init__(self, key: str, targets: Dict[str, Optional[str]],
                 resolve_link: Callable[[str], Optional[str]], *, index_terms: bool = True,
                 line_indent: bool = True, site_url: str = ""):
        self.key = key
        self.targets = targets
        self.resolve_link = resolve_link
        self.index_terms = index_terms
        self.line_indent = line_indent
        self.site_url = site_url.rstrip("/")
        self.footnotes: Dict[str, Node] = {}
        self.warnings: List[str] = []
        self.proof_depth = 0
        self.definition_depth = 0

    def warn(self, message: str) -> None:
        if message not in self.warnings:
            self.warnings.append(message)

    # -- entry point --------------------------------------------------------------
    def write(self, body: Node) -> str:
        for note in body.find_all(lambda n: n.tag == "li" and (n.get("id") or "").startswith("fn:")):
            self.footnotes[note.get("id")] = note
        return self.blocks(body.children, unit=False)

    # -- blocks ---------------------------------------------------------------------
    def blocks(self, nodes: List[Node], unit: bool, soft_lines: bool = True) -> str:
        """Block content: paragraphs, displays, lists and units, joined the way the page
        sets them. `unit` is True inside a statement, a proof or a list item, whose
        paragraphs are flush after a list (post.css); in the body such a paragraph is
        indented. `soft_lines` makes each source line of a paragraph a paragraph of its
        own, which main.js does in the body and in units, not in list items or footnotes."""
        parts: List[Tuple[str, str, str]] = []  # (kind, LaTeX, how it was separated)
        marked = False  # a two- or three-blank-line marker came before the next paragraph
        inline_run: List[Node] = []

        def add_paragraphs(paragraph: Node) -> None:
            nonlocal marked
            for index, text in enumerate(self.paragraphs(paragraph, soft_lines)):
                parts.append(("par", text, "soft" if index else ("marked" if marked else "")))
            marked = False

        def flush_inline() -> None:
            if inline_run:
                paragraph = Node("p")
                paragraph.children = list(inline_run)
                inline_run.clear()
                add_paragraphs(paragraph)

        for node in nodes:
            if node.is_text:
                for kind, piece in self.split_display(node.text):
                    if kind == "display":
                        flush_inline()
                        parts.append(("display", display_math(piece, self.proof_depth > 0), ""))
                    elif piece.strip() or inline_run:
                        inline_run.append(Node(text=piece, parent=node.parent))
                continue
            if node.tag not in BLOCK_TAGS:
                inline_run.append(node)
                continue
            flush_inline()

            classes = node.classes()
            if "post-structural-continuation" in classes or "post-explicit-entry-break" in classes:
                marked = True
            elif "math-environment-end" in classes or "footnotes" in classes:
                pass
            elif node.tag == "p":
                if has_content(node):
                    add_paragraphs(node)
            elif node.tag in ("ol", "ul"):
                parts.append(("list", self.list_environment(node), ""))
            elif node.tag == "section":
                parts.append(("unit", self.unit(node), ""))
            elif node.tag == "figure":
                parts.append(("display", self.figure(node), ""))
            elif node.tag == "pre":
                parts.append(("display", self.preformatted(node), ""))
            elif node.tag == "blockquote":
                inner = self.blocks(node.children, unit=False)
                parts.append(("unit", "\\begin{quote}\n%s\n\\end{quote}" % inner, ""))
            elif node.tag in HEADING_TAGS:
                parts.append(("unit", self.heading(node), ""))
            elif node.tag == "hr":
                parts.append(("unit", "\\sectionbreak", ""))
            elif node.tag == "table":
                parts.append(("unit", self.table(node), ""))
            else:  # a <div> of something else: its content
                inner = self.blocks(node.children, unit=unit, soft_lines=soft_lines)
                if inner.strip():
                    parts.append(("unit", inner, ""))
        flush_inline()
        return self.join(parts, unit)

    def join(self, parts: List[Tuple[str, str, str]], unit: bool) -> str:
        out = ""
        previous = None
        for kind, text, separated in parts:
            if previous is None:
                separator = ""
            elif kind in ("display", "list") and previous in ("par", "display", "list"):
                separator = "\n"  # a display or a list belongs to the paragraph before it
            elif kind == "par" and not separated and previous == "display":
                separator = "\n"  # one blank line after display math continues the sentence
            elif kind == "par" and not separated and previous == "list" and unit:
                separator = "\n"
            elif kind == "par" and previous == "par" and not separated and not self.line_indent:
                separator = "\n\n\\medskip\n"  # line_indent: false keeps a line between paragraphs
            else:
                separator = "\n\n"
            out += separator + text
            previous = kind
        return out

    def split_display(self, text: str) -> List[Tuple[str, str]]:
        """Text between blocks, cut into its display formulas and the text around them."""
        pieces = []
        position = 0
        for match in MATH_TOKEN_RE.finditer(text):
            if match.group("inline") is not None:
                continue
            if match.start() > position:
                pieces.append(("text", text[position:match.start()]))
            body = next(group for group in (match.group("bracket"), match.group("dollars"),
                                            match.group("environment")) if group is not None)
            pieces.append(("display", body))
            position = match.end()
        if position < len(text):
            pieces.append(("text", text[position:]))
        return pieces

    def paragraphs(self, paragraph: Node, soft_lines: bool = True) -> List[str]:
        """A <p>, as one paragraph per source line when `soft_lines` (main.js's softLineBreaks)."""
        text = self.inline(paragraph.children, soft=soft_lines)
        pieces = [piece.strip() for piece in text.split(SOFT_BREAK)]
        return [piece for piece in pieces if piece]

    # -- units ------------------------------------------------------------------------
    def unit(self, section: Node) -> str:
        classes = section.classes()
        if "doc-section--heading" in classes:
            return self.blocks(section.children, unit=False)
        if "doc-section--run-in" in classes or "doc-section--numbered" in classes:
            return self.run_in_section(section)
        if section.get("data-doc") == "proof":
            return self.proof(section)
        if "math-environment" in classes:
            return self.statement(section)
        return self.blocks(section.children, unit=False)

    def opening(self, section: Node, is_label: Callable[[Node], bool], *, consume_period: bool = False):
        """The unit's label, and the unit's children with the label taken out of the
        paragraph it opens."""
        for index, child in enumerate(section.children):
            if child.is_text:
                continue
            if child.tag != "p":
                break
            label = first_element(child)
            if label is None or not is_label(label):
                break
            rest = without(child, label)
            if consume_period:
                # `*Proof*.` puts the marker's punctuation outside the emphasis.
                # Copy its text node too: the HTML tree is shared by style builds.
                for position in range(child.children.index(label), len(rest.children)):
                    part = rest.children[position]
                    if not part.is_text:
                        break
                    text, count = re.subn(r"^(\s*)\.", r"\1", part.text, count=1)
                    if count:
                        rest.children[position] = Node(text=text, parent=rest)
                        break
                    if part.text.strip():
                        break
            return label, section.children[:index] + [rest] + section.children[index + 1:]
        return None, list(section.children)

    def statement(self, section: Node) -> str:
        label, children = self.opening(section, is_statement_label)
        style = "plain" if section.has_class("math-statement-italic") else "definition"
        kind = section.get("data-environment-kind") or "Statement"
        if label is None:
            self.warn("a %s without its label" % kind)
            head, note = kind, None
        else:
            head = label_text(label)
            note = self.statement_name(label, section, children)

        definition = section.get("data-doc") == "definition"
        self.definition_depth += definition
        body = self.blocks(children, unit=True)
        self.definition_depth -= definition

        begin = "\\begin{statement}{%s}{%s}" % (style, escape_text(head))
        if note:
            begin += "[{%s}]" % note
        if label is not None and label.get("id"):
            begin += "\\unitlabel{%s:%s}" % (self.key, label.get("id"))
        if body.startswith(("\\begin{enumerate}", "\\begin{itemize}", "\\[", "\\begin{align",
                            "\\begin{gather")):
            begin += "\\leavevmode"  # the head keeps a line of its own, as on the page
        return "%s\n%s\n\\end{statement}" % (begin, body)

    def statement_name(self, label: Node, section: Node, children: List[Node]) -> Optional[str]:
        name = label.find(lambda n: n.tag == "span" and n.has_class("math-statement-name"))
        if name is not None:
            text = self.inline(name.children, references=False).strip()
            return text[1:-1].strip() if text.startswith("(") and text.endswith(")") else text
        written = section.get("data-name")
        if not written:
            return None
        # The older form, the name after the label: `**Theorem 2.2.20** (Heine–Borel theorem).`
        for child in children:
            if child.is_text or child.tag != "p":
                continue
            first = child.children[0] if child.children else None
            if first is not None and first.is_text:
                match = re.match(r"\s*\(%s\)\.?" % re.escape(written), first.text)
                if match:
                    child.children[0] = Node(text=first.text[match.end():], parent=child)
                    return escape_text(written)
            break
        return None

    def proof(self, section: Node) -> str:
        marker, children = self.opening(
            section, lambda n: n.tag in ("em", "i") and n.has_class("math-proof-marker"),
            consume_period=True)
        kind = section.get("data-environment-kind") or "Proof"
        head = label_text(marker) if marker is not None else kind
        has_qed = section.find(lambda n: n.has_class("qed") or n.has_class("math-environment-end")) \
            is not None or any(TAG_QED_RE.search(n.text) for n in section.iter() if n.is_text)

        self.proof_depth += 1
        body = self.blocks(children, unit=True)
        self.proof_depth -= 1

        environment = "subproof" if kind == "Subproof" else "proof"
        begin = "\\begin{%s}" % environment
        if head != environment.capitalize():
            begin += "[%s]" % escape_text(head)
        if not has_qed:
            begin += "\\noqed"  # the page shows none
            if kind != "Solution":
                self.warn("the %s of %s ends without a QED mark" % (
                    head.lower(), section.get("data-proves") or "a statement"))
        return "%s\n%s\n\\end{%s}" % (begin, body, environment)

    def run_in_section(self, section: Node) -> str:
        label, children = self.opening(
            section, lambda n: n.tag in ("strong", "b") and n.has_class("doc-heading"))
        if label is None:
            return self.blocks(section.children, unit=False)
        title = self.inline(label.children, references=False).strip()
        anchor = "\\unitlabel{%s:%s}" % (self.key, label.get("id")) if label.get("id") else ""
        return "\\bookruninhead{%s}%s\n%s" % (title, anchor, self.blocks(children, unit=False))

    def heading(self, heading: Node) -> str:
        level = int(heading.tag[1])
        command = {1: "section*", 2: "booksubsectionhead", 3: "subsubsection*"}.get(level, "paragraph*")
        title = self.inline(heading.children, references=False).strip()
        anchor = "\\unitlabel{%s:%s}" % (self.key, heading.get("id")) if heading.get("id") else ""
        return "\\%s{%s}%s" % (command, title, anchor)

    # -- lists, figures, tables -----------------------------------------------------------
    def list_environment(self, node: Node) -> str:
        options = []
        if node.tag == "ol":
            depth = 1 + sum(1 for a in ancestors(node) if a.tag == "ol")
            prefix = (node.get("marker-prefix") or node.get("data-marker-prefix") or "").strip()
            style = (node.get("marker-style") or node.get("data-marker-style") or "").strip().lower()
            if not style and (node.has_class("reference") or "reference" in node.attrs):
                style = "reference"
            counter = ("\\arabic*", "\\alph*", "\\roman*", "\\Alph*")[(depth - 1) % 4]
            if style == "reference":
                options.append("label={[\\arabic*]}")
            elif prefix:
                options.append("label={(%s%s)}" % (escape_text(prefix), counter))
            start = node.get("start")
            if start and start.isdigit() and start != "1":
                options.append("start=%s" % start)
            environment = "enumerate"
        else:
            environment = "itemize"
        items = []
        for child in node.children:
            if not child.is_text and child.tag == "li":
                body = self.blocks(child.children, unit=True, soft_lines=False)
                items.append("\\item %s" % self.item_body(body))
        return "\\begin{%s}%s\n%s\n\\end{%s}" % (
            environment, "[%s]" % ", ".join(options) if options else "", "\n".join(items), environment)

    def item_body(self, body: str) -> str:
        # An item that opens with its formula: set the formula on the label's line, centred
        # as the page centres it, rather than leave the label alone on a line above it.
        match = re.match(r"\\\[\n(.*?)\n\\\](.*)\Z", body, re.S)
        if match and "\\\\" not in match.group(1) and "\\tag" not in match.group(1):
            return "\\hfill$\\displaystyle %s$\\hfill\\null%s" % (match.group(1), match.group(2))
        return body

    def figure(self, node: Node) -> str:
        if node.has_class("commutative-diagram"):
            self.warn("a diagram arrived as SVG: build the site with the book's config, "
                      "which keeps it TikZ")
        else:
            self.warn("a <figure> the book cannot set")
        return "\\[\\text{[figure]}\\]"

    def preformatted(self, node: Node) -> str:
        code = node.find(lambda n: n.tag == "code")
        language = ""
        for name in (code.classes() if code is not None else []):
            if name.startswith("language-"):
                language = name[len("language-"):]
        text = (code or node).text_content()
        if language == "tikzcd":  # the concise ```tikzcd form (tikzcd_renderer.rb)
            return "\\[\n\\begin{tikzcd}\n%s\n\\end{tikzcd}\n\\]" % text.rstrip()
        return "\\begin{verbatim}\n%s\n\\end{verbatim}" % text.rstrip("\n")

    def table(self, node: Node) -> str:
        rows = node.find_all(lambda n: n.tag == "tr")
        if not rows:
            return ""
        lines = []
        width = 0
        for row in rows:
            cells = [c for c in row.children if not c.is_text and c.tag in ("td", "th")]
            width = max(width, len(cells))
            texts = [self.inline(cell.children).strip() for cell in cells]
            if cells and all(cell.tag == "th" for cell in cells):
                texts = ["\\textbf{%s}" % text for text in texts]
            lines.append(" & ".join(texts) + " \\\\")
        return "\\begin{center}\n\\begin{tabular}{%s}\n%s\n\\end{tabular}\n\\end{center}" % (
            "l" * width, "\n".join(lines))

    # -- inline ---------------------------------------------------------------------------
    def inline(self, nodes: List[Node], *, soft: bool = False, references: bool = True) -> str:
        return "".join(self.text(node.text, soft=soft, references=references) if node.is_text
                       else self.element(node, references) for node in nodes)

    def text(self, text: str, *, soft: bool, references: bool) -> str:
        out = []
        position = 0
        for match in MATH_TOKEN_RE.finditer(text):
            out.append(self.plain(text[position:match.start()], soft, references))
            if match.group("inline") is not None:  # kramdown's own span math
                out.append(self.math(match.group("span")))
            else:
                body = match.group("bracket") or match.group("dollars") or match.group("environment")
                out.append("\n%s\n" % display_math(body, self.proof_depth > 0))
            position = match.end()
        out.append(self.plain(text[position:], soft, references))
        return "".join(out)

    def plain(self, text: str, soft: bool, references: bool) -> str:
        if soft:
            text = re.sub(r"[ \t\r\f\v]*\n[ \t\r\f\v]*", SOFT_BREAK, text)
        text = re.sub(r"[ \t\r\n\f\v]+", " ", text)
        if not references:
            return escape_text(text)
        out = []
        position = 0
        for match in REFERENCE_RE.finditer(text):
            kind, number = match.groups()
            target = self.targets.get("%s %s" % (kind, number) if kind else number)
            if not target:
                if kind and self.targets.get(number):
                    self.warn("“%s %s” points at %s" % (
                        kind, number, self.targets[number].split(":")[-1]))
                continue
            out.append(escape_text(text[position:match.start()]))
            if kind:
                out.append("%s~" % kind)
            out.append("\\hyperref[%s]{%s}" % (target, number))
            position = match.end()
        out.append(escape_text(text[position:]))
        return "".join(out)

    @staticmethod
    def math(tex: str) -> str:
        tex = re.sub(r"\n\s*\n", "\n", tex)
        if top_level_math_commas(tex) >= 4:
            return "\\bookmath{%s}" % tex
        return "$%s$" % tex

    def element(self, node: Node, references: bool) -> str:
        tag = node.tag
        if tag == "span":
            if node.has_class("math-inline"):
                return self.math_span(node)
            if node.has_class("qed"):
                return self.qed(node)
            return self.inline(node.children, references=references)
        if tag in ("strong", "b"):
            return "\\textbf{%s}" % self.inline(node.children, references=False)
        if tag in ("em", "i"):
            emphasis = "\\emph{%s}" % self.inline(node.children, references=references)
            if self.index_terms and self.definition_depth and not self.proof_depth:
                emphasis += self.index_entry(node)
            return emphasis
        if tag == "sup":
            link = node.find(lambda n: n.tag == "a" and n.has_class("footnote"))
            if link is not None:
                return self.footnote((link.get("href") or "").lstrip("#"))
            return "\\textsuperscript{%s}" % self.inline(node.children, references=references)
        if tag == "sub":
            return "\\textsubscript{%s}" % self.inline(node.children, references=references)
        if tag == "a":
            return self.link(node)
        if tag in ("code", "kbd"):
            return "\\texttt{%s}" % escape_text(node.text_content())
        if tag == "br":
            return "\\newline "
        if tag in ("img", "svg"):
            self.warn("an <%s> the book leaves out" % tag)
            return ""
        if tag in ("script", "style"):
            return ""
        return self.inline(node.children, references=references)

    def math_span(self, node: Node) -> str:
        # `\(F\times V\to V\),`: inline_math_preprocessor.rb keeps the punctuation after a
        # formula in the formula's span (math-inline-punctuated), outside the formula.
        source = node.text_content()
        match = re.match(r"\s*\\\((.*)\\\)(.*?)\s*$", source, re.S)
        if not match:
            return escape_text(source)
        return self.math(match.group(1)) + escape_text(match.group(2))

    def qed(self, node: Node) -> str:
        if self.proof_depth:
            return "\\qedhere"
        return "\\qedsymbolhere{%s}" % (
            "\\blacksquare" if "blacksquare" in node.text_content() else "\\square")

    def footnote(self, note_id: str) -> str:
        note = self.footnotes.get(note_id)
        if note is None:
            self.warn("footnote %s has no text" % note_id)
            return ""
        saved = self.definition_depth
        self.definition_depth = 0  # a footnote defines nothing for the index
        text = self.blocks(note.children, unit=False, soft_lines=False)
        self.definition_depth = saved
        return "\\footnote{%s}" % text.replace("\n\n", "\\par ")

    def link(self, node: Node) -> str:
        if node.has_class("reversefootnote"):
            return ""
        href = node.get("href") or ""
        text = self.inline(node.children, references=False)
        if href.startswith("#"):
            return "\\hyperref[%s:%s]{%s}" % (self.key, href[1:], text) if href[1:] else text
        target = self.resolve_link(href)
        if target:
            return "\\hyperref[%s]{%s}" % (target, text)
        if href.startswith("/"):
            href = self.site_url + href
        if not re.match(r"[a-z][a-z0-9+.-]*:", href):
            return text
        return "\\href{%s}{%s}" % (href.replace("\\", "/").replace("%", "\\%").replace("#", "\\#"), text)

    def index_entry(self, node: Node) -> str:
        """A term a definition introduces, for the index: `\\index{sort key@entry}`."""
        source = node.text_content()
        plain = INLINE_MATH_STRIP_RE.sub(lambda m: re.sub(r"\\[A-Za-z]+|[{}^_]", "", m.group(1)), source)
        plain = collapse_space(plain).strip()
        if not plain or len(plain) > 48 or not re.search(r"[A-Za-z]", plain):
            return ""
        entry = self.inline(node.children, references=False).strip()

        def quote(text: str) -> str:
            return re.sub(r'([@!|"])', r'"\1', text)

        if plain.lower() == entry:
            return "\\index{%s}" % quote(entry)
        return "\\index{%s@%s}" % (quote(plain.lower()), quote(entry))


INLINE_MATH_STRIP_RE = re.compile(r"\\\((.*?)\\\)", re.S)
