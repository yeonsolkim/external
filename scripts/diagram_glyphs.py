#!/usr/bin/env python3
"""Draw the diagrams with New Computer Modern: write _plugins/tikzcd_glyphs.json.

    python3 scripts/diagram_glyphs.py            regenerate the file
    python3 scripts/diagram_glyphs.py --report   also list the glyphs left to Computer Modern

The text of a post is New Computer Modern Book, and so is its math: MathJax's outlines are
those of NewCMMath-Book.otf. The diagrams are typeset by LaTeX in Computer Modern, whose
metrics New Computer Modern keeps, so tikzcd_renderer.rb leaves every glyph where TeX put it
and draws it with New Computer Modern Book's outline, from this file. CI needs no font for it.

Where New Computer Modern has a glyph of another width (the calligraphic capitals, \\circ, \\forall)
the metrics have to be its own as well. All of these are in TeX's symbol font, so the file also
holds newcmsy10.tfm: cmsy10 with their widths, which the renderer sets math symbols in.

A glyph that New Computer Modern lacks, or has in another place (the pieces of \\hookrightarrow
and \\mapsto, text accents), is not in the file, and the renderer draws Computer Modern's.

The text of a picture is not drawn but set by the page, in its own New Computer Modern. For the
renderer to tell it from the math, it is set in TeX's text fonts under a second name; their
metrics are here too, with the widths of their characters.

Needs TeX Live with XeTeX, dvisvgm, the newcomputermodern fonts, tftopl and pltotf. The renderer's
cache follows the file's contents, so nothing else has to change after a run.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_plugins" / "tikzcd_glyphs.json"

BOOK, ITALIC, BOLD, MATH = ("NewCM10-Book.otf", "NewCM10-BookItalic.otf", "NewCM10-Bold.otf", "NewCMMath-Book.otf")
EM = 1000  # units of the fonts, and the size in bp the outlines are read at

# How far a glyph of the same width may reach beyond Computer Modern's box and still be the same
# glyph. New Computer Modern's +- sits 0.084em lower, and MathJax draws that one.
REACH = 100
# The same for a large delimiter or operator, once the two are centred on each other.
LARGE_REACH = 60


# -- what stands where in TeX's fonts: a character, or the name of one of the font's glyphs -------
def ot1(italic: bool = False) -> dict:
    table = dict(enumerate([
        0x393, 0x394, 0x398, 0x39B, 0x39E, 0x3A0, 0x3A3, 0x3A5, 0x3A6, 0x3A8, 0x3A9,  # capital Greek
        0xFB00, 0xFB01, 0xFB02, 0xFB03, 0xFB04, 0x131, 0x237]))                       # ff fi fl ffi ffl, dotless
    table.update({25: 0xDF, 26: 0xE6, 27: 0x153, 28: 0xF8, 29: 0xC6, 30: 0x152, 31: 0xD8})
    table.update({code: code for code in range(33, 123)})
    table.update({34: 0x201D, 39: 0x2019, 60: 0xA1, 62: 0xBF, 92: 0x201C, 96: 0x2018, 123: 0x2013, 124: 0x2014})
    if italic:
        table[36] = 0xA3
    for accent in (94, 95):
        del table[accent]
    return table


def letters(capital: int, small: int, exceptions: dict = {}) -> dict:
    table = {65 + i: capital + i for i in range(26)}
    table.update({97 + i: small + i for i in range(26)})
    table.update(exceptions)
    return table


OML = letters(0x1D434, 0x1D44E, {104: 0x210E})
OML.update(dict(enumerate([
    0x1D6E4, 0x1D6E5, 0x1D6E9, 0x1D6EC, 0x1D6EF, 0x1D6F1, 0x1D6F4, 0x1D6F6, 0x1D6F7, 0x1D6F9, 0x1D6FA,
    0x1D6FC, 0x1D6FD, 0x1D6FE, 0x1D6FF, 0x1D716, 0x1D701, 0x1D702, 0x1D703, 0x1D704, 0x1D705, 0x1D706,
    0x1D707, 0x1D708, 0x1D709, 0x1D70B, 0x1D70C, 0x1D70E, 0x1D70F, 0x1D710, 0x1D719, 0x1D712, 0x1D713,
    0x1D714, 0x1D700, 0x1D717, 0x1D71B, 0x1D71A, 0x1D70D, 0x1D711, 0x21BC, 0x21BD, 0x21C0, 0x21C1])))
OML.update({58: 0x2E, 59: 0x2C, 60: 0x3C, 61: 0x2F, 62: 0x3E, 63: 0x22C6, 64: 0x1D715, 91: 0x266D, 92: 0x266E,
            93: 0x266F, 94: 0x2323, 95: 0x2322, 96: 0x2113, 123: 0x1D6A4, 124: 0x1D6A5, 125: 0x2118})

BOLD_OML = letters(0x1D468, 0x1D482)

CALLIGRAPHIC = {65 + i: 0x1D49C + i for i in range(26)}
CALLIGRAPHIC.update({66: 0x212C, 69: 0x2130, 70: 0x2131, 72: 0x210B, 73: 0x2110, 76: 0x2112, 77: 0x2133, 82: 0x211B})
# 54 and 55 (\not, the bar of \mapsto) and 115 (\smallint) have no counterpart.
OMS = dict(enumerate([
    0x2212, 0x22C5, 0xD7, 0x2217, 0xF7, 0x22C4, 0xB1, 0x2213, 0x2295, 0x2296, 0x2297, 0x2298, 0x2299, 0x25EF,
    0x2218, 0x2219, 0x224D, 0x2261, 0x2286, 0x2287, 0x2264, 0x2265, 0x2AAF, 0x2AB0, 0x223C, 0x2248, 0x2282,
    0x2283, 0x226A, 0x226B, 0x227A, 0x227B, 0x2190, 0x2192, 0x2191, 0x2193, 0x2194, 0x2197, 0x2198, 0x2243,
    0x21D0, 0x21D2, 0x21D1, 0x21D3, 0x21D4, 0x2196, 0x2199, 0x221D, "minute.st", 0x221E, 0x2208, 0x220B,
    0x25B3, 0x25BD, None, None, 0x2200, 0x2203, 0xAC, "emptyset.alt", 0x211C, 0x2111, 0x22A4, 0x22A5, 0x2135]))
OMS.update(CALLIGRAPHIC)
OMS.update(dict(zip(range(91, 128), [
    0x222A, 0x2229, 0x228E, 0x2227, 0x2228, 0x22A2, 0x22A3, 0x230A, 0x230B, 0x2308, 0x2309, 0x7B, 0x7D, 0x27E8,
    0x27E9, 0x7C, 0x2225, 0x2195, 0x21D5, 0x5C, 0x2240, None, 0x2A3F, 0x2207, None, 0x2294, 0x2293, 0x2291,
    0x2292, 0xA7, 0x2020, 0x2021, 0xB6, 0x2663, 0x2662, 0x2661, 0x2660])))

# cmex10: four sizes of the delimiters, two of the operators, four of the radical.
OMX = {}
for size, codes in {
    "v2": {0: "parenleft", 1: "parenright", 2: "bracketleft", 3: "bracketright", 4: "uni230A", 5: "uni230B",
           6: "uni2308", 7: "uni2309", 8: "braceleft", 9: "braceright", 10: "uni27E8", 11: "uni27E9",
           14: "slash", 15: "backslash"},
    "v4": {16: "parenleft", 17: "parenright", 46: "slash", 47: "backslash", 68: "uni27E8", 69: "uni27E9",
           104: "bracketleft", 105: "bracketright", 106: "uni230A", 107: "uni230B", 108: "uni2308",
           109: "uni2309", 110: "braceleft", 111: "braceright"},
    "v6": {18: "parenleft", 19: "parenright", 20: "bracketleft", 21: "bracketright", 22: "uni230A",
           23: "uni230B", 24: "uni2308", 25: "uni2309", 26: "braceleft", 27: "braceright", 28: "uni27E8",
           29: "uni27E9", 30: "slash", 31: "backslash"},
    "v7": {32: "parenleft", 33: "parenright", 34: "bracketleft", 35: "bracketright", 36: "uni230A",
           37: "uni230B", 38: "uni2308", 39: "uni2309", 40: "braceleft", 41: "braceright", 42: "uni27E8",
           43: "uni27E9", 44: "slash", 45: "backslash"},
}.items():
    OMX.update({code: "%s.%s" % (name, size) for code, name in codes.items()})
OMX.update({112: "radical.v1", 113: "radical.v3", 114: "radical.v4", 115: "radical.v5"})
for (text, display), name in {
    (70, 71): "uni2A06", (72, 73): "contourintegral", (74, 75): "uni2A00", (76, 77): "uni2A01", (78, 79): "uni2A02",
    (80, 88): "summation", (81, 89): "product", (82, 90): "integral", (83, 91): "uni22C3", (84, 92): "uni22C2",
    (85, 93): "uni2A04", (86, 94): "uni22C0", (87, 95): "uni22C1", (96, 97): "uni2210",
}.items():
    OMX.update({text: name, display: name + ".v1"})

MSA = dict(zip(
    [0x00, 0x01, 0x02, 0x03, 0x04, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, *range(0x10, 0x20)],
    [0x22A1, 0x229E, 0x22A0, 0x25A1, 0x25A0, 0x25CA, 0x29EB, 0x21BB, 0x21BA, 0x21CC, 0x21CB, 0x229F, 0x22A9, 0x22AA,
     0x22A8, 0x21A0, 0x219E, 0x21C7, 0x21C9, 0x21C8, 0x21CA, 0x21BE, 0x21C2, 0x21BF, 0x21C3, 0x21A3, 0x21A2, 0x21C6,
     0x21C4, 0x21B0, 0x21B1]))
MSA.update({0x20: 0x21DD, 0x21: 0x21AD, 0x22: 0x21AB, 0x23: 0x21AC, 0x24: 0x2257, 0x25: 0x227F, 0x26: 0x2273,
            0x27: 0x2A86, 0x28: 0x22B8, 0x29: 0x2234, 0x2A: 0x2235, 0x2B: 0x2251, 0x2C: 0x225C, 0x2D: 0x227E,
            0x2E: 0x2272, 0x2F: 0x2A85, 0x30: 0x2A95, 0x31: 0x2A96, 0x32: 0x22DE, 0x33: 0x22DF, 0x34: 0x227C,
            0x35: 0x2266, 0x36: 0x2A7D, 0x37: 0x2276, 0x3A: 0x2253, 0x3B: 0x2252, 0x3C: 0x227D, 0x3D: 0x2267,
            0x3E: 0x2A7E, 0x3F: 0x2277, 0x40: 0x228F, 0x41: 0x2290, 0x42: 0x22B3, 0x43: 0x22B2, 0x44: 0x22B5,
            0x45: 0x22B4, 0x46: 0x2605, 0x47: 0x226C, 0x48: 0x25BC, 0x49: 0x25B6, 0x4A: 0x25C0, 0x4D: 0x25B3,
            0x4E: 0x25B2, 0x4F: 0x25BD, 0x50: 0x2256, 0x51: 0x22DA, 0x52: 0x22DB, 0x56: 0x21DB, 0x57: 0x21DA,
            0x59: 0x22BB, 0x5A: 0x22BC, 0x5B: 0x2A5E, 0x5C: 0x2220, 0x5D: 0x2221, 0x5E: 0x2222, 0x5F: 0x221D,
            0x62: 0x22D0, 0x63: 0x22D1, 0x64: 0x22D3, 0x65: 0x22D2, 0x66: 0x22CF, 0x67: 0x22CE, 0x68: 0x22CB,
            0x69: 0x22CC, 0x6A: 0x2AC5, 0x6B: 0x2AC6, 0x6C: 0x224F, 0x6D: 0x224E, 0x6E: 0x22D8, 0x6F: 0x22D9,
            0x73: 0x22D4, 0x74: 0x2214, 0x75: 0x223D, 0x76: 0x22CD, 0x7B: 0x2201, 0x7C: 0x22BA, 0x7D: 0x229A,
            0x7E: 0x229B, 0x7F: 0x229D})
MSB = {65 + i: 0x1D538 + i for i in range(26)}
MSB.update({67: 0x2102, 72: 0x210D, 78: 0x2115, 80: 0x2119, 81: 0x211A, 82: 0x211D, 90: 0x2124})
MSB.update({0x02: 0x2270, 0x03: 0x2271, 0x04: 0x226E, 0x05: 0x226F, 0x06: 0x2280, 0x07: 0x2281, 0x1C: 0x2241,
            0x1D: 0x2247, 0x28: 0x228A, 0x29: 0x228B, 0x2A: 0x2288, 0x2B: 0x2289, 0x2C: 0x2226, 0x2D: 0x2224,
            0x30: 0x22AC, 0x31: 0x22AE, 0x32: 0x22AD, 0x33: 0x22AF, 0x34: 0x22ED, 0x35: 0x22EC, 0x36: 0x22EA,
            0x37: 0x22EB, 0x38: 0x219A, 0x39: 0x219B, 0x3A: 0x21CD, 0x3B: 0x21CF, 0x3C: 0x21CE, 0x3D: 0x21AE,
            0x3E: 0x22C7, 0x3F: 0x2205, 0x66: 0x2127, 0x67: 0xF0, 0x68: 0x2242, 0x69: 0x2136, 0x6A: 0x2137,
            0x6B: 0x2138, 0x6C: 0x22D6, 0x6D: 0x22D7, 0x6E: 0x22C9, 0x6F: 0x22CA, 0x75: 0x224A, 0x78: 0x21B6,
            0x79: 0x21B7, 0x7B: 0x1D718, 0x7D: 0x210F, 0x7F: 0x3F6})

FONTS = {
    "cmr10": (BOOK, ot1()),
    "cmti10": (ITALIC, ot1(italic=True)),
    "cmbx10": (BOLD, ot1()),
    "cmmi10": (MATH, OML),
    "cmmib10": (MATH, BOLD_OML),
    "cmsy10": (MATH, {code: glyph for code, glyph in OMS.items() if glyph is not None}),
    "cmex10": (MATH, OMX),
    "msam10": (MATH, MSA),
    "msbm10": (MATH, MSB),
}
# The one font set in New Computer Modern's own metrics, and the name it has in that form.
OWN_METRICS = {"cmsy10": "newcmsy10"}
# The fonts of a picture's text, and the name they have there.
TEXT = {"cmr10": "newcmr10", "cmti10": "newcmti10", "cmbx10": "newcmbx10"}


# -- outlines -----------------------------------------------------------------------------------
def run(command: list, directory: Path) -> str:
    result = subprocess.run(command, cwd=directory, capture_output=True, text=True, errors="replace")
    if result.returncode:
        raise SystemExit("%s failed:\n%s" % (command[0], (result.stdout + result.stderr)[-1500:]))
    return result.stdout


def outlines(directory: Path, tex: list, dvi: str) -> tuple:
    """Typeset, then {glyph or character code: path} and the log."""
    log = run(tex, directory)
    run(["dvisvgm", "--no-fonts", "--bbox=min", "--precision=3", "--output=glyphs.svg", dvi], directory)
    svg = (directory / "glyphs.svg").read_text(encoding="utf-8")
    return {int(code): path for code, path in re.findall(r"<path id='g\d+-(\d+)' d='([^']*)'", svg)}, log


# Every glyph is set at one and the same place: a page may not be 100 m wide.
AT_ONE_PLACE = r"\hbox to0pt{\vbox to0pt{\vss\box0}\hss}"


def computer_modern(font: str, directory: Path) -> dict:
    """{character code: (width, outline)} in 1/1000em."""
    (directory / "cm.tex").write_text(
        "\\font\\f=%s at %dbp \\hoffset=-1in \\voffset=-1in\n"
        "\\def\\c#1{\\iffontchar\\f#1 \\setbox0\\hbox{\\f\\char#1}\\immediate\\write16{W #1 \\the\\wd0 }%s\\fi}\n"
        "\\shipout\\hbox{%s}\\end\n" % (font, EM, AT_ONE_PLACE, "".join("\\c{%d}" % code for code in range(128))),
        encoding="utf-8")
    paths, log = outlines(directory, ["etex", "-interaction=nonstopmode", "cm.tex"], "cm.dvi")
    widths = {int(code): float(width) * 72 / 72.27 for code, width in re.findall(r"W (\d+) ([\d.]+)pt", log)}
    return {code: (widths[code], path) for code, path in paths.items()}


def new_computer_modern(font: str, table: dict, directory: Path) -> dict:
    """{character code: (width, outline)} of the glyphs the table names, in 1/1000em."""
    lookups = []
    for code, glyph in table.items():
        index = "\\XeTeXcharglyph\"%X" % glyph if isinstance(glyph, int) else "\\XeTeXglyphindex\"%s\"" % glyph
        lookups.append("\\g{%d}{%s}%%\n" % (code, index))
    (directory / "nc.tex").write_text(
        "\\font\\f=\"[%s]\" at %dbp \\hoffset=-1in \\voffset=-1in \\f\n"
        "\\def\\g#1#2{\\count0=#2\\relax \\setbox0\\hbox{\\XeTeXglyph\\count0 }"
        "\\immediate\\write16{G #1 \\the\\count0 \\space\\the\\wd0 }%s}\n"
        "\\shipout\\hbox{%s}\\end\n" % (font, EM, AT_ONE_PLACE, "".join(lookups)), encoding="utf-8")
    paths, log = outlines(directory, ["xetex", "-no-pdf", "-interaction=nonstopmode", "nc.tex"], "nc.xdv")
    found = {}
    for code, index, width in re.findall(r"G (\d+) (\d+)\s+([\d.]+)pt", log):
        if index != "0" and int(index) in paths:
            found[int(code)] = (float(width) * 72 / 72.27, paths[int(index)])
    return found


def segments(path: str) -> list:
    """[(command, numbers)]; dvisvgm writes absolute M, L, H, V, C, S and Z."""
    found = re.findall(r"([A-Za-z])([^A-Za-z]*)", path)
    if any(command not in "MLHVCSZ" for command, _ in found):
        raise SystemExit("an outline has a command this script does not know: %s" % path[:80])
    return [(command, [float(number) for number in re.findall(r"-?\d*\.?\d+", rest)]) for command, rest in found]


def box(path: str) -> tuple:
    """The outline's left, top, right and bottom (y points down)."""
    xs, ys, at, last = [], [], (0.0, 0.0), None
    for command, numbers in segments(path):
        if command in "ML":
            for point in zip(numbers[::2], numbers[1::2]):
                at = point
                xs.append(at[0])
                ys.append(at[1])
        elif command == "H":
            at = (numbers[-1], at[1])
            xs.extend(numbers)
        elif command == "V":
            at = (at[0], numbers[-1])
            ys.extend(numbers)
        elif command in "CS":
            step = 6 if command == "C" else 4
            for start in range(0, len(numbers), step):
                points = list(zip(numbers[start:start + step:2], numbers[start + 1:start + step:2]))
                if command == "S":
                    points.insert(0, (2 * at[0] - last[0], 2 * at[1] - last[1]) if last else at)
                for i in range(25):
                    t = i / 24
                    weights = ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3)
                    curve = [at] + points
                    xs.append(sum(w * p[0] for w, p in zip(weights, curve)))
                    ys.append(sum(w * p[1] for w, p in zip(weights, curve)))
                last, at = points[1], points[2]
            continue
        last = None
    return min(xs), min(ys), max(xs), max(ys)


