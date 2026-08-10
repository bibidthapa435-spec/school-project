// Hero Carousel Slider Handler
document.addEventListener('DOMContentLoaded', function() {
  const heroCarousel = document.querySelector('#heroCarousel');
  if (heroCarousel && typeof bootstrap !== 'undefined') {
    new bootstrap.Carousel(heroCarousel, {
      interval: 5000,
      ride: 'carousel',
      pause: 'hover'
    });
  }
});
