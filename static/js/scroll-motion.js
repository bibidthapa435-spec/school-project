/* ===========================================================================
   Scroll-motion engine for Shree Jaljala Secondary School
   ---------------------------------------------------------------------------
   Ten subtle scroll behaviours, native only (IntersectionObserver + one
   requestAnimationFrame scroll loop). No third-party library.

     1. Smooth in-page scrolling (sticky-navbar aware, keyboard friendly)
     2. Fade-up reveal on entering the viewport          [data-aos="fade-up"]
     3. Fade-left / fade-right for text and images       [data-aos="fade-left"]
     4. Staggered card cascades                          [data-stagger="zoom-in"]
        …plus `fade` (opacity only, for table rows) and `alternate` (odd/even
        children enter from opposite sides, downgraded to a vertical group
        whenever the viewport is too narrow for the sideways start state)
     5. Subtle scale-in for important cards              [data-aos="scale-in"]
     6. Statistic counters      (already in main.js — left untouched, no clash)
     7. Subtle image reveals                             [data-img-reveal]
     8. Navbar active-section highlighting (home page sections)
     9. Subtle hero parallax                            [data-parallax]
    10. Position-linked scrub layer  [data-scrub="hero|title|card|zoom|line"]
    11. One sticky hero window                   (.jj-hero-pin, layout-safe)

   Design notes
   ------------
   * The vocabulary is the one the templates already speak (`data-aos`,
     `data-aos-delay`, `data-aos-duration`), so every existing call site keeps
     working — the previous CDN library was replaced, not the markup.
   * `jj-motion` is put on <html> before first paint by base.html, so hidden
     content never flashes; base.html also removes it again if this file never
     runs, so content can never be stranded invisible.
   * Only `translate` / `scale` / `rotate` / `opacity` / `clip-path` are
     animated. No layout properties, and horizontal reveals are downgraded to
     vertical ones whenever they could reach past the viewport edge — so this
     file cannot cause horizontal scrolling.
   * prefers-reduced-motion removes the flag and stops every observer.
   ========================================================================== */
