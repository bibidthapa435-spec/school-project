/* ============================================================
   GALLERY LIGHTBOX — zoom, captions, counter and keyboard nav
   ------------------------------------------------------------
   static/js/main.js already opens the shared #lightboxModal when
   a .gallery-lightbox-trigger is clicked, so this file only ADDS
   to it: the zoom entrance, the alt text, a category/description
   caption, an "n of m" counter and Previous/Next controls
   (buttons + Arrow keys). It works on any page that renders those
   triggers (gallery + home), and does nothing at all when
   Bootstrap or the modal is missing.
   ============================================================ */
(function () {
  'use strict';

  var triggers = Array.prototype.slice.call(
    document.querySelectorAll('.gallery-lightbox-trigger[data-index]')
  );

  var modal = document.getElementById('lightboxModal');
  if (!triggers.length || !modal || typeof bootstrap === 'undefined') return;

  var image = document.getElementById('lightboxImage');
  var title = document.getElementById('lightboxTitle');
  var body = modal.querySelector('.modal-body');
  if (!image || !title || !body) return;

  /* A visitor who asked for stillness gets the photo, not the animation. */
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ── Build the caption + navigation once, inside the shared modal ── */
  var caption = document.createElement('div');
  caption.className = 'g-lightbox__caption';

  var meta = document.createElement('div');
  meta.className = 'g-lightbox__meta';

  var category = document.createElement('span');
  category.className = 'g-lightbox__cat';

  var counter = document.createElement('span');
  counter.className = 'g-lightbox__count';

  meta.appendChild(category);
  meta.appendChild(counter);

  var description = document.createElement('p');
  description.className = 'g-lightbox__desc';

  var nav = document.createElement('div');
  nav.className = 'g-lightbox__nav';

  var prev = document.createElement('button');
  prev.type = 'button';
  prev.className = 'g-lightbox__btn';
  prev.innerHTML = '<i class="fa-solid fa-chevron-left" aria-hidden="true"></i> Previous';

  var next = document.createElement('button');
  next.type = 'button';
  next.className = 'g-lightbox__btn';
  next.innerHTML = 'Next <i class="fa-solid fa-chevron-right" aria-hidden="true"></i>';

  nav.appendChild(prev);
  nav.appendChild(next);

  caption.appendChild(meta);
  caption.appendChild(description);
  caption.appendChild(nav);
  body.appendChild(caption);

  /* One photo means there is nothing to page through. */
  if (triggers.length < 2) nav.hidden = true;

  var current = 0;

  /* Restart the zoom on every image change. Adding the class is not enough on
     its own — once the animation has run, the class stays on and re-adding it
     changes nothing, so we drop it, force a reflow to flush the old animation
     off the element, then add it back. That is what makes Next/Prev zoom the
     new photo instead of just replacing it. */
  function replayZoom() {
    if (reduceMotion.matches) return;

    var nodes = [image, caption];
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].classList.remove('g-lightbox-zoom');
    }
    void modal.offsetWidth;               // flush, so the animation restarts
    for (var k = 0; k < nodes.length; k++) {
      nodes[k].classList.add('g-lightbox-zoom');
    }
  }

  function show(index) {
    current = (index + triggers.length) % triggers.length;

    var trigger = triggers[current];
    var src = trigger.getAttribute('data-img');
    var label = trigger.getAttribute('data-title') || 'Gallery photo';

    image.src = src || '';
    image.alt = trigger.getAttribute('data-alt') || label;
    title.textContent = label;
    category.textContent = trigger.getAttribute('data-category') || '';
    description.textContent = trigger.getAttribute('data-desc') || '';
    counter.textContent = (current + 1) + ' of ' + triggers.length;

    replayZoom();
  }

  triggers.forEach(function (trigger, index) {
    trigger.addEventListener('click', function () {
      show(index);
    });
  });

  prev.addEventListener('click', function () {
    show(current - 1);
  });

  next.addEventListener('click', function () {
    show(current + 1);
  });

  /* Arrow keys page through the photos while the lightbox is open.
     Escape is left to Bootstrap, which already closes the modal. */
  document.addEventListener('keydown', function (event) {
    if (!modal.classList.contains('show')) return;
    if (triggers.length < 2) return;

    if (event.key === 'ArrowRight') {
      show(current + 1);
      event.preventDefault();
    } else if (event.key === 'ArrowLeft') {
      show(current - 1);
      event.preventDefault();
    }
  });
})();