def number(value: float) -> str:
    return ("%.3f" % value).rstrip("0").rstrip(".").replace("-0", "0") if abs(value) < 0.0005 \
        else ("%.3f" % value).rstrip("0").rstrip(".")


def moved_down(path: str, distance: float) -> str:
    """The outline moved down, in one plain form."""
    out = []
    for command, numbers in segments(path):
        if command == "V":
            numbers = [y + distance for y in numbers]
        elif command in "MLCS":
            numbers = [value + distance * (i % 2) for i, value in enumerate(numbers)]
        out.append(command + " ".join(number(value) for value in numbers))
    return "".join(out).replace(" -", "-")


# -- metrics --------------------------------------------------------------------------------------
def own_metrics(font: str, glyphs: dict, changed: list, directory: Path) -> bytes:
    """The font's TFM with New Computer Modern's width, height and depth for the glyphs it changes."""
    pl = run(["tftopl", run(["kpsewhich", font + ".tfm"], directory).strip()], directory)
    pl = re.sub(r"\(CHECKSUM [^)]*\)\n", "", pl)

    def rewrite(match):
        code = int(match.group(2), 8) if match.group(1) == "O" else ord(match.group(2))
        if code not in changed:
            return match.group(0)
        width, path = glyphs[code]
        _, top, _, bottom = box(path)
        size = "   (CHARWD R %.4f)\n   (CHARHT R %.4f)\n   (CHARDP R %.4f)\n" % (
            width / EM, max(0, -top) / EM, max(0, bottom) / EM)
        rest = re.sub(r" *\(CHAR(?:WD|HT|DP|IC) R [-\d.]+\)\n", "", match.group(3))
        return "(CHARACTER %s %s\n%s%s" % (match.group(1), match.group(2), size, rest)

    pl = re.sub(r"\(CHARACTER ([OC]) (\S+)\n(.*?\n   \)\n)", rewrite, pl, flags=re.S)
    (directory / "own.pl").write_text(pl, encoding="utf-8")
    run(["pltotf", "own.pl", "own.tfm"], directory)
    return (directory / "own.tfm").read_bytes()


