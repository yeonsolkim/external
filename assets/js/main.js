---
---
(function () {
  'use strict';

  var labelPattern = /^(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle)\s+(\d+(?:\.\d+)+)\.?/;
  var sourceLabelPattern = /(?:\*\*|<(?:strong|b)\b[^>]*>)\s*(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle)\s+(\d+(?:\.\d+)+)\.?(?=\s|\*|\)|<\/(?:strong|b)>)/g;
  var referencePattern = /\b(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle)\s+(\d+(?:\.\d+)+)\b/g;
  var entryLabelPattern = /^(?:Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle|Notation|Axiom|Exercise)\s+\d+(?:\.\d+)*\.?/;
  var statementBoundaryLabelPattern = /^(?:Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle|Notation|Axiom|Exercise)\b/;
  var proofMarkerPattern = /^(?:Proof|Subproof|Solution)(?:\s+\d+)?\.?$/i;
  var italicStatementKinds = {
    Theorem: true,
    Lemma: true,
    Proposition: true,
    Corollary: true
  };
  var labelSources = [
    {%- assign first_source = true -%}
    {%- for post in site.posts -%}
      {%- assign reference_scope_source = post.category_path[1] | default: "" -%}
      {%- assign reference_scope = reference_scope_source | slugify -%}
      {%- if reference_scope != "" -%}
        {%- unless first_source -%},{%- endunless -%}
        {
          scope: {{ reference_scope | jsonify }},
          url: {{ post.url | relative_url | jsonify }},
          content: {{ post.content | jsonify }}
        }
        {%- assign first_source = false -%}
      {%- endif -%}
    {%- endfor -%}
  ];

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

  function wrapStatementNameTextNode(node) {
    var match = (node.nodeValue || '').match(/^(\s*)(\([^)\n]+\)\.?)/);
    var wrapper;

    if (!match) {
      return false;
    }

    wrapper = document.createElement('span');
    wrapper.className = 'math-statement-name';
    wrapper.textContent = match[2];

    if (match[1]) {
      node.parentNode.insertBefore(document.createTextNode(match[1]), node);
    }

    node.parentNode.insertBefore(wrapper, node);
    node.nodeValue = node.nodeValue.slice(match[0].length);
    return true;
  }

  function markStatementName(labelElement) {
    var node = labelElement.nextSibling;
    var text;

    while (node && node.nodeType === Node.TEXT_NODE && normalizeSpace(node.nodeValue || '') === '') {
      node = node.nextSibling;
    }

    if (!node) {
      return;
    }

    if (node.nodeType === Node.TEXT_NODE) {
      wrapStatementNameTextNode(node);
      return;
    }

    if (node.nodeType !== Node.ELEMENT_NODE || !/^(EM|I)$/.test(node.tagName)) {
      return;
    }

    text = normalizeSpace(node.textContent || '');

    if (/^\([^)\n]+\)\.?$/.test(text)) {
      node.classList.add('math-statement-name');
    }
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
      markStatementName(element);
    });
  }

  function shouldSkipTypographyTextNode(node) {
    if (!node.parentElement) {
      return true;
    }

    return Boolean(node.parentElement.closest(
      'code, pre, script, style, textarea, noscript, mjx-container'
    ));
  }

  function removeSpacesAfterEmSpaces(postBody) {
    var walker = document.createTreeWalker(postBody, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        return shouldSkipTypographyTextNode(node)
          ? NodeFilter.FILTER_REJECT
          : NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    var node;

    while ((node = walker.nextNode())) {
      nodes.push(node);
    }

    nodes.forEach(function (textNode) {
      textNode.nodeValue = textNode.nodeValue.replace(/\u2003 /g, '\u2003');
    });
  }

  function getNextVisibleSibling(node) {
    var sibling = node.nextSibling;

    while (sibling) {
      if (sibling.nodeType === Node.COMMENT_NODE) {
        sibling = sibling.nextSibling;
        continue;
      }

      if (
        sibling.nodeType === Node.TEXT_NODE &&
        normalizeSpace(sibling.nodeValue || '') === ''
      ) {
        sibling = sibling.nextSibling;
        continue;
      }

      return sibling;
    }

    return null;
  }

  function getStatementLabelEnd(labelElement) {
    var statementName = getNextVisibleSibling(labelElement);

    if (
      statementName &&
      statementName.nodeType === Node.ELEMENT_NODE &&
      statementName.classList.contains('math-statement-name')
    ) {
      return statementName;
    }

    return labelElement;
  }

  function getLabelGapReference(labelEnd) {
    var node = labelEnd.nextSibling;
    var labelText = normalizeSpace(labelEnd.textContent || '');
    var labelHasTerminalPunctuation = /[.!?:;]$/.test(labelText);

    while (node) {
      if (node.nodeType === Node.COMMENT_NODE) {
        node = node.nextSibling;
        continue;
      }

      if (node.nodeType === Node.TEXT_NODE) {
        node.nodeValue = (node.nodeValue || '').replace(/^[\t\n\f\r ]+/, '');

        if (!node.nodeValue) {
          node = node.nextSibling;
          continue;
        }

        if (!labelHasTerminalPunctuation && /^[.!?:;]/.test(node.nodeValue)) {
          node = node.splitText(1);
          labelHasTerminalPunctuation = true;
          continue;
        }

        return node;
      }

      if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'BR') {
        return null;
      }

      return node;
    }

    return null;
  }

  function addFixedLabelGap(labelEnd) {
    var reference = getLabelGapReference(labelEnd);
    var gap;

    if (!reference || reference.parentNode !== labelEnd.parentNode) {
      return;
    }

    gap = document.createElement('span');
    gap.className = 'math-label-gap';
    gap.setAttribute('aria-hidden', 'true');
    labelEnd.parentNode.insertBefore(gap, reference);
  }

  function addMathLabelGaps(postBody) {
    var labels = postBody.querySelectorAll('strong, b, em, i');

    labels.forEach(function (labelElement) {
      var labelText = normalizeSpace(labelElement.textContent || '');
      var labelEnd = labelElement;

      if (isEntryLabel(labelElement)) {
        markStatementName(labelElement);
        labelEnd = getStatementLabelEnd(labelElement);
      } else if (!proofMarkerPattern.test(labelText)) {
        return;
      }

      addFixedLabelGap(labelEnd);
    });
  }

  function initPostTypographySpacing() {
    var postBody = getPostBody();

    if (!postBody || postBody.getAttribute('data-typography-spacing') === 'true') {
      return;
    }

    postBody.setAttribute('data-typography-spacing', 'true');
    removeSpacesAfterEmSpaces(postBody);
    addMathLabelGaps(postBody);
  }

  function getTopLevelBlock(postBody, element) {
    var block = element;

    while (block && block.parentElement !== postBody) {
      block = block.parentElement;
    }

    return block && block.parentElement === postBody ? block : null;
  }

  function getDirectChild(container, descendant) {
    var child = descendant;

    while (child && child.parentNode !== container) {
      child = child.parentNode;
    }

    return child && child.parentNode === container ? child : null;
  }

  function getTextBeforeNode(container, node) {
    var range = document.createRange();

    range.selectNodeContents(container);
    range.setEndBefore(node);

    return normalizeSpace(range.toString());
  }

  function findProofMarker(element) {
    var candidates = element.querySelectorAll('em, i');
    var marker = null;

    candidates.forEach(function (candidate) {
      if (!marker && proofMarkerPattern.test(normalizeSpace(candidate.textContent || ''))) {
        marker = candidate;
      }
    });

    return marker;
  }

  function isEntryLabel(element) {
    return entryLabelPattern.test(normalizeSpace(element.textContent || ''));
  }

  function isSeparatorNode(node) {
    return node.nodeType === Node.TEXT_NODE
      ? normalizeSpace(node.nodeValue || '') === ''
      : node.nodeType === Node.ELEMENT_NODE && node.tagName === 'BR';
  }

  function removeSeparatorsBeforeNode(node) {
    var sibling = node.previousSibling;
    var previous;

    while (sibling && isSeparatorNode(sibling)) {
      previous = sibling.previousSibling;
      sibling.parentNode.removeChild(sibling);
      sibling = previous;
    }
  }

  function removeTrailingSeparators(element) {
    var node = element.lastChild;
    var previous;

    while (node && isSeparatorNode(node)) {
      previous = node.previousSibling;
      element.removeChild(node);
      node = previous;
    }
  }

  function isSeparatorBlock(element) {
    var child = element.firstChild;

    if (normalizeSpace(element.textContent || '') !== '') {
      return false;
    }

    while (child) {
      if (!isSeparatorNode(child)) {
        return false;
      }

      child = child.nextSibling;
    }

    return true;
  }

  function trimBoundaryBefore(block) {
    var previous = block.previousElementSibling;

    while (previous && isSeparatorBlock(previous)) {
      previous.classList.add('math-boundary-spacer');
      previous = previous.previousElementSibling;
    }

    if (previous) {
      removeTrailingSeparators(previous);
    }

    return previous;
  }

  function getEntryStarts(postBody) {
    var starts = [];

    postBody.querySelectorAll('strong, b').forEach(function (labelElement) {
      var block;
      var labelChild;

      if (!isEntryLabel(labelElement)) {
        return;
      }

      block = getTopLevelBlock(postBody, labelElement);

      if (!block || getTextBeforeNode(block, labelElement) !== '') {
        return;
      }

      labelChild = getDirectChild(block, labelElement);

      if (!labelChild) {
        return;
      }

      removeSeparatorsBeforeNode(labelChild);
      labelElement.classList.add('math-entry-label');
      block.classList.add('math-entry-start');

      if (!starts.length || starts[starts.length - 1].block !== block) {
        starts.push({
          block: block,
          label: labelElement
        });
      }
    });

    return starts;
  }

  function getEntryBlocks(startBlock, nextStartBlock) {
    var blocks = [];
    var block = startBlock;

    while (block && block !== nextStartBlock) {
      if (block !== startBlock && (/^H[1-6]$/.test(block.tagName) || block.tagName === 'HR')) {
        break;
      }

      blocks.push(block);
      block = block.nextElementSibling;
    }

    return blocks;
  }

  function getLastContentBlock(blocks) {
    var index;

    for (index = blocks.length - 1; index >= 0; index -= 1) {
      if (!isSeparatorBlock(blocks[index])) {
        return blocks[index];
      }
    }

    return null;
  }

  function markProofSpacing(postBody, blocks) {
    var proofMarker = null;
    var proofBlock;
    var proofChild;
    var previousBlock;
    var gap;
    var breakIndex;

    blocks.some(function (block) {
      proofMarker = findProofMarker(block);
      return Boolean(proofMarker);
    });

    if (!proofMarker) {
      return;
    }

    proofBlock = getTopLevelBlock(postBody, proofMarker);
    proofChild = getDirectChild(proofBlock, proofMarker);

    if (!proofBlock || !proofChild) {
      return;
    }

    proofMarker.classList.add('math-proof-marker');

    if (getTextBeforeNode(proofBlock, proofMarker) !== '') {
      removeSeparatorsBeforeNode(proofChild);
      gap = document.createElement('span');
      gap.className = 'math-proof-gap';
      gap.setAttribute('aria-hidden', 'true');

      for (breakIndex = 0; breakIndex < 2; breakIndex += 1) {
        gap.appendChild(document.createElement('br'));
      }

      proofBlock.insertBefore(gap, proofChild);
      return;
    }

    removeSeparatorsBeforeNode(proofChild);
    previousBlock = trimBoundaryBefore(proofBlock);
    proofBlock.classList.add('math-proof-start');

    if (previousBlock) {
      previousBlock.classList.add('math-before-proof');
    }
  }

  function markMathEntrySpacing(postBody) {
    var starts;

    if (postBody.getAttribute('data-math-entry-spacing') === 'true') {
      return;
    }

    postBody.setAttribute('data-math-entry-spacing', 'true');
    starts = getEntryStarts(postBody);

    starts.forEach(function (entry, index) {
      var nextEntry = starts[index + 1];
      var blocks = getEntryBlocks(entry.block, nextEntry && nextEntry.block);
      var lastBlock = getLastContentBlock(blocks);
      var previousBlock;

      markProofSpacing(postBody, blocks);

      if (lastBlock) {
        removeTrailingSeparators(lastBlock);
        lastBlock.classList.add('math-entry-end');
      }

      if (!nextEntry || blocks[blocks.length - 1].nextElementSibling !== nextEntry.block) {
        return;
      }

      previousBlock = trimBoundaryBefore(nextEntry.block);
      nextEntry.block.classList.add('math-entry-after-entry');

      if (previousBlock) {
        previousBlock.classList.add('math-entry-end');
      }
    });
  }

  function initMathEntrySpacing() {
    var postBody = getPostBody();
    var applySpacing;
    var updateSectionGap;

    if (!postBody) {
      return;
    }

    updateSectionGap = function () {
      var lineHeight = parseFloat(window.getComputedStyle(postBody).lineHeight);

      if (Number.isFinite(lineHeight)) {
        postBody.style.setProperty('--math-section-gap', (lineHeight * 3) + 'px');
      }
    };

    applySpacing = function () {
      markMathEntrySpacing(postBody);
      updateSectionGap();
    };

    updateSectionGap();
    window.addEventListener('resize', updateSectionGap);

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(updateSectionGap);
    }

    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
      window.MathJax.startup.promise.then(applySpacing, applySpacing);
      return;
    }

    applySpacing();
  }

  function isStatementBoundary(element) {
    var tagName = element.tagName;
    var candidates;
    var found = false;

    if (/^H[1-6]$/.test(tagName) || tagName === 'HR') {
      return true;
    }

    candidates = element.querySelectorAll('strong, b');
    candidates.forEach(function (candidate) {
      var labelText = normalizeSpace(candidate.textContent || '');

      if (
        !found &&
        statementBoundaryLabelPattern.test(labelText) &&
        getTextBeforeNode(element, candidate) === ''
      ) {
        found = true;
      }
    });

    return found;
  }

  function wrapSiblingRange(parent, firstNode, stopNode) {
    var nodes = [];
    var node = firstNode;
    var wrapper;

    while (node && node !== stopNode) {
      nodes.push(node);
      node = node.nextSibling;
    }

    if (!nodes.length) {
      return;
    }

    wrapper = document.createElement('span');
    wrapper.className = 'math-statement-italic';
    parent.insertBefore(wrapper, nodes[0]);

    nodes.forEach(function (rangeNode) {
      wrapper.appendChild(rangeNode);
    });
  }

  function italicizeStartingBlock(block, labelElement) {
    var proofMarker = findProofMarker(block);
    var labelChild;
    var proofChild;

    if (!proofMarker) {
      block.classList.add('math-statement-italic');
      return false;
    }

    labelChild = getDirectChild(block, labelElement);
    proofChild = getDirectChild(block, proofMarker);

    if (labelChild && proofChild) {
      wrapSiblingRange(block, labelChild.nextSibling, proofChild);
    }

    return true;
  }

  function italicizeContinuationBlock(block) {
    var proofMarker = findProofMarker(block);
    var proofChild;

    if (!proofMarker) {
      block.classList.add('math-statement-italic');
      return false;
    }

    proofChild = getDirectChild(block, proofMarker);

    if (proofChild && getTextBeforeNode(block, proofMarker) !== '') {
      wrapSiblingRange(block, block.firstChild, proofChild);
    }

    return true;
  }

  function italicizeMathStatements(postBody) {
    var labels;

    if (postBody.getAttribute('data-math-statements-italicized') === 'true') {
      return;
    }

    postBody.setAttribute('data-math-statements-italicized', 'true');
    labels = postBody.querySelectorAll('.math-label-anchor');

    labels.forEach(function (labelElement) {
      var label = readLabel(labelElement.textContent || '');
      var block;
      var nextBlock;
      var reachedProof;

      if (!label || !italicStatementKinds[label.kind]) {
        return;
      }

      block = getTopLevelBlock(postBody, labelElement);

      if (!block) {
        return;
      }

      reachedProof = italicizeStartingBlock(block, labelElement);
      nextBlock = block.nextElementSibling;

      while (!reachedProof && nextBlock && !isStatementBoundary(nextBlock)) {
        reachedProof = italicizeContinuationBlock(nextBlock);
        nextBlock = nextBlock.nextElementSibling;
      }
    });
  }

  function initMathStatementItalics() {
    var postBody = getPostBody();
    var applyItalics;

    if (!postBody) {
      return;
    }

    applyItalics = function () {
      italicizeMathStatements(postBody);
    };

    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
      window.MathJax.startup.promise.then(applyItalics, applyItalics);
      return;
    }

    applyItalics();
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
    var sources = labelSources.filter(function (source) {
      return source.scope === scope;
    });

    if (!postBody) {
      return;
    }

    addAnchorTargets(postBody);

    if (!scope || !sources.length) {
      return;
    }

    linkReferences(postBody, buildLabelTargets(sources));
    bindReferenceLinkClicks(postBody);
    settleHashScroll();
  }

  var tableBalanceFrame = 0;
  var tableBalanceEventsBound = false;

  function readPixelValue(value) {
    var number = parseFloat(value);
    return Number.isFinite(number) ? number : 0;
  }

  function getTableColumnCount(table) {
    var rows = table.rows;
    var maxColumns = 0;

    Array.prototype.forEach.call(rows, function (row) {
      var count = 0;

      Array.prototype.forEach.call(row.cells, function (cell) {
        count += Math.max(1, cell.colSpan || 1);
      });

      maxColumns = Math.max(maxColumns, count);
    });

    return maxColumns;
  }

  function measureCellWidth(cell, measurer) {
    var style = window.getComputedStyle(cell);
    var clone = document.createElement('div');
    var width;

    clone.innerHTML = cell.innerHTML;
    clone.style.boxSizing = 'border-box';
    clone.style.display = 'inline-block';
    clone.style.font = style.font;
    clone.style.fontFamily = style.fontFamily;
    clone.style.fontSize = style.fontSize;
    clone.style.fontStyle = style.fontStyle;
    clone.style.fontWeight = style.fontWeight;
    clone.style.letterSpacing = style.letterSpacing;
    clone.style.lineHeight = style.lineHeight;
    clone.style.paddingLeft = style.paddingLeft;
    clone.style.paddingRight = style.paddingRight;
    clone.style.textTransform = style.textTransform;
    clone.style.whiteSpace = 'nowrap';

    measurer.appendChild(clone);
    width = clone.getBoundingClientRect().width;
    measurer.removeChild(clone);

    return width;
  }

  function collectColumnMetrics(table, columnCount) {
    var preferredWidths = Array(columnCount).fill(0);
    var floorWidths = Array(columnCount).fill(0);
    var measurer = document.createElement('div');

    measurer.setAttribute('aria-hidden', 'true');
    measurer.style.position = 'absolute';
    measurer.style.left = '-10000px';
    measurer.style.top = '0';
    measurer.style.visibility = 'hidden';
    measurer.style.pointerEvents = 'none';
    measurer.style.whiteSpace = 'nowrap';
    document.body.appendChild(measurer);

    Array.prototype.forEach.call(table.rows, function (row) {
      var columnIndex = 0;

      Array.prototype.forEach.call(row.cells, function (cell) {
        var style = window.getComputedStyle(cell);
        var span = Math.max(1, Math.min(cell.colSpan || 1, columnCount - columnIndex));
        var horizontalPadding = readPixelValue(style.paddingLeft) + readPixelValue(style.paddingRight);
        var measuredWidth = measureCellWidth(cell, measurer) / span;
        var floorWidth = (horizontalPadding / span) + 24;
        var index;

        for (index = columnIndex; index < columnIndex + span && index < columnCount; index += 1) {
          preferredWidths[index] = Math.max(preferredWidths[index], measuredWidth);
          floorWidths[index] = Math.max(floorWidths[index], floorWidth);
        }

        columnIndex += span;
      });
    });

    document.body.removeChild(measurer);

    return {
      preferredWidths: preferredWidths,
      floorWidths: floorWidths
    };
  }

  function calculateColumnWidths(totalWidth, preferredWidths, floorWidths) {
    var columnCount = preferredWidths.length;
    var equalWidth = totalWidth / columnCount;
    var widths = Array(columnCount).fill(equalWidth);
    var needs = Array(columnCount).fill(0);
    var available = Array(columnCount).fill(0);
    var totalNeed = 0;
    var totalAvailable = 0;
    var grantedWidth;
    var index;

    for (index = 0; index < columnCount; index += 1) {
      if (preferredWidths[index] > equalWidth) {
        needs[index] = preferredWidths[index] - equalWidth;
        totalNeed += needs[index];
      } else {
        available[index] = Math.max(0, equalWidth - floorWidths[index]);
        totalAvailable += available[index];
      }
    }

    if (totalNeed === 0 || totalAvailable === 0) {
      return widths;
    }

    grantedWidth = Math.min(totalNeed, totalAvailable);

    for (index = 0; index < columnCount; index += 1) {
      if (needs[index] > 0) {
        widths[index] += grantedWidth * (needs[index] / totalNeed);
      } else if (available[index] > 0) {
        widths[index] -= grantedWidth * (available[index] / totalAvailable);
      }
    }

    return widths;
  }

  function applyColumnWidths(table, widths, totalWidth) {
    var oldColGroup = table.querySelector('colgroup[data-balanced-columns]');
    var colGroup = document.createElement('colgroup');

    if (oldColGroup) {
      oldColGroup.remove();
    }

    colGroup.setAttribute('data-balanced-columns', 'true');

    widths.forEach(function (width) {
      var col = document.createElement('col');
      col.style.width = ((width / totalWidth) * 100).toFixed(4) + '%';
      colGroup.appendChild(col);
    });

    table.insertBefore(colGroup, table.firstChild);
    table.setAttribute('data-balanced-columns', 'true');
    table.style.setProperty('table-layout', 'fixed', 'important');
  }

  function balancePostTable(table) {
    var columnCount;
    var tableWidth;
    var metrics;
    var widths;

    if (table.closest('.highlight')) {
      return;
    }

    columnCount = getTableColumnCount(table);
    tableWidth = table.getBoundingClientRect().width;

    if (columnCount < 2 || tableWidth <= 0) {
      return;
    }

    metrics = collectColumnMetrics(table, columnCount);
    widths = calculateColumnWidths(tableWidth, metrics.preferredWidths, metrics.floorWidths);
    applyColumnWidths(table, widths, tableWidth);
  }

  function balancePostTables() {
    var postBody = getPostBody();

    if (!postBody) {
      return;
    }

    postBody.querySelectorAll('table').forEach(balancePostTable);
  }

  function schedulePostTableBalance() {
    if (tableBalanceFrame) {
      window.cancelAnimationFrame(tableBalanceFrame);
    }

    tableBalanceFrame = window.requestAnimationFrame(function () {
      tableBalanceFrame = 0;
      balancePostTables();
    });
  }

  function initPostTableBalance() {
    schedulePostTableBalance();

    if (!tableBalanceEventsBound) {
      tableBalanceEventsBound = true;
      window.addEventListener('resize', schedulePostTableBalance);
    }

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(schedulePostTableBalance);
    }

    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
      window.MathJax.startup.promise.then(schedulePostTableBalance);
    }
  }

  function initPageEnhancements() {
    initMathReferenceLinks();
    initPostTypographySpacing();
    initMathEntrySpacing();
    initMathStatementItalics();
    initPostTableBalance();
  }

  window.balancePostTables = balancePostTables;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPageEnhancements, { once: true });
  } else {
    initPageEnhancements();
  }
}());
