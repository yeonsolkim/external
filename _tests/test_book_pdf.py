"""Exercise the Springer class through one real, small LaTeX build.

    python3 -m unittest discover -s _tests -p 'test_book_pdf.py'

The test skips when the local TeX/Poppler tools or required font packages are
unavailable. It never builds Jekyll or changes the book's persistent PDF cache.
"""
import contextlib
import io
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "book"))

import build_book  # noqa: E402


class SpringerPdfTests(unittest.TestCase):
    def test_symbols_and_numbered_heading_links_survive_the_pdf(self):
        env = build_book.tool_env()
        tools = {name: shutil.which(name, path=env["PATH"])
                 for name in ("latexmk", "lualatex", "kpsewhich", "pdftotext", "pdftohtml", "pdfinfo")}
        missing_tools = [name for name, executable in tools.items() if executable is None]
        if missing_tools:
            self.skipTest("PDF integration test needs local tools: " + ", ".join(missing_tools))

        required_files = (
            "amsmath.sty", "amsthm.sty", "fontspec.sty", "newtxtext.sty", "newtxmath.sty",
            "mathtools.sty", "microtype.sty", "graphicx.sty", "newunicodechar.sty",
            "geometry.sty", "enumitem.sty", "tikz-cd.sty", "footmisc.sty", "multicol.sty",
            "imakeidx.sty", "xcolor.sty", "hyperref.sty", "bookmark.sty", "etoolbox.sty",
            "glyphtounicode.tex", "glyphtounicode-cmr.tex", "glyphtounicode-ntx.tex",
            "NewCM10-Book.otf", "NewCMMath-Book.otf", "TeXGyreTermesX-Regular.otf",
            "NewTXMI.pfb", "txsys.pfb", "txsym.pfb", "txexs.pfb", "txmiaX.pfb",
        )
        missing_files = [name for name in required_files if subprocess.run(
            [tools["kpsewhich"], name], env=env, capture_output=True, text=True).returncode]
        if missing_files:
            self.skipTest("PDF integration test needs TeX packages/fonts: " + ", ".join(missing_files))

        fixture = r"""\documentclass{external-springer-book}
\booktitle{PDF regression fixture}
\bookauthor{Test}
\begin{document}
\frontmatter
\tableofcontents
\mainmatter
\chapter{Fixture}
\setcounter{section}{2}
\section{Symbols}
\bookruninhead{First heading.}\unitlabel{heading:first}
White star: $a\whitestar b$ and $x^{a\whitestar b}$.
Diamond: $G\diamond H$.
\[
\sum_{i=1}^n x_i
\quad\Bigl[x\Bigr]
\quad\left[\begin{matrix}1&2\\3&4\end{matrix}\right].
\]
\begin{proof}A complete proof.\end{proof}
\booksubsectionhead{Second heading.}\unitlabel{heading:second}
Heading references: \ref{heading:first} and \ref{heading:second}.
\hyperref[heading:first]{Return to the first heading.}
\par\noindent Label boundary.\par
\begin{enumerate}[label={(L\arabic*)}]
\item First labelled axiom.
\item Second labelled axiom.
\item Third labelled axiom.
\end{enumerate}
\clearpage
\section{Notes}
\vspace*{.65\textheight}
\noindent Marker sentence.\footnote{NOTESTART A long note should remain readable
and stay with its marker when there is room on a page. A long note should remain
readable and stay with its marker when there is room on a page. A long note should
remain readable and stay with its marker when there is room on a page. A long note
should remain readable and stay with its marker when there is room on a page.
A long note should remain readable and stay with its marker when there is room
on a page. A long note should remain readable and stay with its marker when
there is room on a page. NOTEEND}
\end{document}
"""
        with tempfile.TemporaryDirectory(prefix="external-book-pdf-") as temporary:
            directory = Path(temporary)
            (directory / "book.tex").write_text(fixture, encoding="utf-8")
            # Use the pipeline's TEXINPUTS/INDEXSTYLE setup and resolve references
            # through latexmk, rather than maintaining a second compiler command.
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output):
                    pdf = build_book.typeset(directory, "fixture", style="springer")
            except SystemExit as error:
                log_path = directory / "fixture.log"
                log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
                missing = re.search(r"File [`']([^`']+)[`'] not found", log)
                if missing:
                    self.skipTest("PDF integration test needs TeX file: " + missing.group(1))
                self.fail("Springer fixture did not compile: %s\n%s\n%s" % (
                    error, output.getvalue(), log[-5000:]))

            text = subprocess.check_output([tools["pdftotext"], "-layout", str(pdf), "-"],
                                           env=env, text=True)
            info = subprocess.check_output([tools["pdfinfo"], str(pdf)], env=env, text=True)
            paper = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", info)
            self.assertIsNotNone(paper)
            self.assertAlmostEqual(float(paper.group(1)), 155 * 72 / 25.4, places=2)
            self.assertAlmostEqual(float(paper.group(2)), 235 * 72 / 25.4, places=2)
            for symbol in ("☆", "⋄", "∑", "□", "[", "]"):
                self.assertIn(symbol, text, "Missing extracted Unicode symbol %r" % symbol)
            controls = {"U+%04X" % ord(char) for char in text
                        if (ord(char) < 32 and char not in "\t\n\r\f") or 127 <= ord(char) <= 159}
            self.assertEqual(controls, set(), "Non-text C0/C1 characters escaped into the PDF text")

            normalized = " ".join(text.split())
            self.assertIn("1.3.1 First heading.", normalized)
            self.assertIn("1.3.2 Second heading.", normalized)
            self.assertIn("Heading references: 1.3.1 and 1.3.2.", normalized)
            pages = text.split("\f")
            marker_page = next(i for i, page in enumerate(pages) if "Marker sentence." in page)
            self.assertEqual(marker_page, next(i for i, page in enumerate(pages) if "NOTESTART" in page))
            self.assertEqual(marker_page, next(i for i, page in enumerate(pages) if "NOTEEND" in page))

            xml = subprocess.check_output(
                [tools["pdftohtml"], "-xml", "-i", "-stdout", str(pdf)], env=env,
                text=True, stderr=subprocess.DEVNULL)
            layout = ET.fromstring(xml)
            colors = {font.get("id"): font.get("color") for font in layout.iter("fontspec")}
            # Poppler can mark the last word before a superscript as part of the
            # footnote link's rectangle. Test complete linked text runs, not a
            # partially overlapped black body-text run such as "Marker sentence.".
            linked_text = [node for node in layout.iter("text")
                           if not (node.text or "").strip()
                           and any(re.search(r"[A-Za-z0-9]", "".join(link.itertext()))
                                   for link in node.iter("a"))]
            self.assertGreater(len(linked_text), 5)  # Includes contents titles and page numbers.
            self.assertTrue(all(colors[node.get("font")] == "#0000ff" for node in linked_text))
            text_nodes = list(layout.iter("text"))
            boundary = next(float(node.get("left")) for node in text_nodes
                            if "Label boundary." in "".join(node.itertext()))
            labels = [node for node in text_nodes if re.match(r"^\(L[123]\)", "".join(node.itertext()))]
            self.assertEqual(len(labels), 3)
            self.assertTrue(all(float(node.get("left")) >= boundary for node in labels))

            aux = (directory / "fixture.aux").read_text(encoding="utf-8")
            destinations = subprocess.check_output([tools["pdfinfo"], "-dests", str(pdf)],
                                                   env=env, text=True)
            for label, number in (("heading:first", "1.3.1"), ("heading:second", "1.3.2")):
                pattern = (r"\\newlabel\{%s\}\{\{%s\}\{[^}]*\}\{[^}]*\}\{([^}]+)\}"
                           % (re.escape(label), re.escape(number)))
                match = re.search(pattern, aux)
                self.assertIsNotNone(match, "Heading label %s lost its number or anchor" % label)
                self.assertIn('"%s"' % match.group(1), destinations,
                              "Heading label %s points to a missing PDF destination" % label)
            log = (directory / "fixture.log").read_text(encoding="utf-8", errors="replace")
            self.assertNotRegex(log, r"(?:[Uu]ndefined references|unreferenced destination|Missing character)")


if __name__ == "__main__":
    unittest.main()
