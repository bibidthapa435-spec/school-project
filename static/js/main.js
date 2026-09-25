// Main JavaScript for Jaljala Secondary School Portal
document.addEventListener('DOMContentLoaded', function () {

  // Initialize AOS (Animate on Scroll) — removed per redesign brief
  // (one deliberate hero moment only; no fade-in-on-scroll).
  
  // Back to top button

    // Sticky Navbar - becomes fixed when scrolled past, always stays visible
    const navbar = document.querySelector('#mainNav') || document.querySelector('nav.navbar-custom') || document.querySelector('.navbar-custom');
    const topBar = document.querySelector('.top-bar');
    const brandHeader = document.querySelector('.brand-header');

    if (navbar) {
      // Store the navbar's original height for body padding (prevents layout jump)
      const navbarHeight = navbar.offsetHeight;
      document.documentElement.style.setProperty('--navbar-height', navbarHeight + 'px');

      let isSticky = false;
      let ticking = false;

      // Calculate the scroll threshold (top bar + brand header height)
      const getScrollThreshold = () => {
        const topBarHeight = topBar ? topBar.offsetHeight : 0;
        const brandHeight = brandHeader ? brandHeader.offsetHeight : 0;
        return topBarHeight + brandHeight;
      };

      // Activate sticky mode - navbar becomes fixed at top with animation
      const activateSticky = () => {
        if (isSticky) return;
        isSticky = true;
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

      // Scroll handler - simple threshold check, no direction detection
      const handleScroll = () => {
        const currentScrollY = window.scrollY;
        const threshold = getScrollThreshold();

        if (currentScrollY > threshold) {
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

      // Handle resize to update navbar height
      window.addEventListener('resize', function () {
        if (isSticky) {
          const newHeight = navbar.offsetHeight;
          document.documentElement.style.setProperty('--navbar-height', newHeight + 'px');
        }
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

  // Preloader splash: show on first load and when the Home link is clicked
  const preloader = document.getElementById('school-preloader');
  if (preloader) {
    const shouldShowPreloader = sessionStorage.getItem('show-preloader') === '1' || !sessionStorage.getItem('preloader-seen');
    if (shouldShowPreloader) {
      preloader.style.display = 'flex';
      preloader.classList.add('visible');
      preloader.classList.remove('fade-out');
      sessionStorage.setItem('preloader-seen', '1');
      sessionStorage.removeItem('show-preloader');
      setTimeout(() => {
        preloader.classList.add('fade-out');
        preloader.classList.remove('visible');
        setTimeout(() => { preloader.style.display = 'none'; }, 650);
      }, 1850);
    } else {
      preloader.style.display = 'none';
    }
  }

  document.querySelectorAll('a[href="/"]').forEach(link => {
    link.addEventListener('click', function () {
      sessionStorage.setItem('show-preloader', '1');
    });
  });

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
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

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
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
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
