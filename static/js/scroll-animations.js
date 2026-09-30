/**
 * Shree Jaljala Secondary School - Animate-On-Scroll (SA) Engine
 * Smooth, lightweight, hardware-accelerated scroll animations using IntersectionObserver.
 * Zero layout thrashing, zero scroll event listeners for reveals.
 * Respects prefers-reduced-motion. Preserves existing card hover transforms.
 */

(function () {
  'use strict';

  // Prevent multiple initializations
  if (window.__saInitialized) return;
  window.__saInitialized = true;

  var root = document.documentElement;
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  // If reduced motion is preferred or IntersectionObserver is unsupported, bypass
  if (reducedMotion.matches || !('IntersectionObserver' in window)) {
    return;
  }

  // Activate CSS animations early to avoid flash of unstyled content
  root.classList.add('sa-active');

  // Watchdog safety net: if JS stalls, reveal all content so nothing is stuck invisible
  var safetyTimeout = setTimeout(function () {
    if (!window.__saReady) {
      root.classList.remove('sa-active');
      document.querySelectorAll('[data-sa], [data-aos], [data-img-reveal]').forEach(function (el) {
        el.classList.add('sa-animated');
      });
    }
  }, 2500);

  function parseNumber(val, fallback) {
    var n = parseFloat(val);
    return isNaN(n) ? fallback : n;
  }

  function isExcluded(el) {
    if (!el || el === document.body || el === root) return true;
    return !!el.closest(
      '.navbar, .navbar-custom, .top-bar, .brand-header, ' +
      '.top-notice-ticker, .notice-marquee, .notice-ticker, ' +
      '.carousel, .hero-slider, .modal, .lightbox-modal, #lightboxModal, ' +
      '.admin-layout, .admin-sidebar, .admin-main-content, [data-sa-ignore]'
    );
  }

  function onReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  onReady(function () {
    window.__saReady = true;
    clearTimeout(safetyTimeout);

    // Guard on resize for reduced motion toggle
    reducedMotion.addEventListener('change', function (e) {
      if (e.matches) {
        root.classList.remove('sa-active');
        document.querySelectorAll('[data-sa], [data-aos], [data-img-reveal]').forEach(function (el) {
          el.classList.add('sa-animated');
        });
      } else {
        root.classList.add('sa-active');
      }
    });

    var REVEAL_MARGIN = '0px 0px -40px 0px';
    var isMobile = window.innerWidth < 576;

    // Create the IntersectionObserver
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;

          var target = entry.target;

          // Check if this is a stagger container
          if (target.hasAttribute('data-stagger') || target.hasAttribute('data-sa-stagger')) {
            var step = parseNumber(
              target.getAttribute('data-stagger-step') || target.getAttribute('data-sa-stagger-step'),
              70
            );
            var children = target.children;
            for (var i = 0; i < children.length; i++) {
              (function (child, idx) {
                var delay = idx * step;
                child.style.setProperty('--sa-del', delay + 'ms');
                // Trigger animation
                requestAnimationFrame(function () {
                  child.classList.add('sa-animated');
                });
              })(children[i], i);
            }
          } else {
            // Direct target reveal
            target.classList.add('sa-animated');
          }

          // Once revealed, unobserve to free resources unless explicitly set to repeatable
          var once = target.getAttribute('data-sa-once') || target.getAttribute('data-aos-once');
          if (once !== 'false') {
            observer.unobserve(target);
          }
        });
      },
      {
        root: null,
        rootMargin: REVEAL_MARGIN,
        threshold: 0.05
      }
    );

    // Clean up hover interference after transition finishes
    document.addEventListener('transitionend', function (e) {
      if (e.target && e.target.classList && e.target.classList.contains('sa-animated')) {
        // Clear temporary transition properties so card :hover styles operate natively
        e.target.style.willChange = 'auto';
      }
    });

    // Helper to register an animation target
    function registerTarget(el, defaultVariant) {
      if (isExcluded(el)) return;

      var variant = el.getAttribute('data-sa') || el.getAttribute('data-aos');
      if (!variant) {
        variant = defaultVariant || 'fade-up';
        el.setAttribute('data-sa', variant);
      }

      // Safeguard against horizontal overflow on mobile for left/right animations
      if (isMobile && (variant === 'fade-left' || variant === 'fade-right' || variant === 'zoom-in-left' || variant === 'zoom-in-right')) {
        el.setAttribute('data-sa', 'fade-up');
      }

      var delay = el.getAttribute('data-sa-delay') || el.getAttribute('data-aos-delay');
      if (delay) {
        el.style.setProperty('--sa-del', parseNumber(delay, 0) + 'ms');
      }

      var duration = el.getAttribute('data-sa-duration') || el.getAttribute('data-aos-duration');
      if (duration) {
        el.style.setProperty('--sa-dur', parseNumber(duration, 700) + 'ms');
      }

      observer.observe(el);
    }

    // 1. Observe existing markup carrying data-sa, data-aos, data-img-reveal, data-stagger
    var existingTargets = document.querySelectorAll(
      '[data-sa], [data-aos], [data-img-reveal], [data-stagger], [data-sa-stagger]'
    );
    existingTargets.forEach(function (el) {
      if (isExcluded(el)) return;

      // Handle data-img-reveal (photos / gallery images default to zoom-in-up)
      if (el.hasAttribute('data-img-reveal') && !el.hasAttribute('data-sa') && !el.hasAttribute('data-aos')) {
        el.setAttribute('data-sa', 'zoom-in-up');
      }

      if (el.hasAttribute('data-stagger') || el.hasAttribute('data-sa-stagger')) {
        observer.observe(el);
      } else {
        registerTarget(el);
      }
    });

    // 2. Auto-wire 2-block rows: photo + text (fade-right and fade-left)
    var twoBlockRows = document.querySelectorAll('.row');
    twoBlockRows.forEach(function (row) {
      if (isExcluded(row)) return;
      var cols = row.children;
      // Filter out non-element children or hidden items
      var validCols = [];
      for (var i = 0; i < cols.length; i++) {
        if (cols[i].nodeType === 1 && !cols[i].classList.contains('visually-hidden') && cols[i].style.display !== 'none') {
          validCols.push(cols[i]);
        }
      }
      if (validCols.length === 2) {
        var col1 = validCols[0];
        var col2 = validCols[1];
        // If they don't already have explicit animation attributes
        if (!col1.hasAttribute('data-sa') && !col1.hasAttribute('data-aos') && !col1.hasAttribute('data-stagger')) {
          registerTarget(col1, 'fade-right');
        }
        if (!col2.hasAttribute('data-sa') && !col2.hasAttribute('data-aos') && !col2.hasAttribute('data-stagger')) {
          registerTarget(col2, 'fade-left');
        }
      }
    });

    // 3. Auto-wire images inside gallery and achievement sections that don't have animation yet
    var mediaImages = document.querySelectorAll(
      '.g-tile__img, .gallery-item img, .achievement-img-home, .achievement-image, .achievement-detail-image'
    );
    mediaImages.forEach(function (img) {
      if (isExcluded(img)) return;
      if (!img.hasAttribute('data-sa') && !img.hasAttribute('data-aos') && !img.closest('[data-stagger]')) {
        registerTarget(img, 'zoom-in-up');
      }
    });

    // 4. Auto-wire footer columns if footer is not already animated
    var footer = document.querySelector('footer');
    if (footer && !isExcluded(footer)) {
      var footerCols = footer.querySelectorAll('.col-lg-4, .col-lg-3, .col-lg-2, .col-md-6');
      footerCols.forEach(function (col, idx) {
        if (!col.hasAttribute('data-sa') && !col.hasAttribute('data-aos')) {
          col.setAttribute('data-sa', 'fade-up');
          col.setAttribute('data-sa-delay', (idx * 80) + '');
          registerTarget(col, 'fade-up');
        }
      });
    }
  });
})();
