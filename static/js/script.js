// Global JavaScript initialization for Shree Jaljala Secondary School
document.addEventListener('DOMContentLoaded', function() {
  console.log('Shree Jaljala Secondary School Portal Initialized');

  // Preloader splash dismissal
  const preloader = document.getElementById('school-preloader');
  if (preloader) {
    setTimeout(function() {
      preloader.classList.add('fade-out');
      setTimeout(function() {
        preloader.style.display = 'none';
      }, 600);
    }, 800);
  }

  // Sticky navbar scroll handler
  const navbar = document.querySelector('.main-navbar');
  if (navbar) {
    const handleScroll = function() {
      if (window.scrollY > 60) {
        navbar.classList.add('navbar-scrolled');
      } else {
        navbar.classList.remove('navbar-scrolled');
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial check
  }

  // Initialize AOS animation if loaded
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      once: true,
      easing: 'ease-in-out'
    });
  }

  // Auto hide alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});