(function () {
  'use strict';

  if (window.__jjMotionInit) return;   // never double-initialise
  window.__jjMotionInit = true;

  var root = document.documentElement;
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  var REVEAL_MARGIN = '0px 0px -80px 0px';    // ~80px of "about to be seen"
  var NAV_BAND = '-40% 0px -55% 0px';         // thin band around 45% viewport
  var HORIZONTAL = { 'fade-left': 1, 'fade-right': 1 };
  var STAGGER_MAX = 6;                        // cap the cascade
  var STAGGER_STEP = 70;                      // ms between cards

  function num(value, fallback) {
    var n = parseFloat(value);
    return isNaN(n) ? fallback : n;
  }

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  /* =======================================================================
     1. Reveal engine (items 2, 3, 4, 5 and 7)
     ===================================================================== */
  function initReveals() {
    var handlers = new Map();   // element -> callback fired on first intersect

    var observer = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        if (!entry.isIntersecting) continue;
        var fn = handlers.get(entry.target);
        observer.unobserve(entry.target);
        handlers.delete(entry.target);
        if (fn) fn(entry.target);
      }
    }, { rootMargin: REVEAL_MARGIN, threshold: 0 });

    // A `fade-left` element starts shifted right, which is the only variant
    // that can push past the viewport edge on a full-width column. Measure the
    // start-state box and fall back to fade-up when there is no room.
    function hasRoomForShift(el) {
      if (window.innerWidth < 576) return false;
      var rect = el.getBoundingClientRect();
      var viewport = root.clientWidth;
      var shift = num(getComputedStyle(root).getPropertyValue('--jj-shift-x'), 22);
      return rect.right + shift <= viewport;   // rect already includes the shift
    }

    // An "alternate" stagger child also starts shifted horizontally, so the
    // same edge test applies — but only from the width at which the CSS
    // actually starts moving the group sideways (1200px). Below that the
    // group is already vertical, so there is nothing to guard.
    function hasRoomForAlternateShift(el) {
      if (window.innerWidth < 1200) return true;
      return hasRoomForShift(el);
    }

    function watch(el, fn) {
      handlers.set(el, fn || function (target) { target.classList.add('jj-in'); });
      observer.observe(el);
    }

    function prepareAos(el) {
      var variant = el.getAttribute('data-aos');
      if (HORIZONTAL[variant] && !hasRoomForShift(el)) {
        variant = 'fade-up';
        el.setAttribute('data-aos', variant);
      }
      var delay = num(el.getAttribute('data-aos-delay'), 0);
      if (delay) el.style.setProperty('--jj-d', delay + 'ms');
      var duration = num(el.getAttribute('data-aos-duration'), 0);
      if (duration) el.style.setProperty('--jj-dur', duration + 'ms');
      watch(el);
    }

    function prepareStagger(container) {
      var step = num(container.getAttribute('data-stagger-step'), STAGGER_STEP);
      var kids = [];
      for (var i = 0; i < container.children.length; i++) {
        var child = container.children[i];
        // children that carry their own data-aos are handled individually
        if (child.hasAttribute('data-aos') || child.hasAttribute('data-stagger')) continue;
        child.style.setProperty('--jj-d', Math.min(kids.length, STAGGER_MAX) * step + 'ms');
        kids.push(child);
      }
      if (!kids.length) return;
      // An "alternate" group enters from opposite sides, so it can only run
      // where every child has room for the shift. The CSS already limits it to
      // wide viewports; this re-checks after a resize and falls back to the
      // plain vertical fade-up for the group as a whole.
      if (container.getAttribute('data-stagger') === 'alternate') {
        for (var k = 0; k < kids.length; k++) {
          if (!hasRoomForAlternateShift(kids[k])) { container.setAttribute('data-stagger', 'vertical'); break; }
        }
      }
      watch(container, function () {
        for (var k = 0; k < kids.length; k++) kids[k].classList.add('jj-in');
      });
    }

    var nodes = document.querySelectorAll('[data-aos], [data-img-reveal], [data-stagger]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.hasAttribute('data-stagger')) prepareStagger(el);
      else if (el.hasAttribute('data-aos')) prepareAos(el);
      else watch(el);
    }

    // Photos/fonts settling can move things; re-check anything still pending.
    window.addEventListener('load', function () {
      handlers.forEach(function (fn, el) { observer.unobserve(el); observer.observe(el); });
    });

    // Re-run the horizontal-overflow guard after a viewport change.
    return {
      refresh: function () {
        handlers.forEach(function (fn, el) {
          var variant = el.getAttribute ? el.getAttribute('data-aos') : null;
          if (variant && HORIZONTAL[variant] && !hasRoomForShift(el)) el.setAttribute('data-aos', 'fade-up');
          // An "alternate" group whose children lost their room (e.g. a resize
          // onto a narrower window) falls back to the vertical fade-up. Only
          // downgrade, never back: the first pass already ran before images
          // and fonts had settled, so a later "no room" reading is authoritative.
          if (el.getAttribute && el.getAttribute('data-stagger') === 'alternate') {
            var kids = el.children;
            for (var i = 0; i < kids.length; i++) {
              if (!hasRoomForAlternateShift(kids[i])) { el.setAttribute('data-stagger', 'vertical'); break; }
            }
          }
        });
      }
    };
  }

  /* =======================================================================
     2. Navbar active-section highlighting (item 8)
     The navbar links are routes, not hashes, so each in-page section is
     matched to the route it belongs to (`programs-section` -> /programs);
     a top-level toggle is highlighted when that route lives in a dropdown.
     ===================================================================== */
  function initNavTracking() {
    var nav = document.getElementById('mainNav');
    if (!nav || !nav.querySelector) return;

    var sections = document.querySelectorAll('main section[id], main section[data-nav-section]');
    if (!sections.length) return;

    function linkFor(section) {
      var name = section.getAttribute('data-nav-target') ||
        (section.id || '').replace(/-section$/, '');
      if (!name) return null;
      var links = nav.querySelectorAll('.navbar-nav a[href]');
      for (var i = 0; i < links.length; i++) {
        var href = links[i].getAttribute('href') || '';
        if (!href || href.charAt(0) === '#') continue;
        var path = href.split('#')[0].split('?')[0].replace(/\/+$/, '');
        if (path.split('/').pop() !== name) continue;
        var menu = links[i].closest('.dropdown-menu');
        if (menu && menu.parentNode && menu.parentNode.querySelector('.nav-link')) {
          return menu.parentNode.querySelector('.nav-link');   // highlight the toggle
        }
        return links[i];
      }
      return null;
    }

    var live = [];
    var current = null;
    var sync = function () {
      var winner = null;
      for (var i = 0; i < sections.length && !winner; i++) {
        if (live.indexOf(sections[i]) !== -1) winner = sections[i];   // topmost in view
      }
      var target = winner ? linkFor(winner) : null;
      if (target === current) return;
      if (current) current.classList.remove('jj-inview');
      if (target) target.classList.add('jj-inview');
      nav.classList.toggle('jj-nav-tracking', !!target);
      current = target;
    };

    var observer = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        var el = entries[i].target;
        var at = live.indexOf(el);
        if (entries[i].isIntersecting) {
          if (at === -1) live.push(el);
        } else if (at !== -1) {
          live.splice(at, 1);
        }
      }
      sync();
    }, { rootMargin: NAV_BAND, threshold: 0 });

    for (var i = 0; i < sections.length; i++) observer.observe(sections[i]);
  }

  /* =======================================================================
     3. Smooth in-page scrolling (item 1)
     Route links keep their normal navigation; only `#section` links are
     intercepted, scrolled with the sticky navbar taken into account, and
     focused for keyboard / screen-reader users.
     ===================================================================== */
  function initSmoothAnchors() {
    var FOCUSABLE = /^(a|button|input|select|textarea|summary)$/;

    document.addEventListener('click', function (event) {
      var link = event.target && event.target.closest ? event.target.closest('a[href^="#"]') : null;
      if (!link || link.hasAttribute('data-bs-toggle') || link.hasAttribute('data-bs-target')) return;
      var hash = link.getAttribute('href');
      if (!hash || hash === '#') return;                     // lightbox + dropdown toggles
      var target = document.getElementById(hash.slice(1));
      if (!target) return;

      var nav = document.getElementById('mainNav');
      var offset = document.body.classList.contains('sticky-nav-active') && nav ? nav.offsetHeight : 0;
      var top = target.getBoundingClientRect().top + window.pageYOffset - offset - 12;

      event.preventDefault();
      window.scrollTo({
        top: top > 0 ? top : 0,
        behavior: reducedMotion.matches ? 'auto' : 'smooth'
      });
      if (window.history && history.replaceState) history.replaceState(null, '', hash);

      var tag = (target.tagName || '').toLowerCase();
      if (!target.hasAttribute('tabindex') && !FOCUSABLE.test(tag)) target.setAttribute('tabindex', '-1');
      try { target.focus({ preventScroll: true }); } catch (e) { /* older browsers */ }
      target.addEventListener('blur', function () {
        if (target.getAttribute('tabindex') === '-1') target.removeAttribute('tabindex');
      }, { once: true });
    });
  }

  /* =======================================================================
     4. Subtle parallax for hero / background media (item 9)
     Runs only while the layer is near the viewport, drifts at most ~60% of
     the slack the CSS gives it, and never touches the shade or the text.
     ===================================================================== */
  function initParallax(onFrame) {
    var nodes = document.querySelectorAll('[data-parallax]');
    if (!nodes.length) return null;

    var items = [];

    function measure() {
      items.length = 0;
      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        var inner = el.firstElementChild;                       // the img / video
        var slack = inner ? (inner.offsetHeight - el.offsetHeight) / 2 : 0;
        if (slack < 4) continue;                                // nothing to drift
        items.push({
          el: el,
          slack: slack * 0.6,
          strength: num(el.getAttribute('data-parallax'), 1) || 1,
          active: false
        });
      }
      for (var j = items.length; j--;) items[j].el.style.transform = 'translate3d(0,0,0)';
    }
    measure();
    if (!items.length) return null;

    onFrame(function () {
      for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var rect = item.el.getBoundingClientRect();
        var active = rect.bottom > -80 && rect.top < window.innerHeight + 80;
        if (active !== item.active) {
          item.active = active;
          item.el.style.willChange = active ? 'transform' : '';
        }
        if (!active) continue;
        var progress = rect.height ? -rect.top / rect.height : 0;   // 0 at rest, 1 once passed
        if (progress < -1) progress = -1;
        if (progress > 1) progress = 1;
        var y = progress * item.slack * item.strength;
        item.el.style.transform = 'translate3d(0,' + y.toFixed(2) + 'px,0)';
      }
    });
    return measure;
  }

  /* =======================================================================
     5. Position-linked scrub layer (items 10 + 11)
     Unlike the one-shot reveals above, these elements are driven continuously
     by their own position in the viewport: every [data-scrub] element receives
     a quantised progress custom property (--jj-p: 0 below the fold -> 1 past
     it) and scroll-motion.css maps that to independent transform properties.

       hero — hero content lifts, shrinks and fades as the hero scrolls away
       title — headings drift and tilt a few degrees (subtle 3D depth)
       card — cards float in, settle centred, then ease out again
       zoom — images relax from a 5% zoom to 1.0 while crossing the view
       line — section-title dividers draw themselves (JS fallback only; the
              native CSS animation-timeline path in scroll-motion.css takes
              over in browsers that support it, and JS then stays out)

     `line` attributes are only injected when the browser lacks native CSS
     scroll-driven animations, so each divider is driven by exactly one path.
     ===================================================================== */
  function initScrub(onFrame) {
    var nativeViewTimeline = !!(window.CSS && CSS.supports &&
      CSS.supports('animation-timeline', 'view()'));

    if (!nativeViewTimeline) {
      var lines = document.querySelectorAll('.section-title .divider');
      for (var l = 0; l < lines.length; l++) lines[l].setAttribute('data-scrub', 'line');
    }

    var nodes = document.querySelectorAll('[data-scrub]');
    var items = [];
    for (var i = 0; i < nodes.length; i++) {
      items.push({
        el: nodes[i],
        mode: nodes[i].getAttribute('data-scrub'),
        last: null,
        active: false
      });
    }
    if (!items.length) return null;

    var vh = window.innerHeight;
    var measure = function () { vh = window.innerHeight; };

    onFrame(function () {
      for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var rect = item.el.getBoundingClientRect();
        var near = rect.bottom > -160 && rect.top < vh + 160;

        if (near !== item.active) {
          item.active = near;
          // Promote only the hero (one element) — layer-per-card would cost
          // more than the few pixels of paint it saves.
          if (item.mode === 'hero') item.el.style.willChange = near ? 'transform, opacity' : '';
        }

        var p;
        if (item.mode === 'hero') {
          // 0 while the hero is at rest, 1 once ~70% of it has scrolled past.
          p = -rect.top / Math.max(1, rect.height * 0.7);
        } else if (item.mode === 'line') {
          // Pre-compressed so the divider finishes drawing early in its pass.
          p = ((vh - rect.top) / Math.max(1, vh + rect.height)) * 2.2;
        } else {
          p = (vh - rect.top) / Math.max(1, vh + rect.height);
        }
        if (p < 0) p = 0; else if (p > 1) p = 1;

        // Quantised to 100 steps: sub-pixel drift needs no style writes, and
        // values already parked at an end stop (far off-screen) are skipped.
        var q = Math.round(p * 100) / 100;
        if (q === item.last) continue;
        item.last = q;
        item.el.style.setProperty('--jj-p', q.toFixed(2));
      }
    });

    return measure;
  }

  /* =======================================================================
     Boot
     ===================================================================== */
  ready(function () {
    if (reducedMotion.matches || !('IntersectionObserver' in window)) {
      root.classList.remove('jj-motion');       // nothing may stay hidden
      return;
    }
    root.classList.add('jj-motion');

    var frameCallbacks = [];
    var onFrame = function (fn) { frameCallbacks.push(fn); };
    var measures = [];
    var reveals;

    try {
      reveals = initReveals();
      measures.push(initParallax(onFrame));
      measures.push(initScrub(onFrame));
      initNavTracking();
      initSmoothAnchors();
    } catch (error) {
      root.classList.remove('jj-motion');       // fail safe: show the content
      if (window.console && console.warn) console.warn('scroll-motion: disabled —', error);
      return;
    }

    // One rAF-throttled scroll loop drives every per-frame behaviour.
    var queued = false;
    var run = function () {
      queued = false;
      for (var i = 0; i < frameCallbacks.length; i++) frameCallbacks[i]();
    };
    var onScroll = function () {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(run);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    var remeasure = function () {
      if (reveals) reveals.refresh();
      for (var i = 0; i < measures.length; i++) if (measures[i]) measures[i]();
      onScroll();
    };
    var resizeTimer = null;
    window.addEventListener('resize', function () {
      if (resizeTimer) clearTimeout(resizeTimer);
      resizeTimer = setTimeout(remeasure, 150);
    });
    window.addEventListener('orientationchange', remeasure);
    window.addEventListener('load', remeasure);

    // If the visitor asks for less motion mid-session, stop right away.
    var onPreference = function (event) {
      if (!event.matches) return;
      root.classList.remove('jj-motion');
      window.removeEventListener('scroll', onScroll);
    };
    if (reducedMotion.addEventListener) reducedMotion.addEventListener('change', onPreference);
    else if (reducedMotion.addListener) reducedMotion.addListener(onPreference);

    window.__jjMotionReady = true;   // the base.html watchdog stands down
  });
})();
