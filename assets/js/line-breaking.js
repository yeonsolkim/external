/*
 * Line breaking for the justified text of a post, as TeX breaks a paragraph. A browser sets a
 * paragraph a line at a time, taking as much as fits on each, so a formula or a long word
 * that just fails to fit leaves the line before it with gaping spaces. TeX looks at the whole
 * paragraph before it breaks any line (Knuth and Plass, "Breaking paragraphs into lines",
 * 1981): of all the ways to break it, hyphenating where that helps, it takes the one whose
 * lines are spaced most evenly, each line stretching or shrinking its spaces a little. This
 * file does the same for every justified paragraph and list item of a post, with plain TeX's
 * parameters and TeX's American English hyphenation patterns (hyphenation-en-us.js).
 *
 * The browser then sets exactly the lines chosen (post.css). The paragraph does not wrap by
 * itself; an empty span after each break ends the line with a generated newline, and
 * text-align-last: justify stretches every line so ended to the full measure. A line that
 * keeps its natural spacing instead (the last line, a line before display math or a forced
 * break, a line with no space to stretch, such as a statement's label alone on its line) ends
 * with an invisible filler as wide as the room left, as \parfillskip fills the last line of a
 * TeX paragraph. The breaks are worked out again whenever the column changes width.
 */
(function () {
  'use strict';

  /* Plain TeX's parameters, which LaTeX keeps. A first pass looks for breaks without
     hyphenating, within \pretolerance, and a second hyphenates, within \tolerance. A formula
     breaks only where MathJax allows it, before a relation or a binary operator, at the cost
     TeX gives such a break. */
  var PRETOLERANCE = 100;
  var TOLERANCE = 200;
  var LINE_PENALTY = 10;
  var HYPHEN_PENALTY = 50;
  var EX_HYPHEN_PENALTY = 50;
  var REL_PENALTY = 500;
  var BIN_OP_PENALTY = 700;
  /* amsthm sets a statement's label in a box, which no line breaks. A label wider than the
     column has to break somewhere, so its spaces and dashes are breakpoints, but at a cost
     that only a label too long for one line pays. */
  var LABEL_PENALTY = 5000;
  var ADJ_DEMERITS = 10000;
  var DOUBLE_HYPHEN_DEMERITS = 10000;
  var FINAL_HYPHEN_DEMERITS = 5000;
  var INF_BAD = 10000;
  var INF_PENALTY = 10000;
  var EJECT_PENALTY = -10000;

  /* A space stretches by half its width, as Computer Modern's interword space does (3.33pt
     plus 1.67pt at 10pt): New Computer Modern's roman space, less the post's 0.045em, is
     0.288em, and stretches by STRETCH em. It shrinks by a third, SHRINK em, as far as TeX
     lets Computer Modern's shrink (3.33pt less 1.11pt): the paragraph's spaces start that much
     narrower (--typeset-word-spacing, worked out here in px), and justification widens them
     again. When neither pass
     keeps every line within the tolerance, where TeX would let a line run into the margin, a
     third pass takes the most even spacing it can find, however loose, and justifies it all
     the same: its badness has no ceiling. A line with no space to stretch cannot be
     justified and keeps its natural spacing, so the pass avoids one: it counts as if it had
     a single space to stretch. A statement's label alone on its line is a last resort, worth
     it only to spare a line spaces some four and a half times their width (a stretch of 7). */
  var STRETCH = 0.144;
  var SHRINK = 0.096;
  var LABEL_LINE_BADNESS = 100 * Math.pow(7, 3);

  /* A pixel of every line is left unused, for what the measurements cannot see (the kerning
     across a break, Safari's whole pixels), so that no line comes out wider than its column. */
  var SAFETY = 1;

  var SPACE = /[ \t\n\r\f]/;
  var SPECIAL = /[\s\u00ad\u200b\u2060]/;
  var NO_BREAK_SPACE = /[\u00a0\u2007\u202f]/;
  var LETTER = /\p{L}/u;
  var LETTERS = /\p{L}+/gu;
  var REPLACED = /^(img|svg|video|audio|canvas|iframe|object|embed|input|button|select|textarea)$/i;
  var BLOCKS = 'p, li, ul, ol, dl, blockquote, div, section, table, pre, figure, h1, h2, h3, h4, h5, h6';
  var LABELS = '.math-label-anchor, .math-proof-marker';
  var UNHYPHENATED = 'code, kbd, samp, ' + LABELS;
  var INSERTED = '.typeset-break, .typeset-hyphen, .typeset-fill';

  var supported = !!(window.CSS && CSS.supports && CSS.supports('text-wrap-mode', 'nowrap'));
  var hyphenate = null;
  var hyphenWidths = Object.create(null);
  var canvas = null;
  var watching = false;

  /* Liang's algorithm, as TeX hyphenates: every pattern found in the word (with a dot at each
     end) raises the digits between its letters, and the word may break where the highest
     digit is odd. */
  function buildHyphenator(data) {
    var trie = Object.create(null);
    var exceptions = Object.create(null);
    var cache = Object.create(null);

    data.patterns.split(/\s+/).forEach(function (pattern) {
      var node = trie;
      var points = [0];
      var index;
      var character;

      if (!pattern) {
        return;
      }

      for (index = 0; index < pattern.length; index += 1) {
        character = pattern.charAt(index);

        if (character >= '0' && character <= '9') {
          points[points.length - 1] = Number(character);
        } else {
          node = node[character] || (node[character] = Object.create(null));
          points.push(0);
        }
      }

      node.$ = points;
    });

    data.exceptions.split(/\s+/).forEach(function (entry) {
      var positions = [];
      var word = entry.replace(/-/g, function (_hyphen, offset) {
        positions.push(offset - positions.length);
        return '';
      });

      if (word) {
        exceptions[word] = positions;
      }
    });

    function patternPositions(word) {
      var text = '.' + word + '.';
      var values = new Array(text.length + 1).fill(0);
      var positions = [];
      var start;
      var end;
      var node;
      var index;

      for (start = 0; start < text.length; start += 1) {
        node = trie;

        for (end = start; end < text.length; end += 1) {
          node = node[text.charAt(end)];

          if (!node) {
            break;
          }

          if (node.$) {
            for (index = 0; index < node.$.length; index += 1) {
              values[start + index] = Math.max(values[start + index], node.$[index]);
            }
          }
        }
      }

      // values[i] belongs before text[i], so a break before word[i] reads values[i + 1].
      for (index = 1; index < word.length; index += 1) {
        if (values[index + 1] % 2 === 1) {
          positions.push(index);
        }
      }

      return positions;
    }

    return function (word) {
      var key = word.toLowerCase();
      var positions = cache[key];

      if (!positions) {
        positions = (exceptions[key] || patternPositions(key)).filter(function (position) {
          return position >= data.leftmin && key.length - position >= data.rightmin;
        });
        cache[key] = positions;
      }

      return positions;
    };
  }

  function hyphenWidth(info) {
    var width = hyphenWidths[info.font];

    if (width === undefined) {
      canvas = canvas || document.createElement('canvas').getContext('2d');
      canvas.font = info.font;
      width = canvas.measureText('-').width;
      hyphenWidths[info.font] = width;
    }

    return width;
  }

  function styleOf(element, context) {
    var info = context.styles.get(element);
    var style;

    if (!info) {
      style = window.getComputedStyle(element);
      info = {
        display: style.display,
        collapse: style.whiteSpaceCollapse || 'collapse',
        stretches: style.textJustify !== 'none',
        wordSpacing: parseFloat(style.wordSpacing) || 0,
        hyphenates: (style.hyphens || style.webkitHyphens) === 'auto' &&
          !element.closest(UNHYPHENATED) && element.matches(':lang(en)'),
        inLabel: !!element.closest(LABELS),
        font: [style.fontStyle, style.fontWeight, style.fontSize, style.fontFamily].join(' ')
      };
      context.styles.set(element, info);
    }

    return info;
  }

  /*
   * The paragraph as TeX sees it: boxes (words and the pieces of a hyphenated word, the parts
   * of a formula between its breakpoints, a statement's label), glue (the spaces) and
   * penalties (other places a line may end: at a hyphen, at a breakpoint of a formula, after a
   * label), each with its width, measured while the paragraph stands on one line. It comes
   * in runs, each broken on its own: a run ends at a forced break, or at a block inside the
   * paragraph (display math in a list item). Each breakpoint keeps where in the page its line
   * would end (lineEnd) and where the break goes (breakAt).
   */
  function collectRuns(paragraph, context) {
    var runs = [];
    var run = null;
    var afterSpace = true;

    function addBox(width, left, end, inLabel) {
      if (!run) {
        run = { items: [], left: left };
        runs.push(run);
      }

      run.items.push({ type: 'box', width: width, left: left, end: end, inLabel: inLabel });
      afterSpace = false;
    }

    // Glue or a penalty before the first box of a run would begin a line, where TeX drops it.
    function addBreakable(item) {
      if (run) {
        run.items.push(item);
      }
    }

    /* A space at the end of a line is not set, and neither is one that begins the next. Each
       item is as wide as the distance from where it starts to where the next one does: the run
       stands on one line, and Safari's measure of a range by itself leaves out a space's
       word-spacing and rounds out to whole pixels. A space also has the shrink back that the
       paragraph's narrower spacing took from it. */
    function endRun() {
      var next = null;
      var index;
      var item;

      if (run) {
        while (run.items[run.items.length - 1].type !== 'box') {
          run.items.pop();
        }

        for (index = run.items.length - 1; index >= 0; index -= 1) {
          item = run.items[index];

          if (item.left === undefined) {
            continue;
          }

          if (next && next.left >= item.left) {
            item.width = next.left - item.left + (item.type === 'glue' ? item.shrink : 0);
          }

          next = item;
        }
      }

      run = null;
      afterSpace = true;
    }

    function measureText(node, start, end) {
      context.range.setStart(node, start);
      context.range.setEnd(node, end);
      return context.range.getBoundingClientRect();
    }

    function textBox(node, start, end, info) {
      var rect;

      if (end > start) {
        rect = measureText(node, start, end);
        addBox(rect.width, rect.left, { text: node, offset: end }, info.inLabel);
      }
    }

    function elementBox(element) {
      var rect = element.getBoundingClientRect();

      addBox(rect.width, rect.left, { after: element }, !!element.closest(LABELS));
    }

    function shrinkOf(info) {
      return Math.max(0, context.naturalSpacing - info.wordSpacing);
    }

    // In a statement's label, a line may end at a space only at LABEL_PENALTY.
    function addSpace(glue, info) {
      if (info.inLabel && glue.breakable) {
        addBreakable({
          type: 'penalty',
          width: 0,
          penalty: LABEL_PENALTY,
          flagged: false,
          lineEnd: glue.lineEnd,
          breakAt: glue.breakAt
        });
        glue.breakable = false;
      }

      addBreakable(glue);
    }

    function space(node, start, end, info, collapsible) {
      var shrink = shrinkOf(info);
      var last = run && run.items[run.items.length - 1];
      var rect;

      // Collapsed into the space before it, or dropped at the start of a line.
      if (collapsible && afterSpace) {
        return;
      }

      // The space after a run-in heading, which has no gap of its own, ends the label.
      rect = measureText(node, start, start + 1);
      addSpace({
        type: 'glue',
        width: rect.width + shrink,
        left: rect.left,
        stretch: info.stretches ? context.stretch : 0,
        shrink: shrink,
        breakable: true,
        labelEnd: !info.inLabel && !!last && last.type === 'box' && last.inLabel,
        lineEnd: { text: node, offset: start },
        breakAt: { text: node, offset: end }
      }, info);
      afterSpace = collapsible;
    }

    function special(node, index, info) {
      var character = node.nodeValue.charAt(index);
      var at = { text: node, offset: index };
      var noBreak;
      var shrink;
      var rect;

      if (character === '\u00ad') {
        // A soft hyphen is TeX's \-.
        addBreakable({
          type: 'penalty',
          width: hyphenWidth(info),
          penalty: HYPHEN_PENALTY,
          flagged: true,
          hyphen: true,
          lineEnd: at,
          breakAt: at
        });
      } else if (character === '\u200b') {
        addBreakable({ type: 'penalty', width: 0, penalty: 0, flagged: false, lineEnd: at, breakAt: at });
      } else if (character !== '\u2060' && character !== '\ufeff') {
        // A fixed space: a no-break space stretches and shrinks as a space does, but a line
        // cannot end at it; the others (a label's U+2004 in Safari) keep their width.
        noBreak = NO_BREAK_SPACE.test(character);
        shrink = character === '\u00a0' ? shrinkOf(info) : 0;
        rect = measureText(node, index, index + 1);
        addSpace({
          type: 'glue',
          width: rect.width + shrink,
          left: rect.left,
          stretch: character === '\u00a0' && info.stretches ? context.stretch : 0,
          shrink: shrink,
          breakable: !noBreak,
          lineEnd: at,
          breakAt: { text: node, offset: index + 1 }
        }, info);
        afterSpace = false;
      }
    }

    /* A word is a box, cut where it may break: after an explicit hyphen or a dash, as TeX
       allows at \exhyphenpenalty, and, if the paragraph is hyphenated, where the patterns
       allow a hyphen (TeX's second pass only). As in TeX, a word with a hyphen or a dash of
       its own (finite-dimensional) breaks only there. */
    function word(node, start, end, info) {
      var value = node.nodeValue.slice(start, end);
      var cuts = [];
      var from = 0;
      var index;
      var previous;
      var match;
      var last = run && run.items[run.items.length - 1];

      for (index = 1; index < value.length; index += 1) {
        previous = value.charAt(index - 1);

        if (/[-\u2010]/.test(previous) && LETTER.test(value.charAt(index)) &&
            (index > 1 || (last && last.type === 'box'))) {
          cuts.push({ offset: index, hyphen: false });
        } else if (/[\u2013\u2014]/.test(previous) && /[\p{L}\p{N}]/u.test(value.charAt(index))) {
          cuts.push({ offset: index, hyphen: false });
        }
      }

      if (hyphenate && info.hyphenates && !/[-\u2010\u2013\u2014]/.test(value)) {
        LETTERS.lastIndex = 0;

        while ((match = LETTERS.exec(value))) {
          if (/^[A-Za-z]+$/.test(match[0])) {
            hyphenate(match[0]).forEach(function (position) {
              cuts.push({ offset: match.index + position, hyphen: true });
            });
          }
        }
      }

      cuts.sort(function (a, b) {
        return a.offset - b.offset;
      }).forEach(function (cut) {
        var at = { text: node, offset: start + cut.offset };

        if (cut.offset <= from) {
          return;
        }

        textBox(node, start + from, start + cut.offset, info);
        addBreakable({
          type: 'penalty',
          width: cut.hyphen ? hyphenWidth(info) : 0,
          penalty: cut.hyphen ? HYPHEN_PENALTY : (info.inLabel ? LABEL_PENALTY : EX_HYPHEN_PENALTY),
          flagged: true,
          hyphen: cut.hyphen,
          pattern: cut.hyphen,
          lineEnd: at,
          breakAt: at
        });
        from = cut.offset;
      });

      textBox(node, start + from, end, info);
    }

    function text(node) {
      var value = node.nodeValue;
      var info = styleOf(node.parentElement, context);
      var preservesBreaks = info.collapse !== 'collapse';
      var collapsible = info.collapse === 'collapse' || info.collapse === 'preserve-breaks';
      var index = 0;
      var end;
      var character;

      while (index < value.length) {
        character = value.charAt(index);
        end = index + 1;

        if (character === '\n' && preservesBreaks) {
          endRun();
        } else if (SPACE.test(character)) {
          while (collapsible && end < value.length && SPACE.test(value.charAt(end)) &&
              !(value.charAt(end) === '\n' && preservesBreaks)) {
            end += 1;
          }

          space(node, index, end, info, collapsible);
        } else if (SPECIAL.test(character)) {
          special(node, index, info);
        } else {
          while (end < value.length && !SPECIAL.test(value.charAt(end))) {
            end += 1;
          }

          word(node, index, end, info);
        }

        index = end;
      }
    }

    /* MathJax sets an in-line formula as SVG pieces with an mjx-break between them where the
       formula may break: before a relation (a thick space, size 4 and up) or a binary
       operator. Its space is set and stretched as a word space is, but a line ends there
       only at the penalty before it. */
    function formula(container) {
      Array.prototype.forEach.call(container.children, function (child) {
        var name = child.tagName.toLowerCase();

        if (name === 'svg') {
          elementBox(child);
        } else if (name === 'mjx-break' && child.hasAttribute('newline')) {
          endRun();
        } else if (name === 'mjx-break') {
          addBreakable({
            type: 'penalty',
            width: 0,
            penalty: Number(child.getAttribute('size')) >= 4 ? REL_PENALTY : BIN_OP_PENALTY,
            flagged: false,
            lineEnd: { before: child },
            breakAt: { after: child }
          });
          addBreakable({
            type: 'glue',
            width: child.getBoundingClientRect().width,
            left: child.getBoundingClientRect().left,
            stretch: context.stretch,
            shrink: 0,
            breakable: false
          });
        }
      });
    }

    function element(node) {
      var info;

      if (node.tagName === 'BR') {
        endRun();
        return;
      }

      info = styleOf(node, context);

      if (info.display === 'none') {
        return;
      }

      if (info.display === 'contents') {
        walk(node);
      } else if (info.display.indexOf('inline') !== 0) {
        endRun();
      } else if (node.tagName === 'MJX-CONTAINER') {
        formula(node);
      } else if (node.classList.contains('math-label-gap')) {
        // amsthm never breaks after a statement's label; a line too narrow for the label
        // and what follows it may, setting the label alone on its line.
        elementBox(node);
        addBreakable({
          type: 'penalty',
          width: 0,
          penalty: 0,
          flagged: false,
          labelEnd: true,
          lineEnd: { after: node },
          breakAt: { after: node }
        });
      } else if (info.display !== 'inline' || REPLACED.test(node.tagName) ||
          node.classList.contains('qed')) {
        elementBox(node);
      } else {
        walk(node);
      }
    }

    function walk(parent) {
      var child;

      for (child = parent.firstChild; child; child = child.nextSibling) {
        if (child.nodeType === Node.TEXT_NODE) {
          text(child);
        } else if (child.nodeType === Node.ELEMENT_NODE) {
          element(child);
        }
      }
    }

    walk(paragraph);
    endRun();
    return runs;
  }

  function measure(paragraph, context) {
    var style = window.getComputedStyle(paragraph);
    var rect = paragraph.getBoundingClientRect();
    var left = rect.left + parseFloat(style.borderLeftWidth) + parseFloat(style.paddingLeft);
    var right = rect.right - parseFloat(style.borderRightWidth) - parseFloat(style.paddingRight);
    var fontSize = parseFloat(style.fontSize);

    context.naturalSpacing = parseFloat(paragraph.style.getPropertyValue('--natural-word-spacing')) || 0;
    context.stretch = STRETCH * fontSize;

    return {
      paragraph: paragraph,
      right: right,
      width: right - left,
      spaceStretch: context.stretch,
      runs: collectRuns(paragraph, context)
    };
  }

  function adjustmentRatio(slack, stretch, shrink) {
    if (slack > 0) {
      return stretch > 0 ? slack / stretch : Infinity;
    }

    if (slack < 0) {
      return shrink > 0 ? slack / shrink : -Infinity;
    }

    return 0;
  }

  // TeX's fitness classes: very loose, loose, decent, tight.
  function fitnessClass(ratio) {
    if (ratio > 1) {
      return 0;
    }

    if (ratio > 0.5) {
      return 1;
    }

    return ratio >= -0.5 ? 2 : 3;
  }

  /*
   * Knuth and Plass's algorithm, as TeX's line_break runs it: each feasible breakpoint is
   * reached from every earlier one that can begin its line (the active nodes) and keeps, for
   * each fitness class, the way there with the fewest demerits. Returns the breakpoints of the
   * best way through the run, or null if none keeps every line within the tolerance (or, in
   * the last pass, keeps every line from being too wide).
   */
  function breakRun(run, pass) {
    var items = run.items;
    var tolerance = pass === 1 ? PRETOLERANCE : (pass === 2 ? TOLERANCE : Infinity);
    var width = 0;
    var stretch = 0;
    var shrink = 0;
    var active = [{
      position: -1, line: 0, fitness: 2, width: 0, stretch: 0, shrink: 0,
      demerits: 0, flagged: false, previous: null
    }];
    var index;
    var item;
    var node;
    var breaks = [];

    // The glue and penalties after a break are discarded, up to the next box.
    function totalsAfter(position) {
      var totals = { width: width, stretch: stretch, shrink: shrink };
      var next;

      for (next = position; next < items.length; next += 1) {
        if (items[next].type === 'box' ||
            (next > position && items[next].type === 'penalty' && items[next].penalty <= EJECT_PENALTY)) {
          break;
        }

        if (items[next].type === 'glue') {
          totals.width += items[next].width;
          totals.stretch += items[next].stretch;
          totals.shrink += items[next].shrink;
        }
      }

      return totals;
    }

    function tryBreak(position) {
      var breakpoint = items[position];
      var isPenalty = breakpoint.type === 'penalty';
      var penalty = isPenalty ? breakpoint.penalty : 0;
      var flagged = isPenalty && breakpoint.flagged;
      var forced = penalty <= EJECT_PENALTY;
      var candidates = [];
      var totals = null;

      active = active.filter(function (from) {
        var slack = run.lineWidth(from.line) - (width - from.width + (isPenalty ? breakpoint.width : 0));
        var ratio = adjustmentRatio(slack, stretch - from.stretch, shrink - from.shrink);
        var badness;
        var demerits;
        var fitness;

        if (ratio >= -1) {
          if (ratio < Infinity) {
            badness = 100 * Math.pow(Math.abs(ratio), 3);
          } else if (breakpoint.labelEnd) {
            badness = LABEL_LINE_BADNESS;
          } else {
            badness = 100 * Math.pow(slack / run.spaceStretch, 3);
          }

          if (pass < 3) {
            badness = Math.min(INF_BAD, badness);
          }

          if (badness <= tolerance) {
            demerits = Math.pow(LINE_PENALTY + badness, 2);

            if (penalty > 0) {
              demerits += penalty * penalty;
            } else if (penalty > EJECT_PENALTY) {
              demerits -= penalty * penalty;
            }

            if (flagged && from.flagged) {
              demerits += DOUBLE_HYPHEN_DEMERITS;
            } else if (forced && from.flagged) {
              demerits += FINAL_HYPHEN_DEMERITS;
            }

            fitness = fitnessClass(ratio);

            if (Math.abs(fitness - from.fitness) > 1) {
              demerits += ADJ_DEMERITS;
            }

            demerits += from.demerits;

            if (!candidates[fitness] || demerits < candidates[fitness].demerits) {
              candidates[fitness] = { from: from, demerits: demerits };
            }
          }
        }

        // A line from here on would only be longer; a forced break ends every line.
        return ratio >= -1 && !forced;
      });

      candidates.forEach(function (candidate, fitness) {
        totals = totals || totalsAfter(position);
        active.push({
          position: position,
          line: candidate.from.line + 1,
          fitness: fitness,
          width: totals.width,
          stretch: totals.stretch,
          shrink: totals.shrink,
          demerits: candidate.demerits,
          flagged: flagged,
          previous: candidate.from
        });
      });
    }

    for (index = 0; index < items.length && active.length > 0; index += 1) {
      item = items[index];

      if (item.type === 'box') {
        width += item.width;
      } else if (item.type === 'glue') {
        // Glue is a breakpoint where it follows a box.
        if (item.breakable && items[index - 1].type === 'box') {
          tryBreak(index);
        }

        width += item.width;
        stretch += item.stretch;
        shrink += item.shrink;
      } else if (item.penalty < INF_PENALTY && (pass > 1 || !item.pattern)) {
        tryBreak(index);
      }
    }

    if (active.length === 0) {
      return null;
    }

    node = active.reduce(function (best, next) {
      return next.demerits < best.demerits ? next : best;
    });

    for (; node.previous; node = node.previous) {
      breaks.unshift(node.position);
    }

    return breaks;
  }

  /* The lines of a run, as what to insert into the page: after each line but the last, a
     hyphen if it ends in one and the break; at the end of a line set at its natural spacing,
     a filler as wide as the room left. */
  function setLines(run, breaks, insertions) {
    var items = run.items;
    var start = 0;

    breaks.forEach(function (end, line) {
      var breakpoint = items[end];
      var last = line === breaks.length - 1;
      var natural = 0;
      var stretch = 0;
      var pending = 0;
      var pendingStretch = 0;
      var lastBox = -1;
      var index;
      var item;
      var room;

      while (start < end && items[start].type !== 'box') {
        start += 1;
      }

      // Glue counts only between boxes: at the end of the line it is not set.
      for (index = start; index < end; index += 1) {
        item = items[index];

        if (item.type === 'box') {
          natural += pending + item.width;
          stretch += pendingStretch;
          pending = 0;
          pendingStretch = 0;
          lastBox = index;
        } else if (item.type === 'glue') {
          pending += item.width;
          pendingStretch += item.stretch;
        }
      }

      if (breakpoint.hyphen) {
        natural += breakpoint.width;
      }

      room = run.lineWidth(line) - natural;

      if (!last) {
        if (breakpoint.hyphen) {
          insertions.push({ kind: 'hyphen', at: breakpoint.lineEnd });
        }

        if (room > 0 && stretch <= 0) {
          insertions.push({ kind: 'fill', width: room, at: breakpoint.lineEnd });
        }

        insertions.push({ kind: 'break', at: breakpoint.breakAt });
      } else if (room > 0 && lastBox >= 0) {
        insertions.push({ kind: 'fill', width: room, at: items[lastBox].end });
      }

      start = end + 1;
    });
  }

  // TeX ends a paragraph with \penalty10000 \hskip\parfillskip \penalty-10000.
  function finish(run) {
    run.items.push(
      { type: 'penalty', width: 0, penalty: INF_PENALTY, flagged: false },
      { type: 'glue', width: 0, stretch: 1e9, shrink: 0, breakable: false },
      { type: 'penalty', width: 0, penalty: EJECT_PENALTY, flagged: false }
    );
  }

  function layOut(plan) {
    var insertions = [];
    var set = plan.runs.length > 0 && plan.runs.every(function (run) {
      var breaks;

      // The first line of a run starts where its first box does: after the indent.
      run.lineWidth = function (line) {
        return (line === 0 ? plan.right - run.left : plan.width) - SAFETY;
      };
      run.spaceStretch = plan.spaceStretch;
      finish(run);
      breaks = breakRun(run, 1) || breakRun(run, 2) || breakRun(run, 3);

      if (breaks) {
        setLines(run, breaks, insertions);
      }

      return !!breaks;
    });

    return set ? insertions : null;
  }

  function place(node, at) {
    var range;

    if (at.text) {
      range = document.createRange();
      range.setStart(at.text, at.offset);
      range.insertNode(node);
    } else if (at.after) {
      at.after.parentNode.insertBefore(node, at.after.nextSibling);
    } else {
      at.before.parentNode.insertBefore(node, at.before);
    }
  }

  // Last to first, so that a text node split for one insertion still holds the earlier ones.
  function insert(insertions) {
    var index;
    var insertion;
    var span;

    for (index = insertions.length - 1; index >= 0; index -= 1) {
      insertion = insertions[index];
      span = document.createElement('span');
      span.className = 'typeset-' + insertion.kind;
      span.setAttribute('aria-hidden', 'true');

      if (insertion.kind === 'fill') {
        span.style.setProperty('--fill', insertion.width.toFixed(3) + 'px');
      }

      place(span, insertion.at);
    }
  }

  function reset(postBody) {
    var parents = [];

    postBody.querySelectorAll(INSERTED).forEach(function (span) {
      if (parents.indexOf(span.parentNode) === -1) {
        parents.push(span.parentNode);
      }

      span.parentNode.removeChild(span);
    });

    parents.forEach(function (parent) {
      parent.normalize();
    });
  }

  // Back to the browser's own lines, until the breaks are worked out again.
  function release(postBody) {
    postBody.querySelectorAll('.typeset-paragraph').forEach(function (paragraph) {
      paragraph.classList.remove('typeset-paragraph');
    });
  }

  /* A justified paragraph or list item outside code and tables. One that holds blocks of its
     own (the paragraphs of a loose list item, a nested list) is left to the browser; those
     blocks are set on their own. */
  function isCandidate(element) {
    return !element.closest('pre, table, figure') &&
      !element.querySelector(BLOCKS) &&
      window.getComputedStyle(element).textAlign === 'justify';
  }

  function typeset(postBody) {
    var paragraphs;
    var spacings;
    var context;
    var plans;

    reset(postBody);
    paragraphs = Array.prototype.filter.call(postBody.querySelectorAll('p, li'), isCandidate);

    // The post's own word spacing, read before post.css narrows it.
    spacings = paragraphs.map(function (paragraph) {
      var style = window.getComputedStyle(paragraph);
      var spacing = paragraph.style.getPropertyValue('--natural-word-spacing') || style.wordSpacing;

      spacing = /px$/.test(spacing) ? parseFloat(spacing) : 0;
      return [spacing, spacing - SHRINK * parseFloat(style.fontSize)];
    });

    paragraphs.forEach(function (paragraph, index) {
      paragraph.style.setProperty('--natural-word-spacing', spacings[index][0] + 'px');
      paragraph.style.setProperty('--typeset-word-spacing', spacings[index][1] + 'px');
      paragraph.classList.add('typeset-paragraph');
    });

    postBody.classList.add('typeset-measuring');
    context = { styles: new Map(), range: document.createRange() };

    try {
      plans = paragraphs.map(function (paragraph) {
        return measure(paragraph, context);
      });
    } finally {
      postBody.classList.remove('typeset-measuring');
    }

    plans.forEach(function (plan) {
      var insertions = layOut(plan);

      if (insertions) {
        insert(insertions);
      } else {
        plan.paragraph.classList.remove('typeset-paragraph');
      }
    });
  }

  function run(postBody) {
    try {
      typeset(postBody);
    } catch (error) {
      release(postBody);
      reset(postBody);
      window.console.error(error);
    }
  }

  // While the column changes width the browser sets the lines; they are typeset again once
  // it has settled.
  function watch(postBody) {
    var width = null;
    var timer = 0;

    if (watching || typeof window.ResizeObserver !== 'function') {
      return;
    }

    watching = true;
    new window.ResizeObserver(function (entries) {
      var nextWidth = entries[0].contentRect.width;

      if (width !== null && nextWidth !== width) {
        release(postBody);
        window.clearTimeout(timer);
        timer = window.setTimeout(function () {
          run(postBody);
        }, 150);
      }

      width = nextWidth;
    }).observe(postBody);
  }

  window.lineBreaking = {
    typeset: function (postBody) {
      if (!supported) {
        return Promise.resolve();
      }

      if (!hyphenate && window.hyphenationEnUs) {
        hyphenate = buildHyphenator(window.hyphenationEnUs);
      }

      return Promise.resolve(document.fonts && document.fonts.ready).then(function () {
        run(postBody);
        watch(postBody);
      });
    }
  };
}());
