function normalizeInlineMathDelimiters() {
  var roots = document.querySelectorAll('.post-body');
  var skipTags = {
    CODE: true,
    PRE: true,
    SCRIPT: true,
    STYLE: true,
    TEXTAREA: true,
    NOSCRIPT: true
  };

  function isEscaped(text, index) {
    var backslashes = 0;
    index -= 1;

    while (index >= 0 && text[index] === '\\') {
      backslashes += 1;
      index -= 1;
    }

    return backslashes % 2 === 1;
  }

  function convertText(text) {
    var result = '';
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
        result += text.slice(0, start) + '\\(' + text.slice(start + 1, index) + '\\)';
        text = text.slice(index + 1);
        index = -1;
        start = -1;
      }
    }

    return result + text;
  }

  roots.forEach(function (root) {
    var walker = document.createTreeWalker(root, 4, {
      acceptNode: function (node) {
        var parent = node.parentElement;

        while (parent && parent !== root) {
          if (skipTags[parent.tagName] || parent.tagName === 'MJX-CONTAINER') {
            return 2;
          }

          parent = parent.parentElement;
        }

        return node.nodeValue.indexOf('$') === -1 ? 2 : 1;
      }
    });
    var nodes = [];
    var node;

    while ((node = walker.nextNode())) {
      nodes.push(node);
    }

    nodes.forEach(function (textNode) {
      textNode.nodeValue = convertText(textNode.nodeValue);
    });
  });
}

normalizeInlineMathDelimiters();

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
      normalizeInlineMathDelimiters();

      return MathJax.startup.defaultPageReady().then(
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
    displayOverflow: 'linebreak',
    linebreaks: {
      inline: true,
      width: '100%',
      lineleading: 0.2
    }
  },
  svg: {
    fontCache: 'global',
    scale: 0.89,
    exFactor: 0.5,
    displayAlign: 'center',
    displayOverflow: 'linebreak',
    linebreaks: {
      inline: true,
      width: '100%',
      lineleading: 0.2
    }
  }
};
