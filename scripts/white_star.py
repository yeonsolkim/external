#!/usr/bin/env python3
"""
The white star of \\whitestar, drawn once for the site and for the book.

The site's macro (assets/js/mathjax-config.js) sets U+2606 at 55% of the text, raised .07em,
with a 45-unit stroke. Its glyph used to come from the reader's serif face, which has none:
Safari on a Mac filled it in from Songti SC, and other systems from whatever they had, so
readers saw different stars. This module draws Songti SC's star as a font of the site's own,
"White Star" (assets/fonts/white-star/white-star.woff, declared in assets/css/style.scss), and
the book draws the same star with PGF (scripts/book/site-macros.tex): its path is the centre
line below, stroked as thick as the outline and MathJax's stroke together.

The geometry was fitted to Songti SC's star as WebKit sets it at 800px to the em: a regular
five-pointed star, widened 1.3%, outlined 33.4 of its 1000 units thick, which with the macro's
stroke covers the same ink as Songti SC's to within a pixel. Beside the site's math, whose em
is 430.6/442 of the text's, that is .576em by .54em of ink, from -.013em to .527em; the
book draws it at that size beside its own math.

    python3 scripts/white_star.py           # write the font and the book's drawing
    python3 scripts/white_star.py --check   # fail if either is stale

Stdlib only: the font is TrueType in a WOFF 1.0 wrapper (zlib), built byte by byte, and is the
same bytes on every run.
"""
from __future__ import annotations

import argparse
import math
import re
import struct
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "assets" / "fonts" / "white-star" / "white-star.woff"
BOOK_MACROS = ROOT / "scripts" / "book" / "site-macros.tex"

# The star, in units of the glyph's own em (1000 per em).
TIP, NOTCH = 408.8, 160.8        # radii of the outline's centre line, at its tips and notches
WIDEN = 0.5650 / 0.5575          # Songti SC's star is a little wider than a regular one
OUTLINE = 33.4                   # the glyph's outline
STROKE = 45                      # the stroke the site's macro adds (mathjax-config.js)
CENTRE = (500.0, 281.6)          # centred in its 1000-unit advance, as high as Songti SC's
ADVANCE = 1000
SCALE = 0.55                     # the macro's font-size: 55%
# MathJax sets its math to the text's x-height: its em is 430.6/442 of the text's (the x-heights
# of New Computer Modern 10 Book and of MathJax's newcm). The star is text and keeps the text's
# em, so beside the math it is that much larger (the page writes its font-size as 1026.5px).
TEXT_EM = 442 / 430.6
RAISE = 0.07                     # the macro's \raise, in the math's em
AXIS = 0.25                      # the math axis, in the math's em
MARK = "%% %s drawn by scripts/white_star.py"

FAMILY = "White Star"
UPM = 2000                       # font units per em; twice the glyph's, for finer coordinates
CREATED = datetime(2026, 11, 17, tzinfo=timezone.utc)

Point = Tuple[float, float]


def centre_line() -> List[Point]:
    """The outline's centre line around (0, 0), anticlockwise from the top tip."""
    points = []
    for i in range(10):
        radius = TIP if i % 2 == 0 else NOTCH
        angle = math.radians(90 + 36 * i)
        points.append((radius * math.cos(angle) * WIDEN, radius * math.sin(angle)))
    return points


def offset(points: List[Point], distance: float) -> List[Point]:
    """The anticlockwise polygon `points` moved outward by `distance`, its corners mitred."""
    count = len(points)
    lines = []
    for i in range(count):
        (x0, y0), (x1, y1) = points[i], points[(i + 1) % count]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        lines.append(((x0 + dy / length * distance, y0 - dx / length * distance), (dx, dy)))
    corners = []
    for i in range(count):
        (p, u), (q, v) = lines[i - 1], lines[i]
        s = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / (u[0] * v[1] - u[1] * v[0])
        corners.append((p[0] + s * u[0], p[1] + s * u[1]))
    return corners