# -- the file -------------------------------------------------------------------------------------
def generate(report: bool) -> dict:
    data, tfm, widths = {}, {}, {}
    with tempfile.TemporaryDirectory() as name:
        directory = Path(name)
        for font, (file, table) in FONTS.items():
            modern = computer_modern(font, directory)
            new = new_computer_modern(file, table, directory)
            kept, left, changed = {}, [], []
            for code in sorted(table):
                if code not in modern or code not in new:
                    left.append("%d (not in both)" % code)
                    continue
                (width, path), (own_width, own) = modern[code], new[code]
                theirs, ours = box(path), box(own)
                shift, limit = 0.0, REACH
                if font == "cmex10":  # TeX hangs large symbols from their top; New Computer Modern centres them
                    shift, limit = (theirs[1] + theirs[3] - ours[1] - ours[3]) / 2, LARGE_REACH
                reach = max(abs(theirs[0] - ours[0]), abs(theirs[2] - ours[2]),
                            abs(theirs[1] - ours[1] - shift), abs(theirs[3] - ours[3] - shift))
                if font in OWN_METRICS:
                    if abs(width - own_width) > 0.5 or code in CALLIGRAPHIC:
                        changed.append(code)
                elif reach > limit or (font != "cmex10" and abs(width - own_width) > 5):
                    left.append("%d (width %+.0f, reach %.0f)" % (code, own_width - width, reach))
                    continue
                kept[str(code)] = moved_down(own, shift)
            if font in TEXT:
                metrics = Path(run(["kpsewhich", font + ".tfm"], directory).strip()).read_bytes()
                tfm[TEXT[font]] = base64.b64encode(metrics).decode("ascii")
                widths[TEXT[font]] = {str(code): round(width) for code, (width, _) in sorted(modern.items())}
            name_of = OWN_METRICS.get(font, font)
            data[name_of] = kept
            if changed:
                tfm[name_of] = base64.b64encode(own_metrics(font, new, changed, directory)).decode("ascii")
            print("%-9s %3d glyphs of %s%s" % (
                name_of, len(kept), file, ", %d in its metrics" % len(changed) if changed else ""))
            if report and left:
                print("          left to Computer Modern: " + ", ".join(left))
    return {
        "source": "Outlines of New Computer Modern (Antonis Tsolomitis, GUST Font License); written by "
                  "scripts/diagram_glyphs.py",
        "tfm": tfm,
        "widths": widths,
        "glyphs": data,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--report", action="store_true", help="list the glyphs left to Computer Modern")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    text = json.dumps(generate(arguments.report), indent=0, sort_keys=False, ensure_ascii=True)
    arguments.output.write_text(text + "\n", encoding="utf-8")
    print("%s: %d bytes" % (arguments.output, len(text) + 1))


if __name__ == "__main__":
    main()
