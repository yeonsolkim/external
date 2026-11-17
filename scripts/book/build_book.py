#!/usr/bin/env python3
"""
Typeset one textbook of the site, the posts under one textbook folder, as a LaTeX book.

    python3 scripts/book/build_book.py                       # Linear Algebra
    python3 scripts/book/build_book.py "Linear Algebra" --open
    python3 scripts/book/build_book.py "Linear Algebra" --style springer
    python3 scripts/book/build_book.py "Linear Algebra" --style springer --section lattices
    python3 scripts/book/build_book.py "Introduction to Analysis" --drafts

1. Build the site into the book's cache with the TikZ renderer off, so that diagrams stay
   TikZ (`tikzcd: enabled: false`). Posts that are not `published` come in with --drafts.
2. Read each post's built page, whose structure _docs/STRUCTURE.md describes, and write it
   as a section of the book (latex_writer.py). A section folder is a chapter; numbers are
   the folders' and titles' own, as on the site.
3. Run latexmk (LuaLaTeX) on the result, set by the selected book class.

Everything goes to ~/Library/Caches/External-Jekyll/book/<textbook>/, the PDF included,
unless --output names another place for the PDF. Springer LaTeX lives in springer/tex;
single-section samples have their own samples/<section>/tex folder for each style.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.parse
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

BOOK_DIR = Path(__file__).resolve().parent
ROOT = BOOK_DIR.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import sync_posts_front_matter as sync  # noqa: E402
from _narrator.htmltree import Node, parse_html  # noqa: E402
from latex_writer import PostWriter, escape_text, reference_targets  # noqa: E402

CACHE = Path.home() / "Library" / "Caches" / "External-Jekyll" / "book"
KST = timezone(timedelta(hours=9))
# As scripts/site.zsh: Homebrew Ruby for Bundler, TeX for latexmk, from any launcher.
TOOL_PATH = ["/opt/homebrew/opt/ruby/bin", "/opt/homebrew/bin", "/Library/TeX/texbin", "/usr/local/bin"]
ORDER_RE = re.compile(r"^\s*((?:[IVXLCDM]+|\d+))[.)]\s*(.*)$", re.IGNORECASE)
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
BOOK_STYLES = {"external": "external-book", "springer": "external-springer-book"}


@dataclass
class Post:
    path: Path
    chapter_number: int
    chapter_title: str
    number: Optional[int]
    title: str
    url: str
    published: bool
    date: str
    source_note: Optional[str] = None
    line_indent: bool = True
    key: str = ""
    body: Optional[Node] = None
    anchors: Set[str] = field(default_factory=set)


# -- reading the posts --------------------------------------------------------------------
def order_number(text: str) -> Tuple[Optional[int], str]:
    """`2. Vector Spaces` -> (2, `Vector Spaces`); `III. Topology` -> (3, `Topology`)."""
    match = ORDER_RE.match(text)
    if not match:
        return None, text.strip()
    numeral, rest = match.groups()
    if numeral.isdigit():
        return int(numeral), rest.strip()
    total, previous = 0, 0
    for char in reversed(numeral.upper()):
        value = ROMAN[char]
        total += -value if value < previous else value
        previous = max(previous, value)
    return total, rest.strip()


def find_textbook(name: str) -> Path:
    wanted = name.strip().casefold()
    for folder in sorted(sync.POSTS_ROOT.rglob("*")):
        if folder.is_dir() and ".obsidian" not in folder.parts \
                and order_number(folder.name)[1].casefold() == wanted:
            return folder
    raise SystemExit("No textbook folder named %r under _posts." % name)


def front_matter_value(front_matter: str, key: str) -> Optional[str]:
    return sync.yaml_scalar(sync.top_level_entry(front_matter, key))


def read_posts(textbook: Path) -> List[Post]:
    entries = [sync.post_permalink_entry(path) for path in sync.post_paths(sync.POSTS_ROOT)]
    derived = sync.derived_permalinks(entries)
    frozen = {path: permalink for path, _, _, _, permalink in entries}

    posts = []
    for path in sync.post_paths(textbook):
        folders = path.parent.relative_to(textbook).parts
        if len(folders) != 1:
            print("  skipped %s: a book's posts sit in a section folder" % path.relative_to(ROOT))
            continue
        chapter_number, chapter_title = order_number(folders[0])
        text = path.read_text(encoding="utf-8")
        match = sync.FRONT_MATTER_RE.match(text)
        front_matter = match.group(1) if match else ""
        title = front_matter_value(front_matter, "title") or sync.DATE_PREFIX_RE.sub("", path.stem)
        number, title = order_number(title)
        posts.append(Post(
            path=path,
            chapter_number=chapter_number or 0,
            chapter_title=chapter_title,
            number=number,
            title=title,
            url=(frozen.get(path) or derived.get(path) or "").strip(),
            published=(front_matter_value(front_matter, "published") or "true").lower() != "false",
            date=path.name[:10],
            source_note=front_matter_value(front_matter, "source_note"),
            line_indent=(front_matter_value(front_matter, "line_indent") or "true").lower() != "false",
        ))
    # Numbered posts in their order; an unnumbered one (`Exercises`) after them, by date.
    posts.sort(key=lambda p: (p.chapter_number, p.chapter_title, p.number is None, p.number or 0, p.date))
    return posts


def site_config() -> Dict[str, str]:
    text = (ROOT / "_config.yml").read_text(encoding="utf-8")
    config = {}
    for key in ("title", "author", "url"):
        match = re.search(r"^%s:\s*(.*?)\s*$" % key, text, re.M)
        config[key] = match.group(1).strip().strip("\"'") if match else ""
    return config


# -- building ------------------------------------------------------------------------------
def tool_env() -> Dict[str, str]:
    import os

    env = dict(os.environ)
    env["PATH"] = ":".join(TOOL_PATH + [env.get("PATH", "")])
    env.setdefault("LANG", "en_US.UTF-8")
    return env


def build_site(build_dir: Path, drafts: bool) -> Path:
    site = build_dir / "site"
    config = build_dir / "book-config.yml"
    config.write_text("# scripts/book/build_book.py: the book takes the diagrams as TikZ.\n"
                      "tikzcd:\n  enabled: false\n", encoding="utf-8")
    env = tool_env()
    bundle = shutil.which("bundle", path=env["PATH"]) or "bundle"
    command = [bundle, "exec", "jekyll", "build", "--config", "_config.yml,%s" % config,
               "--destination", str(site)]
    if drafts:
        command.append("--unpublished")
    print("Building the site (diagrams as TikZ)…")
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    if result.returncode:
        print(result.stdout[-6000:], result.stderr[-6000:], sep="\n")
        raise SystemExit("jekyll build failed.")
    return site


def post_body(site: Path, post: Post) -> Optional[Node]:
    page = site / post.url.strip("/") / "index.html"
    if not page.is_file():
        return None
    root = parse_html(page.read_text(encoding="utf-8"))
    return root.find(lambda n: n.tag == "div" and n.has_class("post-body"))


def tikz_preamble() -> str:
    """What tikzcd_renderer.rb adds to TikZ (the `hasse` style), read from the plugin so the
    two cannot drift apart."""
    source = (ROOT / "_plugins" / "tikzcd_renderer.rb").read_text(encoding="utf-8")
    match = re.search(r"TIKZ_PREAMBLE = <<~'LATEX'\.strip\n(.*?)\n\s*LATEX\n", source, re.S)
    if not match:
        raise SystemExit("TIKZ_PREAMBLE not found in _plugins/tikzcd_renderer.rb.")
    return textwrap.dedent(match.group(1)).strip() + "\n"


def unmatched_mathjax_macros() -> List[str]:
    """Macros mathjax-config.js defines that site-macros.tex does not."""
    script = (ROOT / "assets" / "js" / "mathjax-config.js").read_text(encoding="utf-8")
    block = re.search(r"\bmacros:\s*\{(.*?)\n(\s*)\}", script, re.S)
    if not block:
        return []
    names = re.findall(r"^\s*([A-Za-z]+)\s*:", block.group(1), re.M)
    macros = (BOOK_DIR / "site-macros.tex").read_text(encoding="utf-8")
    return [name for name in names if not re.search(r"\\%s(?![A-Za-z])" % name, macros)]


# -- writing ------------------------------------------------------------------------------
def tex_title(text: str) -> str:
    """A title as LaTeX: its `$…$` math kept, plain text in the PDF bookmarks."""
    out = []
    for index, piece in enumerate(re.split(r"(\$[^$]+\$)", text)):
        if index % 2:
            plain = re.sub(r"\\[A-Za-z]+|[{}^_$]", "", piece)
            out.append("\\texorpdfstring{%s}{%s}" % (piece, escape_text(plain)))
        else:
            out.append(escape_text(piece))
    return "".join(out)


def tex_markdown(text: str) -> str:
    """The Markdown of a front matter value (source_note): emphasis, strong and math."""
    out = []
    for index, piece in enumerate(re.split(r"(\$[^$]+\$)", text)):
        if index % 2:
            out.append(piece)
            continue
        piece = escape_text(piece)
        piece = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", piece)
        piece = re.sub(r"(?<![\w*])[*_](?!\s)(.+?)(?<!\s)[*_](?![\w*])", r"\\emph{\1}", piece)
        out.append(piece)
    return "".join(out)


def make_resolver(posts: List[Post], site_url: str):
    by_path = {urllib.parse.urlsplit(post.url).path: post for post in posts}
    host = urllib.parse.urlsplit(site_url).netloc

    def resolve(href: str) -> Optional[str]:
        parts = urllib.parse.urlsplit(href)
        if parts.netloc and parts.netloc != host:
            return None
        path = parts.path if parts.path.endswith("/") else parts.path + "/"
        post = by_path.get(path)
        if post is None:
            return None
        if parts.fragment:
            return "%s:%s" % (post.key, parts.fragment) if parts.fragment in post.anchors else None
        return post.key

    return resolve


def anchors_of(body: Node) -> Set[str]:
    return {node.get("id") for node in body.find_all(
        lambda n: n.get("id") and (n.has_class("math-label-anchor") or n.has_class("doc-heading")
                                   or n.tag in ("h2", "h3", "h4", "h5", "h6")))}


def is_exercise_title(title: str) -> bool:
    return re.sub(r"\s+", " ", title).strip().rstrip(".:").casefold() in ("exercise", "exercises")


def book_body(body: Node) -> Node:
    """Project the site's semantic HTML into book content without changing the site.

    Exercise sections contain their problems and solutions, so remove the complete
    subtree before collecting reference targets, anchors or index terms.
    """
    def copy(node: Node, parent: Optional[Node] = None) -> Optional[Node]:
        if not node.is_text:
            kind = (node.get("data-environment-kind") or node.get("data-doc") or "").casefold()
            if kind == "exercise" or node.has_class("math-environment--exercise"):
                return None
            if node.tag == "section" and node.has_class("doc-section--heading"):
                heading = next((child for child in node.children if child.tag in
                                ("h1", "h2", "h3", "h4", "h5", "h6")), None)
                title = node.get("data-title") or (heading.text_content() if heading else "")
                if is_exercise_title(title):
                    return None
        result = Node(node.tag, dict(node.attrs), text=node.text, parent=parent)
        for child in node.children:
            retained = copy(child, result)
            if retained is not None:
                result.children.append(retained)
        return result

    return copy(body)


def section_tex(post: Post, writer: PostWriter) -> str:
    title = tex_title(post.title)
    if post.number is None:
        head = "\\section*{%s}\\addcontentsline{toc}{section}{%s}\\markright{%s}" % (title, title, title)
    else:
        head = "\\setcounter{section}{%d}\n\\section{%s}" % (post.number - 1, title)
    body = writer.write(post.body)
    if not post.line_indent:
        body = "\\begingroup\\setlength{\\parindent}{0pt}\n%s\n\\endgroup" % body
    lines = ["%% %s" % post.path.relative_to(ROOT), head + "\\unitlabel{%s}" % post.key, body]
    return "\n".join(lines) + "\n"


def write_book(posts: List[Post], tex_dir: Path, textbook_title: str, config: Dict[str, str],
               index: bool, style: str = "springer") -> Dict[str, List[str]]:
    posts = [replace(post, body=book_body(post.body)) for post in posts
             if not is_exercise_title(post.title)]
    if not posts:
        raise SystemExit("No book content remains after excluding exercises.")
    for post in posts:
        post.anchors = anchors_of(post.body)
    sections_dir = tex_dir / "sections"
    if sections_dir.exists():
        shutil.rmtree(sections_dir)
    sections_dir.mkdir(parents=True)

    targets = reference_targets([(post.key, post.body) for post in posts])
    resolve = make_resolver(posts, config["url"])
    warnings: Dict[str, List[str]] = {}
    inputs = []
    chapter = None
    for post in posts:
        if (post.chapter_number, post.chapter_title) != chapter:
            chapter = (post.chapter_number, post.chapter_title)
            inputs.append("\\setcounter{chapter}{%d}\n\\chapter{%s}" % (
                post.chapter_number - 1, tex_title(post.chapter_title)))
        writer = PostWriter(post.key, targets, resolve, index_terms=index,
                            line_indent=post.line_indent, site_url=config["url"])
        name = "%02d-%02d-%s" % (post.chapter_number, post.number or 99, post.key)
        (sections_dir / (name + ".tex")).write_text(section_tex(post, writer), encoding="utf-8")
        inputs.append("\\input{sections/%s}" % name)
        if writer.warnings:
            warnings["%s (%s)" % (post.title, post.path.name)] = writer.warnings

    now = datetime.now(KST)
    first_year = min(int(post.date[:4]) for post in posts)
    years = str(now.year) if first_year >= now.year else "%d–%d" % (first_year, now.year)
    (tex_dir / "tikz-preamble.tex").write_text(
        "%% From TIKZ_PREAMBLE in _plugins/tikzcd_renderer.rb\n" + tikz_preamble(), encoding="utf-8")
    master = r"""%% Written by scripts/book/build_book.py from the built site: edit the posts or