def book_block() -> List[str]:
    """The book's drawing (site-macros.tex, between the marks), in the em of the math beside it,
    as the site sets the star beside its math: the centre line stroked as thick as outline and
    stroke together, from the lower left corner of its ink; a box as wide as the star's advance
    around that ink, made deeper than the ink by twice the height the site's ink centre has
    above the math axis, which \\vcenter turns back into that height."""
    em = SCALE * TEXT_EM / 1000      # the glyph's units, in the math's em
    stroke = STROKE / TEXT_EM        # MathJax's stroke is in the math's units at 55%
    centre = centre_line()
    ink = offset(centre, (OUTLINE + stroke) / 2)
    left, right = min(x for x, _ in ink), max(x for x, _ in ink)
    bottom, top = min(y for _, y in ink), max(y for _, y in ink)
    width, height = (right - left) * em, (top - bottom) * em
    lift = (CENTRE[1] + (top + bottom) / 2) * em + RAISE - AXIS
    box = ADVANCE * em

    def length(value: float) -> str:
        return re.sub(r"^(-?)0\.", r"\1.", "%.4f" % value) + "em"

    def point(x: float, y: float) -> str:
        return "\\pgfpoint{%s}{%s}" % (length(x), length(y))

    lines = [MARK % ">>>",
             "\\pgfsetlinewidth{%s}\\pgfsetmiterjoin\\pgfsetmiterlimit{4}%%" % length((OUTLINE + stroke) * em),
             "\\pgfpathmoveto{%s}%%" % point((centre[0][0] - left) * em, (centre[0][1] - bottom) * em)]
    lines += ["\\pgfpathlineto{%s}%%" % point((x - left) * em, (y - bottom) * em) for x, y in centre[1:]]
    lines += ["\\pgfpathclose",
              "\\pgfusepath{stroke}%",
              "%% ink %s by %s; the box %s wide, %s deeper: a lift of %s" % (
                  length(width), length(height), length(box), length(2 * lift), length(lift)),
              "\\pgfresetboundingbox",
              "\\pgfpathrectanglecorners{%s}{%s}%%" % (point((width - box) / 2, -2 * lift),
                                                       point((width + box) / 2, height)),
              "\\pgfusepath{use as bounding box}%",
              MARK % "<<<"]
    return ["    " + line for line in lines]


