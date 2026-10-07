/* Shree Jaljala reveal engine - PART 1/3 */
(function () {
  'use strict';
  if (window.__jjRevealInitialized) return;
  window.__jjRevealInitialized = true;
  function onReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else { fn(); }
  }
  onReady(function () {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var hasIO = ('IntersectionObserver' in window);
    if (reduce || !hasIO) return;
    if (!document.documentElement.classList.contains('js')) return;
    function show(el) {
      if (!el || el.classList.contains('is-visible')) return;
      el.classList.add('is-visible');
    }
    function applyDelay(el) {
      var d = el.getAttribute('data-delay');
      if (d !== null && d !== '') {
        var n = parseInt(d, 10);
        if (!isNaN(n)) el.style.transitionDelay = n + 'ms';
      }
    }
    var sectionObserver = new IntersectionObserver(function (entries) {
      for (var k = 0; k < entries.length; k++) {
        var entry = entries[k];
        if (!entry.isIntersecting) continue;
        var section = entry.target;
        sectionObserver.unobserve(section);
        var head = section.querySelectorAll('.programs-heading.reveal, .programs-subtitle.reveal, .stagger-child');
        for (var h = 0; h < head.length; h++) { applyDelay(head[h]); show(head[h]); }
        var line = section.querySelector('.heading-underline');
        if (line) { applyDelay(line); show(line); }
        var cards = section.querySelectorAll('.jj-pc__card.reveal');
        for (var c = 0; c < cards.length; c++) { show(cards[c]); }
        watchClones(section);
        var navs = section.querySelectorAll('.jj-pc__nav.reveal');
        for (var n = 0; n < navs.length; n++) { applyDelay(navs[n]); show(navs[n]); }
        var generics = section.querySelectorAll('.reveal:not(.programs-heading):not(.programs-subtitle):not(.jj-pc__card):not(.jj-pc__nav)');
        for (var g = 0; g < generics.length; g++) { applyDelay(generics[g]); show(generics[g]); }
      }
    }, { threshold: 0.2 });
    function watchClones(section) {
      var win = section.querySelector('[data-jj-pc-viewport]');
      var track = section.querySelector('[data-jj-pc-track]');
      if (!win || !track) return;
      var boxObserver = new IntersectionObserver(function (items) {
        for (var m = 0; m < items.length; m++) {
          if (items[m].isIntersecting) show(items[m].target);
        }
      }, { root: win, threshold: 0.35 });
      function tag() {
        var cards = track.querySelectorAll('.jj-pc__card.reveal');
        for (var t = 0; t < cards.length; t++) {
          var card = cards[t];
          var r = card.getBoundingClientRect();
          var w = win.getBoundingClientRect();
          var vis = r.left >= w.left - 8 && r.right <= w.right + 8;
          card.classList.toggle('off-screen', !vis);
          boxObserver.observe(card);
        }
      }
      tag();
      if ('MutationObserver' in window) {
        new MutationObserver(tag).observe(track, { childList: true });
      }
      var deb = null;
      track.addEventListener('transitionend', tag);
      window.addEventListener('resize', function () {
        clearTimeout(deb);
        deb = setTimeout(tag, 150);
      });
    }
    var sections = document.querySelectorAll('[data-jj-programs-carousel], [data-reveal-section]');
    for (var s = 0; s < sections.length; s++) sectionObserver.observe(sections[s]);
    setTimeout(function () {
      for (var f = 0; f < sections.length; f++) {
        var r = sections[f].getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) {
          var all = sections[f].querySelectorAll('.reveal, .heading-underline');
          for (var a = 0; a < all.length; a++) show(all[a]);
        }
      }
    }, 1200);
  });
})();
