// Main JavaScript for Jaljala Secondary School Portal
document.addEventListener('DOMContentLoaded', function () {

  // Initialize AOS (Animate on Scroll)
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      easing: 'ease-in-out',
      once: true,
      offset: 80
    });
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
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Global preloader dismissal
  window.dismissPreloader = function() {
    const preloader = document.getElementById('school-preloader');
    if (preloader && !preloader.classList.contains('fade-out')) {
      preloader.classList.add('fade-out');
      setTimeout(() => { preloader.style.display = 'none'; }, 600);
    }
  };

  // Preloader splash hide
  const preloader = document.getElementById('school-preloader');
  if (preloader) {
    setTimeout(window.dismissPreloader, 1500);
  }

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

  // Numbers counter animation
  const counters = document.querySelectorAll('.stat-number[data-count]');
  let counted = false;

  function runCounters() {
    if (counters.length === 0 || counted) return;
    const firstCounter = counters[0];
    const rect = firstCounter.getBoundingClientRect();
    if (rect.top <= window.innerHeight && rect.bottom >= 0) {
      counted = true;
      counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-count'), 10);
        let count = 0;
        const step = Math.ceil(target / 40);
        const timer = setInterval(() => {
          count += step;
          if (count >= target) {
            counter.textContent = target + (counter.getAttribute('data-suffix') || '');
            clearInterval(timer);
          } else {
            counter.textContent = count + (counter.getAttribute('data-suffix') || '');
          }
        }, 40);
      });
    }
  }

  window.addEventListener('scroll', runCounters);
  runCounters();
});
