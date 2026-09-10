---
---
(function () {
  'use strict';

  var labelPattern = /^(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle)\s+(\d+(?:\.\d+)+)\.?/;
  var sourceLabelPattern = /(?:\*\*|<(?:strong|b)\b[^>]*>)\s*(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle)\s+(\d+(?:\.\d+)+)\.?(?=\s|\*|\)|<\/(?:strong|b)>)/g;
  var referencePattern = /\b\d+(?:\.\d+)+\b/g;
  var entryLabelPattern = /^(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|Principle|Notation|Axiom|Exercise)\s+\d+(?:\.\d+)*\.?/;
  var proofMarkerPattern = /^(Proof|Subproof|Solution)(?:\s+\d+)?\.?$/i;
  var italicStatementKinds = {
    Theorem: true,
    Lemma: true,
    Proposition: true,
    Corollary: true
  };
  var labelSources = [
    {%- assign first_source = true -%}
    {%- for post in site.posts -%}
      {%- assign reference_scope_source = post.category_path | textbook_category -%}
      {%- assign reference_scope = reference_scope_source | strip_category_order_prefix | slugify -%}
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

  function usesLineIndent(postBody) {
    return !postBody || postBody.getAttribute('data-line-indent') !== 'false';
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

  function buildNumberTargets(sources) {
    var targets = {};

    sources.forEach(function (source) {
      var match;

      sourceLabelPattern.lastIndex = 0;

      while ((match = sourceLabelPattern.exec(source.content))) {
        var number = match[2];
        var href = source.url + '#' + makeAnchorId(match[1], number);

        if (Object.prototype.hasOwnProperty.call(targets, number)) {
          if (targets[number] !== href) {
            targets[number] = null;
          }
        } else {
          targets[number] = href;
        }
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

  function removeSpaceAfterEmSpace(postBody) {
    var walker = document.createTreeWalker(postBody, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (
          shouldSkipTypographyTextNode(node) ||
          !node.nodeValue.includes('\u2003 ')
        ) {
          return NodeFilter.FILTER_REJECT;
        }

        return NodeFilter.FILTER_ACCEPT;
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
      } else {
        if (!proofMarkerPattern.test(labelText)) {
          return;
        }

        labelElement.classList.add('math-proof-marker');
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
    removeSpaceAfterEmSpace(postBody);
    addMathLabelGaps(postBody);
  }

  function getTextBeforeNode(container, node) {
    var range = document.createRange();

    range.selectNodeContents(container);
    range.setEndBefore(node);

    return normalizeSpace(range.toString());
  }

  function isEntryLabel(element) {
    return entryLabelPattern.test(normalizeSpace(element.textContent || ''));
  }

  function directChildrenMatching(container, tagName) {
    return Array.prototype.filter.call(container.children, function (child) {
      return child.tagName === tagName;
    });
  }

  function softLineBreaks(paragraph) {
    var walker = document.createTreeWalker(paragraph, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (
          shouldSkipTypographyTextNode(node) ||
          !node.nodeValue ||
          !node.nodeValue.includes('\n')
        ) {
          return NodeFilter.FILTER_REJECT;
        }

        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var breaks = [];
    var node;

    while ((node = walker.nextNode())) {
      for (var index = 0; index < node.nodeValue.length; index += 1) {
        if (node.nodeValue[index] === '\n') {
          breaks.push({ node: node, offset: index });
        }
      }
    }

    return breaks;
  }

  function fragmentHasVisibleContent(fragment) {
    return normalizeSpace(fragment.textContent || '') !== '' || Boolean(
      fragment.querySelector(
        'br, img, svg, canvas, mjx-container, math, iframe, video, audio, input'
      )
    );
  }

  function paragraphSegment(paragraph, contents, continuation) {
    var segment = paragraph.cloneNode(false);

    if (continuation) {
      segment.removeAttribute('id');
      segment.removeAttribute('aria-labelledby');
      segment.setAttribute('data-paragraph-continuation', 'soft');
    }

    segment.classList.add('semantic-unit', 'semantic-paragraph');
    segment.appendChild(contents);
    return segment;
  }

  function splitParagraphAtSoftLines(paragraph) {
    var breaks = softLineBreaks(paragraph);
    var replacement;
    var startNode = paragraph;
    var startOffset = 0;
    var segmentCount = 0;

    if (!breaks.length) {
      paragraph.classList.add('semantic-unit', 'semantic-paragraph');
      return;
    }

    replacement = document.createDocumentFragment();

    breaks.concat([{ node: paragraph, offset: paragraph.childNodes.length }]).forEach(function (boundary) {
      var range = document.createRange();
      var contents;

      range.setStart(startNode, startOffset);
      range.setEnd(boundary.node, boundary.offset);
      contents = range.cloneContents();

      if (fragmentHasVisibleContent(contents)) {
        replacement.appendChild(paragraphSegment(paragraph, contents, segmentCount > 0));
        segmentCount += 1;
      }

      if (boundary.node !== paragraph) {
        startNode = boundary.node;
        startOffset = boundary.offset + 1;
      }
    });

    if (segmentCount) {
      paragraph.parentNode.replaceChild(replacement, paragraph);
    }
  }

  function prepareParagraphUnits(postBody) {
    var paragraphs = directChildrenMatching(postBody, 'P');

    if (usesLineIndent(postBody)) {
      paragraphs.forEach(splitParagraphAtSoftLines);
    } else {
      paragraphs.forEach(function (paragraph) {
        paragraph.classList.add('semantic-unit', 'semantic-paragraph');
      });
    }
  }

  function readEntryDescriptor(paragraph) {
    var candidates;
    var descriptor = null;

    if (!paragraph || paragraph.tagName !== 'P') {
      return null;
    }

    candidates = paragraph.querySelectorAll('strong, b, em, i');

    candidates.forEach(function (candidate) {
      var text;
      var entryMatch;
      var proofMatch;

      if (descriptor || getTextBeforeNode(paragraph, candidate) !== '') {
        return;
      }

      text = normalizeSpace(candidate.textContent || '');
      entryMatch = text.match(entryLabelPattern);

      if (entryMatch) {
        descriptor = {
          kind: entryMatch[1],
          labelElement: candidate
        };
        return;
      }

      proofMatch = text.match(proofMarkerPattern);

      if (proofMatch) {
        descriptor = {
          kind: proofMatch[1].charAt(0).toUpperCase() + proofMatch[1].slice(1).toLowerCase(),
          labelElement: candidate
        };
      }
    });

    return descriptor;
  }

  function isSemanticBoundary(element) {
    return element.classList.contains('post-explicit-entry-break') ||
      isDocumentBoundary(element);
  }

  function isDocumentBoundary(element) {
    return /^H[1-6]$/.test(element.tagName) || element.tagName === 'HR';
  }

  function isMarkerTerminatedEnvironment(kind) {
    return kind === 'Proof' || kind === 'Subproof';
  }

  function elementEndsEnvironment(element, kind) {
    var expected = kind.toLowerCase();
    var marker = element.matches('[data-environment-end]') ?
      element :
      element.querySelector('[data-environment-end]');

    return Boolean(marker && marker.getAttribute('data-environment-end') === expected);
  }

  function isCompetingProofStart(descriptor, kind) {
    if (!descriptor) {
      return false;
    }

    if (kind === 'Proof') {
      return descriptor.kind === 'Proof';
    }

    return descriptor.kind === 'Proof' || descriptor.kind === 'Subproof';
  }

  function hasMatchingEnvironmentEnd(start, kind) {
    var member = start;

    while (member) {
      var descriptor = member === start ? null : readEntryDescriptor(member);

      if (isCompetingProofStart(descriptor, kind)) {
        return false;
      }

      if (elementEndsEnvironment(member, kind)) {
        return true;
      }

      member = member.nextElementSibling;
    }

    return false;
  }

  function isStructuralContinuationMarker(element) {
    return element.classList.contains('post-structural-continuation');
  }

  function environmentKindClass(kind) {
    return kind.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }

  function ensureEntryLabelId(labelElement, kind, number) {
    var id = labelElement.id;

    if (id) {
      return id;
    }

    id = 'math-' + environmentKindClass(kind) + '-' + number;
    labelElement.id = id;
    return id;
  }

  function decorateEnvironmentParagraphs(environment) {
    directChildrenMatching(environment, 'P').forEach(function (paragraph) {
      paragraph.classList.remove('semantic-unit', 'semantic-paragraph');
      paragraph.classList.add('math-environment__paragraph');
    });
  }

  function groupMathEnvironments(container, state, skipOpeningParagraph) {
    var current = container.firstElementChild;

    if (skipOpeningParagraph && current) {
      current = current.nextElementSibling;
    }

    while (current) {
      var descriptor = readEntryDescriptor(current);
      var markerTerminated;

      if (!descriptor) {
        current = current.nextElementSibling;
        continue;
      }

      markerTerminated = isMarkerTerminatedEnvironment(descriptor.kind);

      if (markerTerminated && !hasMatchingEnvironmentEnd(current, descriptor.kind)) {
        current = current.nextElementSibling;
        continue;
      }

      state.environmentNumber += 1;

      var environment = document.createElement('section');
      var kindClass = environmentKindClass(descriptor.kind);
      var member = current;
      var structuralBridge = false;
      var structuralContinuation = false;

      environment.className = 'semantic-unit math-environment math-environment--' + kindClass;
      environment.setAttribute('data-environment-kind', descriptor.kind);
      environment.setAttribute(
        'aria-labelledby',
        ensureEntryLabelId(descriptor.labelElement, descriptor.kind, state.environmentNumber)
      );

      if (italicStatementKinds[descriptor.kind]) {
        environment.classList.add('math-statement-italic');
      }

      container.insertBefore(environment, member);

      while (member) {
        var nextMember = member.nextElementSibling;

        if (member !== current) {
          var memberDescriptor;

          if (isStructuralContinuationMarker(member)) {
            structuralContinuation = structuralBridge;
            environment.appendChild(member);
            member = nextMember;
            continue;
          }

          memberDescriptor = readEntryDescriptor(member);

          if (
            !markerTerminated &&
            (isSemanticBoundary(member) || memberDescriptor)
          ) {
            break;
          }

          if (member.tagName === 'P') {
            if (
              !markerTerminated &&
              member.getAttribute('data-paragraph-continuation') !== 'soft' &&
              !structuralBridge
            ) {
              break;
            }

            if (structuralContinuation && !memberDescriptor) {
              member.setAttribute('data-paragraph-continuation', 'structural');
            }

            structuralBridge = false;
            structuralContinuation = false;
          } else {
            structuralBridge = true;
            structuralContinuation = false;
          }
        }

        environment.appendChild(member);
        member = nextMember;

        if (markerTerminated && elementEndsEnvironment(environment.lastElementChild, descriptor.kind)) {
          break;
        }
      }

      decorateEnvironmentParagraphs(environment);

      if (descriptor.kind === 'Proof') {
        groupMathEnvironments(environment, state, true);
      }

      current = member;
    }
  }

  function markSectionOpeningParagraphs(postBody) {
    var needsOpeningParagraph = true;

    Array.prototype.forEach.call(postBody.children, function (element) {
      if (/^H[1-6]$/.test(element.tagName)) {
        needsOpeningParagraph = true;
        return;
      }

      if (
        element.classList.contains('post-explicit-entry-break') ||
        element.classList.contains('post-structural-continuation')
      ) {
        return;
      }

      if (element.matches('p.semantic-paragraph')) {
        if (needsOpeningParagraph) {
          element.classList.add('semantic-paragraph--section-opening');
        }

        needsOpeningParagraph = false;
        return;
      }

      needsOpeningParagraph = false;
    });
  }

  function buildSemanticPostUnits(postBody) {
    if (postBody.getAttribute('data-semantic-units') === 'true') {
      return;
    }

    prepareParagraphUnits(postBody);
    groupMathEnvironments(postBody, { environmentNumber: 0 }, false);
    markSectionOpeningParagraphs(postBody);
    postBody.setAttribute('data-semantic-units', 'true');
  }

  function initSemanticPostUnits() {
    var postBody = getPostBody();
    var applyUnits;

    if (!postBody) {
      return;
    }

    applyUnits = function () {
      buildSemanticPostUnits(postBody);
      initScrollablePostTables();
    };

    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
      window.MathJax.startup.promise.then(applyUnits, applyUnits);
      return;
    }

    applyUnits();
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
      var numberText = match[0];
      var href = targets[numberText];
      var link;
      var number;

      if (!href) {
        continue;
      }

      fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));

      link = document.createElement('a');
      link.className = 'math-ref-link';
      link.href = href;
      link.setAttribute('aria-label', 'Reference ' + numberText);

      number = document.createElement('span');
      number.className = 'math-ref-number';
      number.textContent = numberText;
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

    linkReferences(postBody, buildNumberTargets(sources));
    bindReferenceLinkClicks(postBody);
    settleHashScroll();
  }

  function applyPostTableNoWrapColumns(table) {
    var attribute = table.getAttribute('nowrap-columns') ||
      table.getAttribute('data-nowrap-columns') ||
      '';
    var noWrapColumns = {};

    attribute.split(/[\s,]+/).forEach(function (value) {
      var columnNumber;

      if (!/^\d+$/.test(value)) {
        return;
      }

      columnNumber = parseInt(value, 10);

      if (columnNumber > 0) {
        noWrapColumns[columnNumber - 1] = true;
      }
    });

    Array.prototype.forEach.call(table.rows, function (row) {
      var columnIndex = 0;

      Array.prototype.forEach.call(row.cells, function (cell) {
        var span = Math.max(1, cell.colSpan || 1);
        var index;

        for (index = columnIndex; index < columnIndex + span; index += 1) {
          if (noWrapColumns[index]) {
            cell.classList.add('post-table-cell-nowrap');
            break;
          }
        }

        columnIndex += span;
      });
    });
  }

  function initScrollablePostTables() {
    var postBody = getPostBody();

    if (!postBody) {
      return;
    }

    postBody.querySelectorAll('table').forEach(function (table) {
      var scrollArea;

      if (table.closest('.highlight')) {
        return;
      }

      applyPostTableNoWrapColumns(table);

      if (table.closest('.post-table-scroll')) {
        return;
      }

      scrollArea = document.createElement('div');
      scrollArea.className = 'post-table-scroll';
      scrollArea.setAttribute('role', 'region');
      scrollArea.setAttribute('aria-label', 'Scrollable table');
      scrollArea.setAttribute('tabindex', '0');

      table.parentNode.insertBefore(scrollArea, table);
      scrollArea.appendChild(table);
    });
  }

  function initPageEnhancements() {
    initMathReferenceLinks();
    initPostTypographySpacing();
    initSemanticPostUnits();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPageEnhancements, { once: true });
  } else {
    initPageEnhancements();
  }
}());
