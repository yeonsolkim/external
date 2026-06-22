(function () {
  function promoteListItemDisplayMath() {
    var elements = document.querySelectorAll('.post-body li > p');

    elements.forEach(function (element) {
      if (element.closest('pre, code, script, style, textarea, noscript, mjx-container')) {
        return;
      }

      var html = element.innerHTML;

      if (html.indexOf('\\(') === -1 || !/<br\s*\/?>/i.test(html)) {
        return;
      }

      element.innerHTML = html.replace(
        /\s*<br\s*\/?>\s*\\\(([\s\S]*?)\\\)\s*$/i,
        function (_match, math) {
          return '\n\\[' + math.trim() + '\\]';
        }
      );
    });
  }

  function prepareMathDelimiters() {
    promoteListItemDisplayMath();
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

    function tokenizeHtml(html) {
      var tokens = [];
      var pattern = /<\/?em\b[^>]*>/gi;
      var lastIndex = 0;
      var match;

      while ((match = pattern.exec(html))) {
        if (match.index > lastIndex) {
          tokens.push({
            raw: html.slice(lastIndex, match.index),
            synthetic: html.slice(lastIndex, match.index),
            rawStart: lastIndex,
            rawEnd: match.index
          });
        }

        tokens.push({
          raw: match[0],
          synthetic: '_',
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

    var elements = document.querySelectorAll('.post-body p, .post-body li');

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

  window.normalizeInlineMathDelimiters = normalizeInlineMathDelimiters;
  window.promoteListItemDisplayMath = promoteListItemDisplayMath;
  window.prepareMathDelimiters = prepareMathDelimiters;
  normalizeInlineMathWhenReady();

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
      displayOverflow: scrollDisplayMath ? 'scroll' : 'linebreak',
      linebreaks: {
        inline: true,
        width: '100%',
        lineleading: 0.2
      }
    },
    svg: {
      blacker: touchMathWeight ? 7 : 11,
      fontCache: 'none',
      scale: 0.85,
      exFactor: 0.5,
      displayAlign: 'center',
      displayOverflow: scrollDisplayMath ? 'scroll' : 'linebreak',
      linebreaks: {
        inline: true,
        width: '100%',
        lineleading: 0.2
      }
    }
  };
}());
