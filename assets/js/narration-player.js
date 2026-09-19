/*
 * Narration without a player. Reads /audio/<page>.json (written by the narrator after the
 * site is built) and, only when it exists:
 *   – a click or tap on a statement's label ("Theorem 3.1.1.") plays that statement;
 *   – a click on the post title plays the whole post from the start;
 *   – while playing, one click or tap anywhere stops.
 * While playing, everything except the section being read fades to grey, the page follows
 * the reading, a hairline at the top shows progress, and the lock screen gets controls.
 */
(function () {
  'use strict';

  var host = document.querySelector('.narration[data-manifest]');
  if (!host || !window.fetch) return;

  fetch(host.getAttribute('data-manifest'), { cache: 'no-cache' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (m) { if (m && m.audio) mount(m); })
    .catch(function () {});

  function norm(s) { return (s || '').replace(/\s+/g, ' ').trim(); }

  /* The block (direct child of .post-body) where each section starts. */
  function locateStarts(sections, blocks) {
    var starts = {};
    var body = document.querySelector('.post-body');
    function block(el) { return el && (el.closest('.post-body > *') || null); }
    sections.forEach(function (s) {
      var el = document.getElementById(s.id);          /* main.js anchors every labelled statement */
      if (!el && s.kind === 'introduction') {
        el = blocks.filter(function (b) { return b.tagName === 'P'; })[0];
      } else if (!el && s.kind === 'prose') {
        var head = norm(s.title.split('…')[0]).slice(0, 40).toLowerCase();
        if (head.length >= 12) {
          el = blocks.filter(function (b) {
            return b.tagName === 'P' && norm(b.textContent).slice(0, 40).toLowerCase().indexOf(head) === 0;
          })[0];
        }
      } else if (!el) {
        /* A labelled paragraph main.js gave no id (e.g. "1. Trials and outcomes."): find it by
           its lead <strong>, anywhere under a block, and make the label the anchor. */
        var label = norm(s.title.split(' (')[0]).toLowerCase();
        var leads = body ? body.querySelectorAll('p > strong:first-child, p > b:first-child') : [];
        el = Array.prototype.filter.call(leads, function (lead) {
          return norm(lead.textContent).replace(/\.$/, '').toLowerCase() === label;
        })[0] || null;
        if (el && !el.id) el.id = s.id;
      }
      var b = block(el);
      if (b) {
        var i = blocks.indexOf(b);
        if (i >= 0) starts[s.id] = i;
      }
    });
    return starts;
  }

  function mount(m) {
    var sections = m.sections || [];
    var body = document.querySelector('.post-body');
    var title = document.querySelector('.post-title');
    var blocks = [], starts = {}, blockSection = [], layoutCount = -1;

    /* The page's own scripts wrap statements into <section>s after MathJax has run, so the
       block map is rebuilt whenever .post-body's children change. */
    function layout() {
      if (!body || body.childElementCount === layoutCount) return false;
      layoutCount = body.childElementCount;
      blocks.forEach(function (b) { b.classList.remove('nrp-dim'); });
      blocks = Array.prototype.filter.call(body.children, function (el) { return !/^(SCRIPT|STYLE)$/.test(el.tagName); });
      starts = locateStarts(sections, blocks);
      blockSection = blocks.map(function () { return -1; });
      var order = sections.map(function (s, i) { return { i: i, at: starts[s.id] }; })
        .filter(function (x) { return x.at !== undefined; }).sort(function (a, b) { return a.at - b.at; });
      order.forEach(function (x, k) {
        var end = k + 1 < order.length ? order[k + 1].at : blocks.length;
        for (var b = x.at; b < end; b++) blockSection[b] = x.i;
      });
      markLabels();
      return true;
    }

    /* Labels that have audio get the pointer cursor; the title too. */
    function markLabels() {
      sections.forEach(function (s) {
        var el = document.getElementById(s.id);
        if (el) el.setAttribute('data-nrp', s.id);
      });
      if (title) title.setAttribute('data-nrp', 'all');
    }

    layout();
    if (body && window.MutationObserver) {
      new MutationObserver(function () { if (layout()) applyDim(); }).observe(body, { childList: true });
    }

    var audio = document.createElement('audio');
    audio.preload = 'metadata';
    audio.src = m.audio;
    audio.setAttribute('aria-hidden', 'true');
    document.body.appendChild(audio);

    var bar = document.createElement('div');
    bar.className = 'nrp-progress';
    document.body.appendChild(bar);

    var range = null;            /* {start, end} of what is being played */
    var current = -1;
    var userScrolledAt = 0;

    function sectionAt(t) {
      var found = -1;
      for (var i = 0; i < sections.length; i++) { if (sections[i].start <= t + 0.05) found = i; else break; }
      return found;
    }

    function applyDim() {
      blocks.forEach(function (b, k) { b.classList.toggle('nrp-dim', blockSection[k] !== current); });
    }

    function focusSection(i) {
      if (i === current) return;
      current = i;
      layout();
      applyDim();
      if (i >= 0 && !audio.paused && Date.now() - userScrolledAt > 8000 && starts[sections[i].id] !== undefined) {
        var el = blocks[starts[sections[i].id]];
        var r = el.getBoundingClientRect();
        if (r.top < 0 || r.bottom > window.innerHeight * 0.8) {
          var top = window.scrollY + r.top - Math.round(window.innerHeight * 0.15);
          window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
        }
      }
    }

    function setReading(on) {
      document.documentElement.classList.toggle('nrp-reading', on);
      if (!on) { current = -1; blocks.forEach(function (b) { b.classList.remove('nrp-dim'); }); bar.style.width = '0'; }
      else focusSection(sectionAt(audio.currentTime || (range ? range.start : 0)));
    }

    function play(start, end) {
      range = { start: start, end: end };
      /* Setting currentTime before the first load sets where playback begins. */
      audio.currentTime = start;
      var p = audio.play();
      if (p && p.catch) p.catch(function () { range = null; setReading(false); });
      audio.addEventListener('loadedmetadata', function () {
        if (range && Math.abs(audio.currentTime - range.start) > 1) audio.currentTime = range.start;
      }, { once: true });
      focusSection(sectionAt(start));
    }

    function stop() {
      if (audio.paused && !range) return;
      audio.pause();
      range = null;
      setReading(false);
    }

    audio.addEventListener('play', function () { setReading(true); update(); });
    audio.addEventListener('pause', function () { setReading(false); });   /* the lock screen can resume the range */
    audio.addEventListener('ended', function () { range = null; setReading(false); });
    audio.addEventListener('timeupdate', update);

    function update() {
      if (!range) return;
      var t = audio.currentTime || 0;
      if (t >= range.end - 0.05) { stop(); return; }
      focusSection(sectionAt(t));
      bar.style.width = (100 * Math.max(0, t - range.start) / Math.max(1, range.end - range.start)) + '%';
      if ('mediaSession' in navigator && audio.duration && navigator.mediaSession.setPositionState) {
        try { navigator.mediaSession.setPositionState({ duration: audio.duration, playbackRate: audio.playbackRate, position: t }); } catch (e) {}
      }
    }

    /* A dropped connection mid-stream leaves the element stuck; reload at the same spot. */
    var recoveries = 0;
    audio.addEventListener('error', function () {
      if (!audio.error || !range) return;
      if (recoveries >= 3) { stop(); return; }
      recoveries += 1;
      var at = audio.currentTime;
      setTimeout(function () {
        audio.load();
        audio.addEventListener('loadedmetadata', function () {
          audio.currentTime = at;
          audio.play().catch(function () {});
        }, { once: true });
      }, 800 * recoveries);
    });
    audio.addEventListener('playing', function () { recoveries = 0; });

    /* ---- input: a label plays its statement, the title plays everything, anything stops ---- */
    var down = null;
    document.addEventListener('pointerdown', function (e) { down = { x: e.clientX, y: e.clientY }; }, true);
    document.addEventListener('click', function (e) {
      var moved = down && (Math.abs(e.clientX - down.x) > 8 || Math.abs(e.clientY - down.y) > 8);
      down = null;
      if (moved) return;                                                   /* a drag or a text selection */
      var sel = window.getSelection && window.getSelection();
      if (sel && sel.type === 'Range' && sel.toString()) return;
      if (range && !audio.paused) { stop(); return; }                      /* playing: one click stops */
      var target = e.target.closest('[data-nrp]');
      if (!target) return;
      var id = target.getAttribute('data-nrp');
      if (id === 'all') {
        e.preventDefault();
        play(0, m.duration);
        return;
      }
      var s = sections.filter(function (x) { return x.id === id; })[0];
      if (!s) return;
      e.preventDefault();
      play(s.start, s.start + s.duration);
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') stop(); });
    window.addEventListener('wheel', function () { userScrolledAt = Date.now(); }, { passive: true });
    window.addEventListener('touchmove', function () { userScrolledAt = Date.now(); }, { passive: true });

    /* ---- lock screen / hardware keys ------------------------------------------------- */
    if ('mediaSession' in navigator) {
      try {
        var author = document.querySelector('meta[name="author"]');
        navigator.mediaSession.metadata = new MediaMetadata({ title: m.title, artist: author ? author.content : '', album: document.title });
        navigator.mediaSession.setActionHandler('play', function () { if (range) audio.play(); else play(0, m.duration); });
        navigator.mediaSession.setActionHandler('pause', function () { audio.pause(); });
        navigator.mediaSession.setActionHandler('stop', stop);
        navigator.mediaSession.setActionHandler('seekbackward', function (d) { audio.currentTime = Math.max(range ? range.start : 0, audio.currentTime - (d.seekOffset || 15)); });
        navigator.mediaSession.setActionHandler('seekforward', function (d) { audio.currentTime = Math.min(range ? range.end : m.duration, audio.currentTime + (d.seekOffset || 15)); });
        navigator.mediaSession.setActionHandler('seekto', function (d) { if (d.seekTime != null) audio.currentTime = d.seekTime; });
      } catch (e) {}
    }
  }
})();
