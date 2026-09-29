// Main JavaScript for Jaljala Secondary School Portal
document.addEventListener('DOMContentLoaded', function () {

  // Single source of truth for the motion preference, read by the
  // counters, the slider and the gallery. Declared once here and
  // reused below.
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  // Small helper used by the carousel logic below.
  const isReducedMotion = () => window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  // ---------------------------------------------------------------
  // Latest Notices ticker: seamless right-to-left loop.
  // The track holds TWO identical lists and the CSS slides 0 -> -50%,
  // so one loop = exactly one list width. Speed is px/sec (not a fixed
  // duration), so 1 notice and 5 notices scroll at the same pace.
  // Pure CSS still scrolls with JS disabled; this only tunes duration
  // and pauses the loop for reduced-motion users.
  // ---------------------------------------------------------------
  (function initNoticeTicker() {
    const track = document.querySelector('[data-ticker-track]');
    if (!track) return;
    const bar = track.closest('.notice-marquee-bar');
    const viewport = track.closest('.notice-marquee-bar__viewport');
    const PX_PER_SECOND = 90;

    function applyDuration() {
      const first = track.querySelector('.notice-marquee-bar__list');
      if (!first || !first.offsetWidth || !viewport) return;
      // Total travel per loop = enter offset (off-screen right) + one list
      // width (-50%). Duration covers that distance at a constant px/sec,
      // so short/long titles scroll at the same pace, like a <marquee>.
      const distance = viewport.offsetWidth + first.offsetWidth;
      track.style.setProperty('--ticker-enter', viewport.offsetWidth + 'px');
      const seconds = Math.max(12, distance / PX_PER_SECOND);
      track.style.setProperty('--ticker-duration', seconds.toFixed(2) + 's');
    }

    function ensureWidth() {
      // A single short title can be narrower than the viewport, which would
      // leave an empty gap in the -50% loop. Repeat that title INSIDE each
      // list until one list fills the viewport; both lists stay identical
      // so the loop seam never shows.
      if (!viewport) return;
      const lists = track.querySelectorAll('.notice-marquee-bar__list');
      if (!lists.length) return;
      const first = lists[0];
      let guard = 0;
      while (first.offsetWidth < viewport.offsetWidth + 200 && guard < 5) {
        first.querySelectorAll('.notice-marquee-bar__item').forEach((item) => {
          first.appendChild(item.cloneNode(true));
        });
        guard += 1;
      }
      // Second list mirrors the first so the -50% jump is pixel-identical.
      // Its links are removed from tab order (the first list already
      // exposes every notice to keyboard users).
      if (lists[1]) {
        lists[1].innerHTML = first.innerHTML;
        lists[1].querySelectorAll('a').forEach((a) => a.setAttribute('tabindex', '-1'));
      }
    }

    function syncReducedMotion() {
      if (bar) bar.classList.toggle('is-paused', isReducedMotion());
    }

    // Measure after fonts/layout settle so the first loop is exact.
    function refresh() { ensureWidth(); applyDuration(); }
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(refresh);
    }
    window.addEventListener('load', refresh);
    window.addEventListener('resize', refresh);
    refresh();
    syncReducedMotion();
  })();

  // Initialize AOS (Animate on Scroll) — removed per redesign brief
  // (one deliberate hero moment only; no fade-in-on-scroll).
  
  // Back to top button

    // Sticky Navbar - pinned to the top of the viewport once the top bar
    // and brand header have scrolled away, and it stays there for the
    // rest of the page.
    const navbar = document.querySelector('#mainNav') || document.querySelector('nav.navbar-custom') || document.querySelector('.navbar-custom');
    const topBar = document.querySelector('.top-bar');
    const brandHeader = document.querySelector('.brand-header');

    if (navbar) {
      let isSticky = false;
      let ticking = false;
      // The scroll threshold only changes when the header is re-laid-out
      // (resize, font load) — not on every scroll frame. Caching it keeps
      // the handler down to a single comparison and avoids two forced
      // layout reads on every tick.
      let scrollThreshold = 0;

      // The body padding must match the navbar's CURRENT height at the
      // moment it becomes fixed, otherwise the page content jumps by the
      // difference (the "sticky navbar jump" the audit reported). It is
      // also re-measured on resize, because the bar changes height when
      // the viewport crosses the collapse breakpoint.
      const syncNavbarHeight = () => {
        document.documentElement.style.setProperty(
          '--navbar-height',
          navbar.offsetHeight + 'px'
        );
      };

      syncNavbarHeight();

      // Calculate the scroll threshold (top bar + brand header height)
      const getScrollThreshold = () => {
        const topBarHeight = topBar ? topBar.offsetHeight : 0;
        const brandHeight = brandHeader ? brandHeader.offsetHeight : 0;
        return topBarHeight + brandHeight;
      };

      scrollThreshold = getScrollThreshold();

      // Activate sticky mode - navbar becomes fixed at top
      const activateSticky = () => {
        if (isSticky) return;
        isSticky = true;
        // Measure BEFORE switching to `position: fixed`, while the bar is
        // still in normal flow and its height still reflects the layout.
        syncNavbarHeight();
        navbar.classList.add('is-sticky');
        document.body.classList.add('sticky-nav-active');
      };

      // Deactivate sticky mode - navbar returns to original normal position
      const deactivateSticky = () => {
        if (!isSticky) return;
        isSticky = false;
        navbar.classList.remove('is-sticky');
        document.body.classList.remove('sticky-nav-active');
      };

      // Scroll handler - simple threshold check, no direction detection,
      // so the bar can never hide itself again while scrolling down.
      const handleScroll = () => {
        if (window.scrollY > scrollThreshold) {
          // Past the original navbar position - make it sticky
          activateSticky();
        } else {
          // Back at the top - restore to normal position
          deactivateSticky();
        }
      };

      // Throttled scroll listener using requestAnimationFrame
      window.addEventListener('scroll', function () {
        if (!ticking) {
          window.requestAnimationFrame(function () {
            handleScroll();
            ticking = false;
          });
          ticking = true;
        }
      }, { passive: true });

      // A page restored mid-scroll (refresh, back/forward cache, a deep
      // link straight to an anchor) never fires a scroll event, so the
      // navbar would sit in the flow while the header is already gone.
      // Evaluate once on load to settle the initial state.
      handleScroll();

      // Keep the body padding in step with the navbar on resize, and
      // re-evaluate stickiness because the header height also changed.
      let resizeTimer;
      window.addEventListener('resize', function () {
        scrollThreshold = getScrollThreshold();
        syncNavbarHeight();
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleScroll, 100);
      });

      // While the collapsed mobile menu is open the bar is much taller
      // than the reserved padding. Drop the reservation for the duration
      // so the menu is never clipped and the page does not jump.
      const collapseEl = document.getElementById('mainNavbar');
      if (collapseEl) {
        collapseEl.addEventListener('shown.bs.collapse', function () {
          document.body.classList.add('nav-menu-open');
        });
        collapseEl.addEventListener('hidden.bs.collapse', function () {
          document.body.classList.remove('nav-menu-open');
          syncNavbarHeight();
        });
      }
    }

    // Back to top button

  const backToTopBtn = document.getElementById('back-to-top');
  if (backToTopBtn) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 300) {
        backToTopBtn.style.display = 'flex';
      } else {
        backToTopBtn.style.display = 'none';
      }
    });

    backToTopBtn.addEventListener('click', function () {
      // Honour the motion preference: no smooth scroll for a visitor
      // who asked for reduced motion.
      window.scrollTo({
        top: 0,
        behavior: prefersReducedMotion ? 'auto' : 'smooth'
      });
    });
  }

  // Global preloader dismissal
  window.dismissPreloader = function() {
    const preloader = document.getElementById('school-preloader');
    if (preloader && !preloader.classList.contains('fade-out')) {
      // The pre-paint flag is what holds the overlay on screen
      // (html.jj-splash in style.css), so it goes first: while it is still
      // set, the fade-out class underneath could not win.
      document.documentElement.classList.remove('jj-splash');
      preloader.classList.add('fade-out');
      setTimeout(() => { preloader.style.display = 'none'; }, 600);
    }
  };

  // Splash screen. Whether this load shows it was already decided in <head>,
  // before the page was painted (first visit of the session, or a click on
  // Home), and flagged as `jj-splash` on <html>. Deciding again here - which
  // is what this block used to do - put the splash on screen seconds after
  // the site on a cold load. All that is left is taking it down again.
  const preloader = document.getElementById('school-preloader');
  if (preloader) {
    if (document.documentElement.classList.contains('jj-splash')) {
      preloader.classList.add('visible');
      preloader.classList.remove('fade-out');
      setTimeout(() => window.dismissPreloader(), 1850);
    } else {
      preloader.style.display = 'none';
    }
  }

  document.querySelectorAll('a[href="/"]').forEach(link => {
    link.addEventListener('click', function () {
      try {
        sessionStorage.setItem('show-preloader', '1');
      } catch (e) {
        // Storage blocked: the Home click simply will not replay the splash.
      }
    });
  });

  // ---------------------------------------------------------------
  // Hero slider: pause auto-advance on hover and on keyboard focus,
  // and never auto-advance for a reduced-motion visitor.
  // Bootstrap pauses on hover by default but NOT on focus, which is
  // the gap the audit found.
  // ---------------------------------------------------------------
  const heroSlider = document.getElementById('schoolSlider');
  if (heroSlider && window.bootstrap) {
    const carousel = bootstrap.Carousel.getOrCreateInstance(heroSlider, {
      interval: 7000,
      ride: false
    });

    const pause = () => carousel.pause();
    const resume = () => {
      // Only resume if the visitor has not asked for reduced motion.
      if (heroSlider.dataset.bsRide === 'carousel' && !isReducedMotion()) {
        carousel.cycle();
      }
    };

    ['mouseenter', 'focusin'].forEach(evt =>
      heroSlider.addEventListener(evt, pause)
    );
    ['mouseleave', 'focusout'].forEach(evt =>
      heroSlider.addEventListener(evt, resume)
    );

    // Stop the ride entirely if the preference flips on mid-session.
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motionQuery.addEventListener) {
      motionQuery.addEventListener('change', function (e) {
        if (e.matches) carousel.pause();
      });
    }
  }

  // ---------------------------------------------------------------
  // Global broken-image safety net.
  // Some uploaded media referenced by the database is missing (the
  // audit found /media/sliders/sport_3.jpg and
  // /media/notices/1000031894.jpg returning 404). A broken image
  // must never leave an ugly empty box: if the element has a
  // data-fallback-src, use it once; if the fallback also fails,
  // remove the element so the layout closes up cleanly.
  // Uses capture=true so it also catches errors from images whose
  // own onerror attribute has not yet run.
  // ---------------------------------------------------------------
  document.addEventListener(
    'error',
    function (event) {
      const el = event.target;
      if (!el || el.tagName !== 'IMG') return;

      const fallback = el.getAttribute('data-fallback-src');
      if (fallback && el.src !== fallback && !el.dataset.fallbackTried) {
        el.dataset.fallbackTried = '1';
        el.src = fallback;
        return;
      }

      // Nothing left to try: drop it rather than show a broken icon.
      // Preserve the space when the image has an explicit aspect box.
      if (el.classList.contains('teacher-photo') ||
          el.classList.contains('school-logo')) {
        el.style.visibility = 'hidden';
      } else {
        el.remove();
      }
    },
    true
  );

  // Gallery Lightbox Modal
  const galleryLinks = document.querySelectorAll('.gallery-lightbox-trigger');
  const lightboxModal = document.getElementById('lightboxModal');
  const lightboxImg = document.getElementById('lightboxImage');
  const lightboxTitle = document.getElementById('lightboxTitle');

  if (galleryLinks.length > 0 && lightboxImg && lightboxTitle) {
    galleryLinks.forEach(link => {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        const imgSrc = this.getAttribute('data-img');
        const title = this.getAttribute('data-title');
        lightboxImg.src = imgSrc;
        lightboxTitle.textContent = title || 'Gallery Image';
        const modal = new bootstrap.Modal(lightboxModal);
        modal.show();
      });
    });
  }

  // Auto-hide alert messages
  const alertMessages = document.querySelectorAll('.alert-dismissible');
  alertMessages.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 6000);
  });

  // Numbers counter animation (signature moment, brief §2§3): count up once
  // when the trust band enters the viewport. Replaces the old scroll+setInterval
  // version so both do not fight over the same .stat-number spans.
  const statCounters = document.querySelectorAll('.stat-number[data-count]');

  function animateCount(el, target, suffix, duration) {
    if (prefersReducedMotion) {
      el.textContent = target + suffix;
      return;
    }
    const startTime = performance.now();
    function tick(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      el.textContent = Math.floor(eased * target) + suffix;
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  if (statCounters.length) {
    if ('IntersectionObserver' in window) {
      const statObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          animateCount(el, parseInt(el.getAttribute('data-count'), 10), el.getAttribute('data-suffix') || '', 1400);
          statObserver.unobserve(el);
        });
      }, { threshold: 0.5 });
      statCounters.forEach((el) => statObserver.observe(el));
    } else {
      statCounters.forEach((el) => {
        el.textContent = el.getAttribute('data-count') + (el.getAttribute('data-suffix') || '');
      });
    }
  }

  // Gallery scroll-triggered animation using IntersectionObserver
  function initGalleryAnimation() {
    // Check if user prefers reduced motion
    if (prefersReducedMotion) {
      // Skip animation for users who prefer reduced motion
      document.querySelectorAll('.gallery-item-animate').forEach(item => {
        item.classList.add('animated');
      });
      return;
    }

    const galleryItems = document.querySelectorAll('.gallery-item-animate');
    
    if (galleryItems.length === 0) return;

    // Create IntersectionObserver for scroll-triggered animations
    const observerOptions = {
      root: null, // viewport
      rootMargin: '0px',
      threshold: 0.1 // trigger when 10% of element is visible
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // Add staggered delay based on item position
          const delay = entry.target.dataset.index * 100; // 100ms stagger between items
          setTimeout(() => {
            entry.target.classList.add('animated');
          }, delay);
          
          // Stop observing once animated
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Add index to each gallery item for staggered animation
    galleryItems.forEach((item, index) => {
      item.dataset.index = index;
      observer.observe(item);
    });
  }

  // Initialize gallery animation on page load
  initGalleryAnimation();
});
