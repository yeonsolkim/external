"""
A minimal DOM over the standard library's html.parser.

Stdlib on purpose: the skeleton is a cache-key dimension (every hash downstream is
derived from it), and a third-party parser changing its whitespace or entity handling
under us would silently rewrite every hash and regenerate every recording.
"""
from __future__ import annotations

from html.parser import HTMLParser
from typing import Callable, Iterator, Optional

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag: Optional[str] = None, attrs: Optional[dict] = None,
                 text: Optional[str] = None, parent: Optional["Node"] = None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children: list = []
        self.parent = parent
        self.text = text

    # -- identity -------------------------------------------------------------
    @property
    def is_text(self) -> bool:
        return self.tag is None

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        return self.attrs.get(name, default)

    def classes(self) -> list:
        return (self.attrs.get("class") or "").split()

    def has_class(self, name: str) -> bool:
        return name in self.classes()

    # -- traversal ------------------------------------------------------------
    def iter(self) -> Iterator["Node"]:
        yield self
        for child in self.children:
            yield from child.iter()

    def elements(self) -> Iterator["Node"]:
        for node in self.iter():
            if not node.is_text:
                yield node

    def find(self, pred: Callable[["Node"], bool]) -> Optional["Node"]:
        for node in self.elements():
            if pred(node):
                return node
        return None

    def find_all(self, pred: Callable[["Node"], bool]) -> list:
        return [node for node in self.elements() if pred(node)]

    def first(self, tag: str, **attrs) -> Optional["Node"]:
        def match(node: "Node") -> bool:
            if node.tag != tag:
                return False
            for key, value in attrs.items():
                key = key.rstrip("_").replace("_", "-")
                if key == "class":
                    if not node.has_class(value):
                        return False
                elif node.get(key) != value:
                    return False
            return True
        return self.find(match)

    def text_content(self) -> str:
        return "".join(node.text for node in self.iter() if node.is_text)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        if self.is_text:
            return "Text(%r)" % (self.text[:30],)
        return "<%s %s>" % (self.tag, " ".join("%s=%r" % kv for kv in self.attrs.items()))


class _TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.current = self.root

    def handle_starttag(self, tag: str, attrs: list) -> None:
        node = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, parent=self.current)
        self.current.children.append(node)
        if tag not in VOID_ELEMENTS:
            self.current = node

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        node = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, parent=self.current)
        self.current.children.append(node)

    def handle_endtag(self, tag: str) -> None:
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.current = node.parent

    def handle_data(self, data: str) -> None:
        self.current.children.append(Node(text=data, parent=self.current))


def parse_html(source: str) -> Node:
    builder = _TreeBuilder()
    builder.feed(source)
    builder.close()
    return builder.root