def book_text(text: str) -> str:
    """`text` (site-macros.tex) with the lines between the marks drawn anew."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.strip() == MARK % ">>>")
    end = next(i for i, line in enumerate(lines) if line.strip() == MARK % "<<<")
    return "\n".join(lines[:start] + book_block() + lines[end + 1:])


# -- the font -------------------------------------------------------------------------------
def checksum(data: bytes) -> int:
    data += b"\0" * (-len(data) % 4)
    return sum(struct.unpack(">%dI" % (len(data) // 4), data)) & 0xFFFFFFFF


def padded(data: bytes) -> bytes:
    return data + b"\0" * (-len(data) % 4)


def star_contours() -> List[List[Tuple[int, int]]]:
    """The glyph's outline in font units: the outer edge clockwise, the inner anticlockwise,
    as TrueType fills them."""
    scale = UPM / 1000
    centre = centre_line()

    def placed(points: List[Point]) -> List[Tuple[int, int]]:
        return [(round((x + CENTRE[0]) * scale), round((y + CENTRE[1]) * scale)) for x, y in points]

    outer = placed(offset(centre, OUTLINE / 2))
    inner = placed(offset(centre, -OUTLINE / 2))
    return [outer[:1] + outer[1:][::-1], inner]


def glyph(contours: List[List[Tuple[int, int]]]) -> bytes:
    points = [p for contour in contours for p in contour]
    xs, ys = [x for x, _ in points], [y for _, y in points]
    ends, total = [], 0
    for contour in contours:
        total += len(contour)
        ends.append(total - 1)
    data = struct.pack(">hhhhh", len(contours), min(xs), min(ys), max(xs), max(ys))
    data += struct.pack(">%dH" % len(ends), *ends) + struct.pack(">H", 0)
    data += bytes([0x01] * len(points))  # on the curve; x and y as 16-bit deltas
    xs_data = ys_data = b""
    previous = (0, 0)
    for x, y in points:
        xs_data += struct.pack(">h", x - previous[0])
        ys_data += struct.pack(">h", y - previous[1])
        previous = (x, y)
    return padded(data + xs_data + ys_data)


def name_table() -> bytes:
    names = [
        (0, "Drawn for the External site: the star of its \\whitestar macro"),
        (1, FAMILY),
        (2, "Regular"),
        (3, FAMILY + " 1.000"),
        (4, FAMILY),
        (5, "Version 1.000"),
        (6, FAMILY.replace(" ", "")),
    ]
    strings = b""
    records = b""
    for name_id, text in names:
        encoded = text.encode("utf-16-be")
        records += struct.pack(">HHHHHH", 3, 1, 0x0409, name_id, len(encoded), len(strings))
        strings += encoded
    return struct.pack(">HHH", 0, len(names), 6 + 12 * len(names)) + records + strings


def cmap_table() -> bytes:
    segments = [(0x2606, 0x2606, (1 - 0x2606) & 0xFFFF), (0xFFFF, 0xFFFF, 1)]
    count = len(segments)
    search = 2 * 2 ** int(math.log2(count))
    subtable = struct.pack(">HHHHHHH", 4, 16 + 8 * count, 0, 2 * count, search,
                           int(math.log2(search // 2)), 2 * count - search)
    subtable += struct.pack(">%dH" % count, *(end for _, end, _ in segments)) + b"\0\0"
    subtable += struct.pack(">%dH" % count, *(start for start, _, _ in segments))
    subtable += struct.pack(">%dH" % count, *(delta for _, _, delta in segments))
    subtable += struct.pack(">%dH" % count, *([0] * count))
    return struct.pack(">HH", 0, 2) + struct.pack(">HHI", 0, 3, 20) + struct.pack(">HHI", 3, 1, 20) + subtable


def sfnt_tables() -> dict:
    contours = star_contours()
    star = glyph(contours)
    points = [p for contour in contours for p in contour]
    x_min, x_max = min(x for x, _ in points), max(x for x, _ in points)
    y_min, y_max = min(y for _, y in points), max(y for _, y in points)
    advance = ADVANCE * UPM // 1000
    # Songti SC's vertical metrics, so that a line box measured on the star is as before.
    ascent, descent = 1060 * UPM // 1000, 340 * UPM // 1000
    seconds = int((CREATED - datetime(1904, 1, 1, tzinfo=timezone.utc)).total_seconds())

    head = struct.pack(">iiIIHHqqhhhhHHhhh", 0x00010000, 0x00010000, 0, 0x5F0F3CF5, 0x000B, UPM,
                       seconds, seconds, x_min, y_min, x_max, y_max, 0, 8, 2, 1, 0)
    hhea = struct.pack(">ihhhHhhhhhhhhhhhH", 0x00010000, ascent, -descent, 0, advance,
                       min(0, x_min), advance - x_max, x_max, 1, 0, 0, 0, 0, 0, 0, 0, 2)
    hmtx = struct.pack(">HhHh", advance // 2, 0, advance, x_min)
    maxp = struct.pack(">iHHHHHHHHHHHHHH", 0x00010000, 2, len(points), len(contours),
                       0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0)
    loca = struct.pack(">III", 0, 0, len(star))
    os2 = struct.pack(">HhHHH", 4, advance, 400, 5, 0)
    os2 += struct.pack(">hhhh", 1300, 1200, 0, 300) + struct.pack(">hhhh", 1300, 1200, 0, 900)
    os2 += struct.pack(">hh", 100, 560) + struct.pack(">h", 0) + bytes(10)
    os2 += struct.pack(">IIII", 0, 1 << 14, 0, 0)  # Miscellaneous Symbols, U+2600–26FF
    os2 += b"NONE" + struct.pack(">HHH", 0x40, 0x2606, 0x2606)
    os2 += struct.pack(">hhh", ascent, -descent, 0) + struct.pack(">HH", ascent, descent)
    os2 += struct.pack(">II", 0, 0) + struct.pack(">hh", 0, 0) + struct.pack(">HHH", 0, 0x20, 0)
    post = struct.pack(">iihhIIIII", 0x00030000, 0, -150, 100, 0, 0, 0, 0, 0)
    return {b"OS/2": os2, b"cmap": cmap_table(), b"glyf": star, b"head": head, b"hhea": hhea,
            b"hmtx": hmtx, b"loca": loca, b"maxp": maxp, b"name": name_table(), b"post": post}


def sfnt(tables: dict) -> bytes:
    tags = sorted(tables)
    selector = int(math.log2(len(tags)))
    header = struct.pack(">IHHHH", 0x00010000, len(tags), 16 * 2 ** selector, selector,
                         16 * len(tags) - 16 * 2 ** selector)
    position = 12 + 16 * len(tags)
    directory = data = b""
    for tag in tags:
        table = tables[tag]
        directory += struct.pack(">4sIII", tag, checksum(table), position, len(table))
        data += padded(table)
        position += len(padded(table))
    font = header + directory + data
    adjustment = (0xB1B0AFBA - checksum(font)) & 0xFFFFFFFF
    head_at = 12 + 16 * len(tags) + sum(len(padded(tables[t])) for t in tags[:tags.index(b"head")])
    return font[:head_at + 8] + struct.pack(">I", adjustment) + font[head_at + 12:]


def woff() -> bytes:
    tables = sfnt_tables()
    font = sfnt(tables)
    tags = sorted(tables)
    # The head table as the sfnt has it, with its checksum adjustment.
    head_at = 12 + 16 * len(tags) + sum(len(padded(tables[t])) for t in tags[:tags.index(b"head")])
    tables[b"head"] = font[head_at:head_at + len(tables[b"head"])]
    position = 44 + 20 * len(tags)
    directory = data = b""
    for tag in tags:
        original = tables[tag]
        compressed = zlib.compress(original, 9)
        stored = compressed if len(compressed) < len(original) else original
        record_checksum = checksum(original if tag != b"head"
                                   else original[:8] + b"\0\0\0\0" + original[12:])
        directory += struct.pack(">4sIIII", tag, position, len(stored), len(original), record_checksum)
        data += padded(stored)
        position += len(padded(stored))
    header = struct.pack(">4sIIHHIHHIIIII", b"wOFF", 0x00010000, position, len(tags), 0, len(font),
                         1, 0, 0, 0, 0, 0, 0)
    return header + directory + data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="change nothing; fail if the font or the book's drawing is stale")
    args = parser.parse_args()
    data = woff()
    macros = BOOK_MACROS.read_text(encoding="utf-8")
    if args.check:
        stale = []
        if not FONT.is_file() or FONT.read_bytes() != data:
            stale.append(str(FONT.relative_to(ROOT)))
        if book_text(macros) != macros:
            stale.append(str(BOOK_MACROS.relative_to(ROOT)))
        for name in stale:
            print("stale: %s (python3 scripts/white_star.py writes it)" % name)
        return 1 if stale else 0
    FONT.parent.mkdir(parents=True, exist_ok=True)
    FONT.write_bytes(data)
    BOOK_MACROS.write_text(book_text(macros), encoding="utf-8")
    print("%s: %d bytes; %s: the star's drawing" % (
        FONT.relative_to(ROOT), len(data), BOOK_MACROS.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
