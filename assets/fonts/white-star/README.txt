White Star (white-star.woff)

One glyph, U+2606 WHITE STAR, for the site's \whitestar macro (assets/js/mathjax-config.js),
declared in assets/css/style.scss.

The glyph is drawn, not taken from another font: scripts/white_star.py builds a regular
five-pointed star, widened 1.3% and outlined 33.4 of its 1000 units thick, fitted to the
Songti SC star that Safari on a Mac used to fill in for the reader's serif face, and writes
these bytes (TrueType in WOFF 1.0, which needs only zlib). The book draws the same star from
the same numbers (scripts/book/site-macros.tex). `python3 scripts/white_star.py` rewrites
both; its --check, which _tests/test_white_star.py runs, fails when either is stale.

It is part of the site's code and shares its license (LICENSE).
