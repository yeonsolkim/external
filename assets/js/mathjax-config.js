window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true
  },
  options: {
    enableMenu: false
  },
  startup: {
    pageReady() {
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
