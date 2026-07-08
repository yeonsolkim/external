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

      return '';
    }

    function formatMarkerText(markerStyle, markerText) {
      if (markerStyle === 'reference') {
        return '[' + markerText + ']';
      }

      return '(' + markerText + ')';
    }

    function measureMarkerWidth(orderedList, listItems) {
      if (listItems.length === 0) {
        orderedList.style.removeProperty('--ol-marker-width');
        return;
      }

      var markerStyle = window.getComputedStyle(listItems[0], '::before');
      var measurer = document.createElement('span');
      measurer.style.position = 'absolute';
      measurer.style.visibility = 'hidden';
      measurer.style.whiteSpace = 'nowrap';
      measurer.style.fontFamily = markerStyle.fontFamily;
      measurer.style.fontSize = markerStyle.fontSize;
      measurer.style.fontStyle = markerStyle.fontStyle;
      measurer.style.fontWeight = markerStyle.fontWeight;
      measurer.style.letterSpacing = markerStyle.letterSpacing;
      document.body.appendChild(measurer);

      var maxWidth = 0;
      listItems.forEach(function (listItem) {
        measurer.textContent = listItem.getAttribute('data-marker-text') || '';
        maxWidth = Math.max(maxWidth, measurer.getBoundingClientRect().width);
      });

      document.body.removeChild(measurer);
      orderedList.style.setProperty('--ol-marker-width', Math.ceil(maxWidth) + 'px');
    }

    orderedLists.forEach(function (orderedList) {
      var prefix = orderedList.getAttribute('data-marker-prefix') ||
        orderedList.getAttribute('marker-prefix') ||
        '';
      var markerStyle = readMarkerStyle(orderedList);
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

        listItem.setAttribute(
          'data-marker-text',
          formatMarkerText(markerStyle, (prefix || '') + number)
        );

        number += reversed ? -1 : 1;
      });

      measureMarkerWidth(orderedList, listItems);
    });
  }

  function prepareMathDelimiters() {
    promoteListItemDisplayMath();
    markListItemsWithDisplayMath();
    applyOrderedListMarkerPrefixes();
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
      '.math-scroll mjx-container[display="true"], .math-scroll .MathJax_Display'
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
  window.prepareMathDelimiters = prepareMathDelimiters;
  window.updateDisplayMathOverflow = updateDisplayMathOverflow;
  normalizeInlineMathWhenReady();

  window.addEventListener('resize', scheduleDisplayMathOverflowCheck);
  window.addEventListener('orientationchange', scheduleDisplayMathOverflowCheck);

  var iOSTouchDevice = isIOSTouchDevice();
  var scrollDisplayMath = shouldScrollDisplayMath();
  var touchMathWeight = shouldUseTouchMathWeight();

  window.MathJax = {
    tex: {
      inlineMath: [['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true
    },
    options: {
      enableMenu: false
    },
    startup: {
      pageReady() {
        return normalizeInlineMathWhenReady().then(function () {
          return MathJax.startup.defaultPageReady();
        }).then(
          () => {
            updateDisplayMathOverflow();
            window.setTimeout(updateDisplayMathOverflow, 100);
            document.documentElement.classList.remove('mathjax-loading');
          },
          (error) => {
            document.documentElement.classList.remove('mathjax-loading');
            throw error;
          }
        );
      }
    },
    output: {
      font: 'mathjax-tex',
      displayOverflow: scrollDisplayMath ? 'overflow' : 'linebreak',
      linebreaks: {
        inline: true,
        width: '100%',
        lineleading: 0.2
      }
    },
    svg: {
      blacker: touchMathWeight ? 7 : 9,
      fontCache: 'none',
      scale: 0.9,
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
