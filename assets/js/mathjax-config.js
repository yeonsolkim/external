(function () {
  function promoteListItemDisplayMath() {
    var elements = document.querySelectorAll('.post-body li > p, .post-body li');
    var trailingDisplayCandidate = /(?:\s*<br\s*\/?>\s*|\s*\n\s*)\\\(([\s\S]*?)\\\)\s*$/i;

    elements.forEach(function (element) {
      if (element.closest('pre, code, script, style, textarea, noscript, mjx-container')) {
        return;
      }

      var html = element.innerHTML;

      if (html.indexOf('\\(') === -1 || !trailingDisplayCandidate.test(html)) {
        return;
      }

      element.innerHTML = html.replace(
        trailingDisplayCandidate,
        function (_match, math) {
          return '\n\\[' + math.trim() + '\\]';
        }
      );
    });
  }

  function markListItemsWithDisplayMath() {
    var listItems = document.querySelectorAll('.post-body li');

    listItems.forEach(function (listItem) {
      if (listItem.closest('pre, code, script, style, textarea, noscript, mjx-container')) {
        return;
      }

      if (listItem.innerHTML.indexOf('\\[') !== -1) {
        listItem.classList.add('list-item-display-math');

        var content = listItem.innerHTML.trim()
          .replace(/^<p>\s*/i, '')
          .replace(/\s*<\/p>$/i, '')
          .trim();

        if (/^\\\[[\s\S]*\\\]$/.test(content)) {
          listItem.classList.add('list-item-display-math-only');
        }
      }
    });
  }

  // The element whose ::before draws an item's label: the item itself, or the <p> a loose
  // item opens with (post.css hangs the label from that paragraph).
  function labelHost(listItem) {
    var first = listItem.firstElementChild;

    return first && first.tagName === 'P' ? first : listItem;
  }

  // post.css makes each list's label box as wide as its widest label.
  function measureLabelWidth(list, listItems, labelText) {
    if (listItems.length === 0) {
      list.style.removeProperty('--list-labelwidth');
      return;
    }

    var labelStyle = window.getComputedStyle(labelHost(listItems[0]), '::before');
    var measurer = document.createElement('span');
    measurer.style.position = 'absolute';
    measurer.style.visibility = 'hidden';
    measurer.style.whiteSpace = 'nowrap';
    measurer.style.fontFamily = labelStyle.fontFamily;
    measurer.style.fontSize = labelStyle.fontSize;
    measurer.style.fontStyle = labelStyle.fontStyle;
    measurer.style.fontWeight = labelStyle.fontWeight;
    measurer.style.letterSpacing = labelStyle.letterSpacing;
    document.body.appendChild(measurer);

    var maxWidth = 0;
    listItems.forEach(function (listItem) {
      measurer.textContent = labelText(listItem);
      maxWidth = Math.max(maxWidth, measurer.getBoundingClientRect().width);
    });

    document.body.removeChild(measurer);
    list.style.setProperty('--list-labelwidth', Math.ceil(maxWidth) + 'px');
  }

  function applyOrderedListMarkerPrefixes() {
    var orderedLists = document.querySelectorAll('.post-body ol');

    function readMarkerStyle(orderedList) {
      var markerStyle = orderedList.getAttribute('data-marker-style') ||
        orderedList.getAttribute('marker-style') ||
        '';

      markerStyle = markerStyle.trim().toLowerCase();

      if (markerStyle) {
        return markerStyle;
      }

      if (orderedList.classList.contains('reference') || orderedList.hasAttribute('reference')) {
        return 'reference';
      }

      // kramdown's footnote list; post.css sets the bare number as a superscript.
      if (orderedList.parentElement && orderedList.parentElement.classList.contains('footnotes')) {
        return 'footnote';
      }

      return '';
    }

    // enumerate's counters by depth, as \theenumi–\theenumiv print them: \arabic, \alph,
    // \roman, \Alph. Only ordered lists count; an ul in between does not.
    function enumerateDepth(orderedList) {
      var depth = 0;
      var element;

      for (element = orderedList; element && !element.classList.contains('post-body'); element = element.parentElement) {
        if (element.tagName === 'OL') {
          depth += 1;
        }
      }

      return depth;
    }

    function alphabetic(number) {
      var text = '';

      while (number > 0) {
        text = String.fromCharCode(97 + (number - 1) % 26) + text;
        number = Math.floor((number - 1) / 26);
      }

      return text;
    }

    function roman(number) {
      var numerals = [
        [1000, 'm'], [900, 'cm'], [500, 'd'], [400, 'cd'], [100, 'c'], [90, 'xc'],
        [50, 'l'], [40, 'xl'], [10, 'x'], [9, 'ix'], [5, 'v'], [4, 'iv'], [1, 'i']
      ];
      var text = '';

      numerals.forEach(function (numeral) {
        while (number >= numeral[0]) {
          text += numeral[1];
          number -= numeral[0];
        }
      });

      return text;
    }

    function formatCounter(number, depth) {
      if (number < 1) {
        return String(number);
      }

      switch ((depth - 1) % 4) {
        case 1: return alphabetic(number);
        case 2: return roman(number);
        case 3: return alphabetic(number).toUpperCase();
        default: return String(number);
      }
    }

    function formatMarkerText(markerStyle, markerText) {
      if (markerStyle === 'reference') {
        return '[' + markerText + ']';
      }

      if (markerStyle === 'footnote') {
        return markerText;
      }

      return '(' + markerText + ')';
    }

    orderedLists.forEach(function (orderedList) {
      var prefix = orderedList.getAttribute('data-marker-prefix') ||
        orderedList.getAttribute('marker-prefix') ||
        '';
      var markerStyle = readMarkerStyle(orderedList);
      // Bibliography and footnote numbers stay arabic wherever they sit.
      var depth = markerStyle ? 1 : enumerateDepth(orderedList);
      var reversed = orderedList.hasAttribute('reversed');
      var start = parseInt(
        orderedList.getAttribute('start') ||
          orderedList.getAttribute('data-start') ||
          orderedList.getAttribute(':start'),
        10
      );
      var listItems = Array.prototype.filter.call(orderedList.children, function (child) {
        return child.tagName === 'LI';
      });
      var number = Number.isNaN(start) ? (reversed ? listItems.length : 1) : start;
      prefix = prefix.trim();

      listItems.forEach(function (listItem) {
        var itemNumber = parseInt(listItem.getAttribute('value'), 10);

        if (!Number.isNaN(itemNumber)) {
          number = itemNumber;
        }

        if (prefix) {
          listItem.setAttribute('data-marker-prefix', prefix);
        } else {
          listItem.removeAttribute('data-marker-prefix');
        }

        var markerText = formatMarkerText(markerStyle, (prefix || '') + formatCounter(number, depth));
        var firstParagraph = listItem.firstElementChild;

        listItem.setAttribute('data-marker-text', markerText);

        // A loose item opens with a block <p>; post.css hangs the marker from
        // that paragraph so it shares the paragraph's first line.
        if (firstParagraph && firstParagraph.tagName === 'P') {
          firstParagraph.setAttribute('data-marker-text', markerText);
        }

        number += reversed ? -1 : 1;
      });

      measureLabelWidth(orderedList, listItems, function (listItem) {
        return listItem.getAttribute('data-marker-text') || '';
      });
    });
  }

  // Itemize labels come from post.css (\labelitemi–iv by depth); measure them as above.
  function measureItemizeLabels() {
    document.querySelectorAll('.post-body ul').forEach(function (list) {
      var listItems = Array.prototype.filter.call(list.children, function (child) {
        return child.tagName === 'LI';
      });

      measureLabelWidth(list, listItems, function (listItem) {
        var content = window.getComputedStyle(labelHost(listItem), '::before').content;

        return content.charAt(0) === '"' ? content.slice(1, -1) : '';
      });
    });
  }

  function prepareMathDelimiters() {
    promoteListItemDisplayMath();
    markListItemsWithDisplayMath();
    applyOrderedListMarkerPrefixes();
    measureItemizeLabels();
    normalizeInlineMathDelimiters();
  }

  function normalizeInlineMathDelimiters() {
    function isEscaped(text, index) {
      var backslashes = 0;
      index -= 1;

      while (index >= 0 && text[index] === '\\') {
        backslashes += 1;
        index -= 1;
      }

      return backslashes % 2 === 1;
    }

    function findInlineMathRanges(text) {
      var ranges = [];
      var start = -1;

      for (var index = 0; index < text.length; index += 1) {
        if (text[index] !== '$' || isEscaped(text, index)) {
          continue;
        }

        if (text[index + 1] === '$' || text[index - 1] === '$') {
          continue;
        }

        if (start === -1) {
          start = index;
        } else {
          ranges.push({ start: start, end: index });
          start = -1;
        }
      }

      return ranges;
    }

    function getAttributeValue(rawTag, attributeName) {
      var pattern = new RegExp("\\s" + attributeName + "\\s*=\\s*(\"([^\"]*)\"|'([^']*)'|([^\\s>]+))", 'i');
      var match = rawTag.match(pattern);

      if (!match) {
        return '';
      }

      return match[2] || match[3] || match[4] || '';
    }

    function tokenizeHtml(html) {
      var tokens = [];
      var pattern = /<a\b[^>]*>[\s\S]*?<\/a>|<\/?em\b[^>]*>/gi;
      var lastIndex = 0;
      var match;

      while ((match = pattern.exec(html))) {
        var raw = match[0];
        var synthetic = '_';

        if (match.index > lastIndex) {
          tokens.push({
            raw: html.slice(lastIndex, match.index),
            synthetic: html.slice(lastIndex, match.index),
            rawStart: lastIndex,
            rawEnd: match.index
          });
        }

        if (/^<a\b/i.test(raw)) {
          synthetic = raw.replace(
            /^<a\b[^>]*>([\s\S]*?)<\/a>$/i,
            function (_anchor, label) {
              return '[' + label + '](' + getAttributeValue(raw, 'href') + ')';
            }
          );
        }

        tokens.push({
          raw: raw,
          synthetic: synthetic,
          rawStart: match.index,
          rawEnd: pattern.lastIndex
        });

        lastIndex = pattern.lastIndex;
      }

      if (lastIndex < html.length) {
        tokens.push({
          raw: html.slice(lastIndex),
          synthetic: html.slice(lastIndex),
          rawStart: lastIndex,
          rawEnd: html.length
        });
      }

      return tokens;
    }

    function buildSyntheticMap(tokens) {
      var synthetic = '';
      var map = [];

      tokens.forEach(function (token) {
        for (var index = 0; index < token.synthetic.length; index += 1) {
          synthetic += token.synthetic[index];
          map.push({
            rawStart: token.rawStart + (token.raw === token.synthetic ? index : 0),
            rawEnd: token.raw === token.synthetic ? token.rawStart + index + 1 : token.rawEnd
          });
        }
      });

      return {
        synthetic: synthetic,
        map: map
      };
    }

    function normalizeHtml(html) {
      var tokens = tokenizeHtml(html);
      var mapped = buildSyntheticMap(tokens);
      var ranges = findInlineMathRanges(mapped.synthetic);

      if (ranges.length === 0) {
        return html;
      }

      ranges.slice().reverse().forEach(function (range) {
        var rawStart = mapped.map[range.start].rawStart;
        var rawEnd = mapped.map[range.end].rawEnd;
        var replacement = '\\(' + mapped.synthetic.slice(range.start + 1, range.end) + '\\)';
        html = html.slice(0, rawStart) + replacement + html.slice(rawEnd);
      });

      return html;
    }

    var elements = document.querySelectorAll('.post-body p, .post-body li, .post-body th, .post-body td');

    elements.forEach(function (element) {
      if (element.closest('pre, code, script, style, textarea, noscript, mjx-container')) {
        return;
      }

      if (element.innerHTML.indexOf('$') === -1) {
        return;
      }

      element.innerHTML = normalizeHtml(element.innerHTML);
    });
  }

  function normalizeInlineMathWhenReady() {
    if (document.readyState === 'loading') {
      return new Promise(function (resolve) {
        document.addEventListener('DOMContentLoaded', function () {
          prepareMathDelimiters();
          resolve();
        }, { once: true });
      });
    }

    prepareMathDelimiters();
    return Promise.resolve();
  }

  function isIOSTouchDevice() {
    var userAgent = navigator.userAgent || '';
    var platform = navigator.platform || '';

    return /iPad|iPhone|iPod/.test(userAgent) ||
      (platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  function isIPhoneDevice() {
    return /iPhone|iPod/.test(navigator.userAgent || '');
  }

  function shouldScrollDisplayMath() {
    if (typeof window.matchMedia !== 'function') {
      return isIOSTouchDevice();
    }

    return isIOSTouchDevice() ||
      window.matchMedia('(max-width: 768px)').matches ||
      window.matchMedia('(pointer: coarse)').matches;
  }

  function shouldUseTouchMathWeight() {
    if (typeof window.matchMedia !== 'function') {
      return isIOSTouchDevice();
    }

    return isIOSTouchDevice() ||
      window.matchMedia('(max-width: 768px)').matches ||
      window.matchMedia('(pointer: coarse)').matches;
  }

  var displayMathOverflowFrame = 0;

  function updateDisplayMathOverflow() {
    displayMathOverflowFrame = 0;

    var elements = document.querySelectorAll(
      '.post-body mjx-container[display="true"], .post-body .MathJax_Display'
    );

    elements.forEach(function (element) {
      var isOverflowing = element.scrollWidth - element.clientWidth > 1;

      if (isOverflowing) {
        element.classList.add('math-overflowing');
      } else {
        element.classList.remove('math-overflowing');
      }
    });
  }

  function scheduleDisplayMathOverflowCheck() {
    if (displayMathOverflowFrame) {
      return;
    }

    displayMathOverflowFrame = window.requestAnimationFrame(updateDisplayMathOverflow);
  }

  window.normalizeInlineMathDelimiters = normalizeInlineMathDelimiters;
  window.promoteListItemDisplayMath = promoteListItemDisplayMath;
  window.markListItemsWithDisplayMath = markListItemsWithDisplayMath;
  window.applyOrderedListMarkerPrefixes = applyOrderedListMarkerPrefixes;
  window.measureItemizeLabels = measureItemizeLabels;
  window.prepareMathDelimiters = prepareMathDelimiters;
  window.updateDisplayMathOverflow = updateDisplayMathOverflow;
  normalizeInlineMathWhenReady();

  window.addEventListener('resize', scheduleDisplayMathOverflowCheck);
  window.addEventListener('orientationchange', scheduleDisplayMathOverflowCheck);

  var iOSTouchDevice = isIOSTouchDevice();
  var iPhoneDevice = isIPhoneDevice();
  var scrollDisplayMath = shouldScrollDisplayMath();
  var touchMathWeight = shouldUseTouchMathWeight();
  var mathBlacker = iPhoneDevice ? 0 : (touchMathWeight ? 2 : 9);

  // post.css strokes commutative-diagram glyphs to the same weight.
  document.documentElement.style.setProperty('--math-blacker', String(mathBlacker));

  window.MathJax = {
    loader: {
      load: ['[tex]/mathtools', '[tex]/unicode', '[tex]/html']
    },
    tex: {
      packages: {'[+]': ['mathtools', 'unicode', 'html']},
      inlineMath: [['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      macros: {
        // The system-font star is roughly 0.9em wide, so scale it down toward
        // \circ's 0.3em and lift it onto the math axis. Its outline is much
        // thinner than \circ's ring, so stroke it (in the glyph's 1000-per-em
        // units) to bring the weight up to match. Unlike the math font's own
        // glyphs, which are paths, this one is real SVG <text> and inherits
        // font-style/weight from the surrounding prose, so an italic statement
        // body would slant it; pin both to normal.
        whitestar: '\\mathbin{\\raise0.07em{\\style{font-size:55%;stroke-width:45px;font-style:normal;font-weight:normal}{\\unicode[serif]{x2606}}}}',
        lowparen: [
          '\\mathinner{\\mathopen{\\lower .3em {\\bigg(}}#1\\mathclose{\\lower .3em {\\bigg)}}}',
          1
        ]
      }
    },
    options: {
      enableMenu: false
    },
    startup: {
      pageReady() {
        return normalizeInlineMathWhenReady().then(function () {
          return MathJax.startup.defaultPageReady();
        }).then(function () {
          updateDisplayMathOverflow();

          return new Promise(function (resolve) {
            window.requestAnimationFrame(function () {
              updateDisplayMathOverflow();
              resolve();
            });
          });
        });
      }
    },
    output: {
      font: 'mathjax-newcm',
      displayOverflow: scrollDisplayMath ? 'overflow' : 'linebreak',
      linebreaks: {
        inline: true,
        width: '100%',
        lineleading: 0.2
      }
    },
    svg: {
      blacker: mathBlacker,
      fontCache: 'none',
      exFactor: 0.5,
      displayAlign: 'center',
      displayOverflow: scrollDisplayMath ? 'overflow' : 'linebreak',
      linebreaks: {
        inline: true,
        width: '100%',
        lineleading: 0.2
      }
    }
  };
}());