%% scripts/book/%(class)s.cls, not this file.
\documentclass{%(class)s}
\input{tikz-preamble}
\booktitle{%(title)s}
\bookauthor{%(author)s}
\booksite{%(site)s}{%(url)s}
\bookdate{%(date)s}
\bookyears{%(years)s}
%(makeindex)s
\begin{document}
\frontmatter
\maketitlepages
\tableofcontents
\mainmatter
%(inputs)s
\backmatter
%(printindex)s
\end{document}
""" % {
        "class": BOOK_STYLES[style],
        "title": tex_title(textbook_title),
        "author": escape_text(config["author"]),
        "site": escape_text(config["title"]),
        "url": config["url"],
        "date": "%s %d, %d" % (now.strftime("%B"), now.day, now.year),
        "years": years,
        "makeindex": "\\makebookindex" if index else "",
        "inputs": "\n".join(inputs),
        "printindex": "\\printindex" if index else "",
    }
    (tex_dir / "book.tex").write_text(master, encoding="utf-8")
    return warnings


def typeset(tex_dir: Path, jobname: str, style: str = "springer") -> Path:
    env = tool_env()
    env["TEXINPUTS"] = "%s:%s:%s" % (
        BOOK_DIR, BOOK_DIR / "vendor" / "springer", env.get("TEXINPUTS", ""))
    command = ["latexmk", "-lualatex", "-interaction=nonstopmode", "-halt-on-error",
               "-file-line-error", "-jobname=%s" % jobname]
    if style == "springer":
        command.extend(["-e", '$makeindex = "makeindex -s springer-hyperref.ist %O -o %D %S";'])
        env["INDEXSTYLE"] = "%s:%s:%s" % (
            BOOK_DIR, BOOK_DIR / "vendor" / "springer", env.get("INDEXSTYLE", ""))
        if not env["INDEXSTYLE"].endswith(":"):
            env["INDEXSTYLE"] += ":"  # retain the TeX distribution's default search path
        # latexmk watches .idx but does not notice a changed makeindex style.
        index_style = BOOK_DIR / "springer-hyperref.ist"
        index_output = tex_dir / (jobname + ".ind")
        if index_output.is_file() and index_style.stat().st_mtime_ns > index_output.stat().st_mtime_ns:
            index_output.unlink()
    command.append("book.tex")
    print("Typesetting with LuaLaTeX (latexmk)…")
    result = subprocess.run(command, cwd=tex_dir, env=env, capture_output=True, text=True)
    log_path = tex_dir / (jobname + ".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    if result.returncode:
        errors = re.findall(r"^(?:\S+:\d+: |! ).*(?:\n.*){0,3}", log, re.M)
        print("\n".join(errors[:5]) or result.stdout[-4000:])
        raise SystemExit("LaTeX failed; the log is %s" % log_path)
    report = {
        "overfull lines": len(re.findall(r"^Overfull \\hbox", log, re.M)),
        "undefined references": len(re.findall(r"Reference `[^']*' on page", log)),
        "unreferenced destinations": len(re.findall(r"unreferenced destination", log, re.I)),
        "missing characters": len(re.findall(r"Missing character", log)),
    }
    problems = ", ".join("%d %s" % (count, name) for name, count in report.items() if count)
    print("LaTeX: %s (log: %s)" % (
        problems or "no overfull lines, references, destinations or glyphs amiss", log_path))
    # Where a line runs into the margin: the section file open at the time, and its line.
    for match in re.finditer(r"^Overfull \\hbox \(([\d.]+)pt too wide\) "
                             r"(?:in paragraph at lines (\d+)--\d+|detected at line (\d+))", log, re.M):
        opened = re.findall(r"\(\./(sections/[^\s()]+\.tex)", log[:match.start()])
        print("  %.0fpt too wide: %s, line %s" % (
            float(match.group(1)), opened[-1] if opened else "book.tex", match.group(2) or match.group(3)))
    return tex_dir / (jobname + ".pdf")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("textbook", nargs="?", default="Linear Algebra",
                        help="the textbook folder's name, without its number (default: Linear Algebra)")
    parser.add_argument("--drafts", action="store_true", help="take posts that are not published as well")
    parser.add_argument("--style", choices=BOOK_STYLES, default="springer",
                        help="the book design (default: springer, 155 x 235 mm)")
    parser.add_argument("--section", help="typeset only the section with this permalink slug (e.g. lattices)")
    parser.add_argument("--no-index", action="store_true", help="leave out the index of defined terms")
    parser.add_argument("--tex-only", action="store_true", help="write the LaTeX, do not typeset it")
    parser.add_argument("--output", type=Path, help="where to put the PDF")
    parser.add_argument("--open", action="store_true", help="open the PDF when it is done")
    args = parser.parse_args()

    textbook = find_textbook(args.textbook)
    title = order_number(textbook.name)[1]
    slug = sync.slug(title)
    build_dir = CACHE / slug
    style_dir = build_dir if args.style == "external" else build_dir / args.style

    posts = read_posts(textbook)
    section = args.section.strip("/") if args.section is not None else None
    if section is not None:
        posts = [post for post in posts if post.url.strip("/").split("/")[-1] == section]
        if not posts:
            raise SystemExit("No section with permalink slug %r under %s." % (
                section, textbook.relative_to(ROOT)))
        style_dir = style_dir / "samples" / section
    left_out = [post for post in posts if not post.published and not args.drafts]
    posts = [post for post in posts if (post.published or args.drafts) and not is_exercise_title(post.title)]
    if not posts:
        raise SystemExit("No posts to typeset under %s." % textbook.relative_to(ROOT))

    tex_dir = style_dir / "tex"
    tex_dir.mkdir(parents=True, exist_ok=True)
    site = build_site(build_dir, args.drafts)
    keys: Set[str] = set()
    for post in list(posts):
        post.body = post_body(site, post)
        if post.body is None:
            print("  skipped %s: no page at %s" % (post.path.name, post.url))
            posts.remove(post)
            continue
        key = post.url.strip("/").split("/")[-1] or sync.slug(post.title)
        post.key = key if key not in keys else post.url.strip("/").replace("/", "-")
        keys.add(post.key)
        post.anchors = anchors_of(post.body)

    if not posts:
        raise SystemExit("No built pages to typeset under %s." % textbook.relative_to(ROOT))
    config = site_config()
    warnings = write_book(posts, tex_dir, title, config, index=not args.no_index, style=args.style)
    chapters = len({(p.chapter_number, p.chapter_title) for p in posts})
    print("%s: %d chapters, %d sections." % (title, chapters, len(posts)))
    for post in left_out:
        print("  left out (not published; --drafts takes it): %s" % post.title)
    for macro in unmatched_mathjax_macros():
        print("  \\%s is a MathJax macro (mathjax-config.js) that site-macros.tex does not define" % macro)
    for where, messages in warnings.items():
        for message in messages:
            print("  %s: %s" % (where, message))
    if args.tex_only:
        print("LaTeX: %s" % (tex_dir / "book.tex"))
        return 0

    pdf = typeset(tex_dir, slug, style=args.style)
    filename = title
    if section is not None:
        filename += " - " + posts[0].title
    if args.style == "springer":
        filename += " - Springer"
    filename += ".pdf"
    destination = args.output or style_dir / filename
    if args.output and args.output.is_dir():
        destination = args.output / filename
    shutil.copyfile(pdf, destination)
    print("PDF: %s" % destination)
    if args.open:
        subprocess.run(["open", str(destination)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
