---
---
(function () {
  'use strict';

  var labelPattern = /^(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example)\s+(\d+(?:\.\d+)+)\.?/;
  var sourceLabelPattern = /(?:\*\*|<(?:strong|b)\b[^>]*>)\s*(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example)\s+(\d+(?:\.\d+)+)\.?(?=\s|\*|\)|<\/(?:strong|b)>)/g;
  var referencePattern = /\b(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example)\s+(\d+(?:\.\d+)+)\b/g;
  var labelSources = {
    "calculus": [
      {%- assign first_source = true -%}
      {%- for post in site.posts -%}
        {%- assign category_path = post.category_path | join: "/" -%}
        {%- if category_path contains "II. Calculus" -%}
          {%- unless first_source -%},{%- endunless -%}
          {
            url: {{ post.url | relative_url | jsonify }},
            content: {{ post.content | jsonify }}
          }
          {%- assign first_source = false -%}
        {%- endif -%}
      {%- endfor -%}
    ],
    "linear-algebra": [
      {%- assign first_source = true -%}
      {%- for post in site.posts -%}
        {%- assign category_path = post.category_path | join: "/" -%}
        {%- if category_path contains "III. Linear Algebra" -%}
          {%- unless first_source -%},{%- endunless -%}
          {
            url: {{ post.url | relative_url | jsonify }},
            content: {{ post.content | jsonify }}
          }
          {%- assign first_source = false -%}
        {%- endif -%}
      {%- endfor -%}
    ]
  };

  function getPostBody() {
    return document.querySelector('.post-body.math-scroll') || document.querySelector('.post-body');
  }

  function getReferenceScope() {
    var scopeElement = document.querySelector('[data-reference-scope]');

    if (!scopeElement) {
      return '';
    }

    return scopeElement.getAttribute('data-reference-scope') || '';
  }

  function normalizeSpace(text) {
    return text.replace(/\s+/g, ' ').trim();
  }

  function makeLabel(kind, number) {
    return kind + ' ' + number;
  }

  function makeAnchorId(kind, number) {
    return kind.toLowerCase() + '-' + number.replace(/\./g, '-');
  }

  function getScrollElement() {
    return document.scrollingElement || document.documentElement;
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function getCenteredScrollTop(target) {
    var scrollElement = getScrollElement();
    var rect = target.getBoundingClientRect();
    var targetCenter = rect.top + window.pageYOffset + (rect.height / 2);
    var viewportCenter = window.innerHeight / 2;
    var maxScrollTop = scrollElement.scrollHeight - window.innerHeight;

    return clamp(targetCenter - viewportCenter, 0, Math.max(0, maxScrollTop));
  }

  function scrollTargetToCenter(target) {
    var destination = getCenteredScrollTop(target);
    window.scrollTo(0, destination);
  }

  function decodeHash(hash) {
    if (!hash) {
      return '';
    }

    try {
      return decodeURIComponent(hash.slice(1));
    } catch (error) {
      return hash.slice(1);
    }
  }

  function getTargetFromHash(hash) {
    var id = decodeHash(hash);

    if (!id) {
      return null;
    }

    return document.getElementById(id);
  }

  function getSamePageHashTarget(href) {
    var url;

    try {
      url = new URL(href, window.location.href);
    } catch (error) {
      return null;
    }

    if (url.origin !== window.location.origin || url.pathname !== window.location.pathname || !url.hash) {
      return null;
    }

    return getTargetFromHash(url.hash);
  }

  function updateLocationHash(hash) {
    if (!hash) {
      return;
    }

    if (window.history && typeof window.history.pushState === 'function') {
      window.history.pushState(null, '', hash);
      return;
    }

    window.location.hash = hash;
  }

  function buildLabelTargets(sources) {
    var targets = {};

    sources.forEach(function (source) {
      var match;

      sourceLabelPattern.lastIndex = 0;

      while ((match = sourceLabelPattern.exec(source.content))) {
        var label = makeLabel(match[1], match[2]);
        targets[label] = source.url + '#' + makeAnchorId(match[1], match[2]);
      }
    });

    sourceLabelPattern.lastIndex = 0;

    return targets;
  }

  function readLabel(text) {
    var match = normalizeSpace(text).match(labelPattern);

    if (!match) {
      return null;
    }

    return {
      kind: match[1],
      number: match[2],
      label: makeLabel(match[1], match[2]),
      id: makeAnchorId(match[1], match[2])
    };
  }

  function addAnchorTargets(postBody) {
    var labels = postBody.querySelectorAll('strong, b');

    labels.forEach(function (element) {
      var label = readLabel(element.textContent || '');

      if (!label) {
        return;
      }

      if (!element.id) {
        element.id = label.id;
      }

      element.classList.add('math-label-anchor');
    });
  }

  function shouldSkipTextNode(node) {
    if (!node.nodeValue || !referencePattern.test(node.nodeValue)) {
      referencePattern.lastIndex = 0;
      return true;
    }

    referencePattern.lastIndex = 0;

    if (!node.parentElement) {
      return true;
    }

    return Boolean(node.parentElement.closest('a, strong, b, code, pre, script, style, textarea, noscript, mjx-container'));
  }

  function replaceReferencesInTextNode(node, targets) {
    var text = node.nodeValue;
    var fragment = document.createDocumentFragment();
    var lastIndex = 0;
    var changed = false;
    var match;

    referencePattern.lastIndex = 0;

    while ((match = referencePattern.exec(text))) {
      var label = makeLabel(match[1], match[2]);
      var href = targets[label];
      var link;
      var number;

      if (!href) {
        continue;
      }

      fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
      fragment.appendChild(document.createTextNode(match[1] + ' '));

      link = document.createElement('a');
      link.className = 'math-ref-link';
      link.href = href;
      link.setAttribute('aria-label', match[0]);

      number = document.createElement('span');
      number.className = 'math-ref-number';
      number.textContent = match[2];
      link.appendChild(number);

      fragment.appendChild(link);

      lastIndex = match.index + match[0].length;
      changed = true;
    }

    referencePattern.lastIndex = 0;

    if (!changed) {
      return;
    }

    fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
    node.parentNode.replaceChild(fragment, node);
  }

  function linkReferences(postBody, targets) {
    var walker = document.createTreeWalker(postBody, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        return shouldSkipTextNode(node) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    var node;

    while ((node = walker.nextNode())) {
      nodes.push(node);
    }

    nodes.forEach(function (textNode) {
      replaceReferencesInTextNode(textNode, targets);
    });
  }

  function bindReferenceLinkClicks(postBody) {
    postBody.addEventListener('click', function (event) {
      var link;
      var target;

      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
      }

      link = event.target.closest && event.target.closest('a.math-ref-link');

      if (!link) {
        return;
      }

      target = getSamePageHashTarget(link.href);

      if (!target) {
        return;
      }

      event.preventDefault();
      updateLocationHash(link.hash);
      scrollTargetToCenter(target);
    });
  }

  function scrollToHashTarget() {
    var target = getTargetFromHash(window.location.hash);

    if (!target) {
      return;
    }

    window.requestAnimationFrame(function () {
      scrollTargetToCenter(target);
    });
  }

  function settleHashScroll() {
    scrollToHashTarget();
    window.setTimeout(function () {
      scrollToHashTarget();
    }, 150);

    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
      window.MathJax.startup.promise.then(function () {
        scrollToHashTarget();
      });
    }

    window.addEventListener('hashchange', function () {
      scrollToHashTarget();
    });
  }

  function initMathReferenceLinks() {
    var postBody = getPostBody();
    var scope = getReferenceScope();
    var sources = labelSources[scope];

    if (!postBody || !sources) {
      return;
    }

    addAnchorTargets(postBody);
    linkReferences(postBody, buildLabelTargets(sources));
    bindReferenceLinkClicks(postBody);
    settleHashScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMathReferenceLinks, { once: true });
  } else {
    initMathReferenceLinks();
  }
}());
