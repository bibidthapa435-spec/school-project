/* ===========================================================================
   Academic Programs carousel
   ---------------------------------------------------------------------------
   Vanilla, no dependency. Bootstrap 5 is already on the page, but its
   Carousel moves exactly one .carousel-item per step and cannot do a
   multi-card 3-up loop, so the loop is implemented here directly.

   How the infinite loop works
   --------------------------
   With N programs and P visible per view the track is built as:

       [ clone xP ][ real xN ][ clone xP ]

   `index` is the position (0-based, into the FULL track) of the leftmost
   visible slide, and it may run 0 .. N+P-1. Because P clones sit on each
   side there is always a full page of real content to the right of `index`,
   so the row can never run into empty space.

   On reaching the far right, `index` re-seats onto the equivalent position
   among the left-hand clones. Those clones are pixel-identical to the real
   slides in that region, so the jump is invisible: it is applied with the
   transition switched off for one frame, hence `.is-settling`.

   Everything animates via `transform: translate3d()` only. Width, left and
   margin are never animated, so the loop costs no layout and cannot lag.

   Accessibility
     - Viewport is a labelled `region` with `aria-roledescription`.
     - Autoplay pauses on hover AND on focus, and never starts at all under
       `prefers-reduced-motion`.
     - Arrow keys page the carousel when the viewport has focus.
     - Clones are `aria-hidden` + `inert` with `tabindex="-1"` descendants,
       so AT and the tab order only ever see the N real programs.
   =========================================================================== */
