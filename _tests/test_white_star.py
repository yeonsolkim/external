"""
Tests for scripts/white_star.py: the site's White Star face and the book's drawing of the same
star are current, and the face is a sound font that the site uses.

    python3 -m unittest discover -s _tests -p 'test_*.py'
"""
import struct
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import white_star  # noqa: E402


def woff_tables(data):
    """{tag: (table, checksum in the directory)} of a WOFF 1.0 file, and its header fields."""
    signature, flavor, length, count = struct.unpack(">4sIIH", data[:14])
    tables = {}
    for i in range(count):
        tag, offset, stored, original, checksum = struct.unpack(">4sIIII", data[44 + 20 * i:64 + 20 * i])
        raw = data[offset:offset + stored]
        table = zlib.decompress(raw) if stored < original else raw
        assert len(table) == original, tag
        tables[tag] = (table, checksum)
    return signature, flavor, length, tables


def glyph_for(cmap, code):
    """The glyph a format 4 cmap subtable (the first encoding record's) maps `code` to."""
    offset = struct.unpack(">I", cmap[8:12])[0]
    sub = cmap[offset:]
    count = struct.unpack(">H", sub[6:8])[0] // 2
    ends = struct.unpack(">%dH" % count, sub[14:14 + 2 * count])
    starts = struct.unpack(">%dH" % count, sub[16 + 2 * count:16 + 4 * count])
    deltas = struct.unpack(">%dH" % count, sub[16 + 4 * count:16 + 6 * count])
    for start, end, delta in zip(starts, ends, deltas):
        if start <= code <= end:
            return (code + delta) & 0xFFFF
    return 0


class WhiteStarTests(unittest.TestCase):
    def test_the_committed_face_is_current(self):
        self.assertEqual(white_star.FONT.read_bytes(), white_star.woff(),
                         "run python3 scripts/white_star.py")

    def test_the_book_draws_the_same_star(self):
        text = white_star.BOOK_MACROS.read_text(encoding="utf-8")
        self.assertEqual(white_star.book_text(text), text, "run python3 scripts/white_star.py")

    def test_the_face_is_a_sound_font(self):
        data = white_star.FONT.read_bytes()
        signature, flavor, length, tables = woff_tables(data)
        self.assertEqual((signature, flavor, length), (b"wOFF", 0x00010000, len(data)))
        self.assertEqual(sorted(tables), sorted(white_star.sfnt_tables()))
        for tag, (table, checksum) in tables.items():
            if tag == b"head":
                table = table[:8] + bytes(4) + table[12:]
            self.assertEqual(checksum, white_star.checksum(table), tag)

        self.assertEqual(glyph_for(tables[b"cmap"][0], 0x2606), 1)
        self.assertEqual(glyph_for(tables[b"cmap"][0], 0x2605), 0)
        glyf = tables[b"glyf"][0]
        contours = struct.unpack(">h", glyf[:2])[0]
        self.assertEqual(contours, 2)
        self.assertEqual(struct.unpack(">HH", glyf[10:14]), (9, 19))  # ten points each
        advance = struct.unpack(">H", tables[b"hmtx"][0][4:6])[0]
        units = struct.unpack(">H", tables[b"head"][0][18:20])[0]
        self.assertEqual(advance, units)  # 1em, as Songti SC's star was

    def test_the_outline_is_one_band_around_the_centre_line(self):
        centre = white_star.centre_line()
        outer = white_star.offset(centre, 10)
        inner = white_star.offset(centre, -10)
        # Every tip moves out and every notch in, along the same bisector, both ways.
        for c, o, i in zip(centre, outer, inner):
            self.assertAlmostEqual((o[0] + i[0]) / 2, c[0], places=9)
            self.assertAlmostEqual((o[1] + i[1]) / 2, c[1], places=9)

    def test_the_site_sets_the_star_in_its_face(self):
        config = (ROOT / "assets" / "js" / "mathjax-config.js").read_text(encoding="utf-8")
        self.assertIn("\\\\unicode[White Star]{x2606}", config)
        self.assertIn("document.fonts.load('1em \"White Star\"'", config)
        style = (ROOT / "assets" / "css" / "style.scss").read_text(encoding="utf-8")
        self.assertIn('font-family: "White Star";', style)
        self.assertIn('url("../fonts/white-star/white-star.woff") format("woff")', style)


if __name__ == "__main__":
    unittest.main()