(function () {
  'use strict';

  if (window.__jjProgramCarousel) return;
  window.__jjProgramCarousel = true;

  // 3s between automatic advances, as requested. Comfortably longer than the
  // 620ms CSS transition below, so a slide always finishes moving before the
  // next one starts - the row can never appear to stutter.
  var INTERVAL = 3000;
  var SWIPE_MIN_PX = 45;    // horizontal travel that counts as a swipe

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var roots = document.querySelectorAll('[data-jj-programs-carousel]');
    for (var r = 0; r < roots.length; r++) {
      try {
        initCarousel(roots[r]);
      } catch (err) {
        /* A carousel failure must never break the page: on any thrown error
           the server-rendered list is still on screen and still readable. */
        if (window.console) console.error('Program carousel failed to start', err);
      }
    }
  });


  function initCarousel(root) {
    var viewport = root.querySelector('[data-jj-pc-viewport]');
    var track = root.querySelector('[data-jj-pc-track]');
    var prevBtn = root.querySelector('[data-jj-pc-prev]');
    var nextBtn = root.querySelector('[data-jj-pc-next]');
    if (!viewport || !track) return;

    // The server-rendered slides. Everything added after this is a clone.
    var slides = Array.prototype.slice.call(track.children);
    var count = slides.length;
    if (!count) return;

    var motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    var perView = 1;      // slides visible; mirrors --jj-pc-per in the CSS
    var index = 0;        // leftmost visible slide, index into the full track
    var step = 0;         // px to translate per one slide
    var timer = null;
    var paused = false;   // hover / focus / off-screen pause
    var dragging = false;
    var pointerX = 0;
    var pointerId = null;
    var wrapFrame = null;   // pending rAF that finishes a loop re-seat

    // -------------------------------------------------------------- metrics

    function readPerView() {
      /* Read the value CSS actually resolved, so JS can never disagree with
         the slide widths the visitor sees. */
      var n = parseInt(getComputedStyle(root).getPropertyValue('--jj-pc-per'), 10);
      return n > 0 ? n : 1;
    }

    function measure() {
      var first = track.children[0];
      if (!first) { step = 0; return; }
      var style = getComputedStyle(track);
      var gap = parseFloat(style.columnGap || style.gap) || 0;
      step = first.getBoundingClientRect().width + gap;
    }

    function maxIndex() {
      // Track is [ lead x 2P ][ real x N ][ tail x P ], so the last window
      // that still shows P real-ish slides starts at 2P + N.
      return 2 * perView + count;
    }

    function startIndex() {
      // Start on the first REAL slide, not on a lead clone.
      return 2 * perView;
    }

    // ------------------------------------------ clone-based infinite track

    function makeClone(source) {
      var node = source.cloneNode(true);
      node.setAttribute('data-jj-pc-clone', '');
      var img = node.querySelector('img');
      if (img) img.removeAttribute('loading');
      return node;
    }

    function build() {
      // Clear any previous clone set before rebuilding.
      var existing = track.querySelectorAll('[data-jj-pc-clone]');
      for (var i = 0; i < existing.length; i++) {
        existing[i].parentNode.removeChild(existing[i]);
      }

      perView = readPerView();

      /* Only a single program is genuinely unscrollable. With two or more the
         row still loops (a school may well publish exactly 3, which is what
         fits a desktop row), so the arrows stay live in that case. */
      var scrollable = count > 1;
      root.classList.toggle('jj-pc--static', !scrollable);
      if (prevBtn) prevBtn.hidden = !scrollable;
      if (nextBtn) nextBtn.hidden = !scrollable;
      if (!scrollable) {
        /* `index` must be zeroed HERE, not just left alone. The window 'load'
           handler below re-applies setTranslate(index * step) after measuring,
           and a single slide has no clone runway to sit in - so a stale
           startIndex() (2 * perView = 6 on desktop) would shift the lone card
           1800px to the left and out of the clip box, leaving an empty section
           under its own heading. The static CSS cannot rescue it: this writes an
           INLINE transform, which outranks `.jj-pc--static .jj-pc__track`. */
        index = 0;
        stop();
        setTranslate(0, false);
        return;
      }

      /* Runway layout: 2P lead clones, N real slides, P tail clones.

         The tail gives the forward wrap somewhere to land, and the DOUBLE lead
         gives the backward wrap the same amount of runway. With only P lead
         clones a backward step past the first real slide would run out of
         track and show blank space. */
      var before = document.createDocumentFragment();
      var after = document.createDocumentFragment();

      for (var k = 0; k < 2 * perView; k++) {
        before.appendChild(makeClone(slides[(((count - 2 * perView + k) % count) + count) % count]));
      }
      for (var j = 0; j < perView; j++) {
        after.appendChild(makeClone(slides[j % count]));
      }

      track.insertBefore(before, track.firstChild);
      track.appendChild(after);

      // Clones are decorative duplicates: hide them from AT and keep them out
      // of the tab order, so only the N real programs are reachable.
      var clones = track.querySelectorAll('[data-jj-pc-clone]');
      for (var c = 0; c < clones.length; c++) {
        clones[c].setAttribute('aria-hidden', 'true');
        if ('inert' in HTMLElement.prototype) clones[c].inert = true;
        var focusables = clones[c].querySelectorAll('a, button, [tabindex]');
        for (var f = 0; f < focusables.length; f++) {
          focusables[f].setAttribute('tabindex', '-1');
        }
      }
      for (var s = 0; s < slides.length; s++) {
        slides[s].removeAttribute('aria-hidden');
        slides[s].removeAttribute('inert');
      }

      measure();
      setTranslate(index * step, false);
    }


    // ------------------------------------------------------------ positioning

    function setTranslate(px, animate) {
      /* A non-animated write supersedes any re-seat still waiting on a frame,
         so cancel it here rather than letting a stale rAF yank the row back. */
      if (!animate && wrapFrame !== null) {
        window.cancelAnimationFrame(wrapFrame);
        wrapFrame = null;
      }

      track.classList.toggle('is-settling', !animate);
      track.style.transform = 'translate3d(' + (-px) + 'px, 0, 0)';

      if (!animate) {
        /* Reading offsetWidth forces a style+layout flush, so this transform is
           committed RIGHT NOW with transitions off. Committing synchronously
           is the whole point: a timer - or anything else deferred - lets the
           next animation frame overtake it, and the move is then applied while
           .is-settling is still on. That is an instant jump with no visible
           motion, which is exactly how the loop wrap looked like a stall. */
        void track.offsetWidth;
      }
    }

    function goTo(target, animate) {
      if (count < 2) return;

      /* The clone layout repeats every `count` slides, so the window sitting
         exactly `count` positions away shows the identical cards. Crossing the
         seam is therefore two moves, never one animated jump:

           1. re-seat onto that equivalent position with the transition OFF -
              invisible, because the cards under the left edge do not change;
           2. run the real one-slide step from there, which animates normally.

         Tweening straight to the wrapped target instead would drag the whole
         row backwards across the screen: a very visible multi-card rewind. */
      var rebase = null;

      if (target > maxIndex()) {
        rebase = index - count;
        target = rebase + 1;
      } else if (target < 0) {
        rebase = index + count;
        target = rebase - 1;
      }

      index = target;

      if (rebase !== null) {
        /* Leg 1 - land on the equivalent position with transitions OFF. The
           cards under the left edge do not change, so this is invisible. */
        setTranslate(rebase * step, false);

        /* Leg 2 - the real one-slide step, on the NEXT frame. Waiting a frame
           guarantees the browser has taken the re-seat first, so this is a
           clean 620ms slide instead of two writes it can coalesce into one
           instant jump. */
        if (wrapFrame !== null) window.cancelAnimationFrame(wrapFrame);
        wrapFrame = window.requestAnimationFrame(function () {
          wrapFrame = null;
          track.classList.remove('is-settling');
          track.style.transform = 'translate3d(' + (-index * step) + 'px, 0, 0)';
        });
        return;
      }

      setTranslate(index * step, animate);
    }

    function next() { goTo(index + 1, true); }
    function prev() { goTo(index - 1, true); }

    // --------------------------------------------------------------- autoplay

    function tick() {
      goTo(index + 1, true);
    }

    function start() {
      if (timer || paused) return;
      if (count < 2) return;
      timer = window.setInterval(tick, INTERVAL);
    }

    function stop() {
      window.clearInterval(timer);
      timer = null;
    }

    function resume() {
      paused = false;
      // A reduced-motion visitor never gets an auto-advancing carousel.
      if (!motionQuery.matches) start();
    }

    /* Manual navigation restarts the dwell, so a click never "uses up" the
       autoplay timer, and never stops it either. */
    function restart() {
      if (!timer) return;
      stop();
      if (!paused && !motionQuery.matches) start();
    }

    // ----------------------------------------------------------------- events

    if (prevBtn) {
      prevBtn.addEventListener('click', function () { prev(); restart(); });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', function () { next(); restart(); });
    }

    // Pause on hover AND on focus, resume on leave - matching the hero slider
    // so the two carousels feel consistent on this site.
    ['mouseenter', 'focusin'].forEach(function (evt) {
      root.addEventListener(evt, function () { paused = true; stop(); });
    });
    ['mouseleave', 'focusout'].forEach(function (evt) {
      root.addEventListener(evt, resume);
    });

    // Keyboard paging when the carousel itself has focus.
    viewport.setAttribute('tabindex', '0');
    viewport.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { next(); restart(); e.preventDefault(); }
      else if (e.key === 'ArrowLeft') { prev(); restart(); e.preventDefault(); }
    });

    // ---- Swipe / drag (pointer events cover touch, pen and mouse) --------
    viewport.addEventListener('pointerdown', function (e) {
      // A drag that starts on the card link must stay a normal tap, so the
      // pointer is not hijacked in that case.
      if (e.target.closest && e.target.closest('a')) return;
      dragging = true;
      pointerX = e.clientX;
      pointerId = e.pointerId;
      paused = true;
      stop();
    });

    viewport.addEventListener('pointerup', function (e) {
      if (!dragging) return;
      dragging = false;
      if (pointerId !== null && e.pointerId !== pointerId) return;
      var delta = e.clientX - pointerX;
      if (Math.abs(delta) >= SWIPE_MIN_PX) {
        if (delta < 0) { next(); } else { prev(); }
      }
      resume();
    });

    viewport.addEventListener('pointercancel', function () {
      dragging = false;
      resume();
    });

    /* Safety net: pointerdown sets paused = true, and only the handlers above
       clear it again. A drag that ends off-window - or a pointerup the element
       never receives - would otherwise latch paused for the rest of the session
       and autoplay would never return. Watching the window guarantees the
       release is seen. */
    ['pointerup', 'pointercancel'].forEach(function (evt) {
      window.addEventListener(evt, function () {
        if (!dragging) return;
        dragging = false;
        resume();
      });
    });

    /* Same latch risk from a tab switch: intervals are throttled hard in a
       background tab, so drop it and re-arm on return. */
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        stop();
      } else if (!paused && !motionQuery.matches) {
        start();
      }
    });

    // A horizontal swipe must not scroll the page sideways.
    viewport.addEventListener('touchmove', function (e) {
      if (e.cancelable) e.preventDefault();
    }, { passive: false });

    // Don't churn transforms for a section nobody is looking at.
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          if (!paused && !motionQuery.matches) start();
        } else {
          stop();
        }
      }, { threshold: 0.15 }).observe(root);
    }

    // If the preference flips mid-session, stop for good.
    if (motionQuery.addEventListener) {
      motionQuery.addEventListener('change', function (e) {
        if (e.matches) { stop(); paused = true; }
      });
    }

    /* Responsive rebuild: a change of per-view invalidates both the clone set
       and the current offset, so the track is rebuilt from scratch. Within one
       breakpoint the slides only change width, so re-measure in place and keep
       the visitor where they were. */
    var resizeTimer;
    var lastPerView = null;

    window.addEventListener('resize', function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(function () {
        var now = readPerView();
        if (now !== lastPerView) {
          lastPerView = now;
          // New breakpoint => new clone layout, so restart on the first
          // real slide rather than keeping a now-invalid offset.
          index = startIndex();
          build();
        } else {
          measure();
          if (index > maxIndex()) index = maxIndex();
          setTranslate(index * step, false);
        }
        if (!paused && !motionQuery.matches) start();
      }, 150);
    });

    // Late-loading images change the rendered slide width, so re-measure once
    // the page has fully settled.
    window.addEventListener('load', function () {
      measure();
      setTranslate(index * step, false);
    });

    // ------------------------------------------------------------------ start
    // readPerView() must run before startIndex(), which depends on it.
    lastPerView = readPerView();
    index = startIndex();
    build();
    if (!motionQuery.matches) start();
  }
})();
