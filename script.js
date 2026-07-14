document.addEventListener("DOMContentLoaded", function () {

    const slides = document.querySelectorAll(".slide");

    let current = 0;

    function changeSlide() {
        slides[current].classList.remove("active");

        current = (current + 1) % slides.length;

        slides[current].classList.add("active");
    }

    setInterval(changeSlide, 10000);

});
window.addEventListener("scroll", function () {

    const navbar = document.getElementById("navbar-container");

    if (window.scrollY > 200) {
        navbar.classList.add("sticky");
    } else {
        navbar.classList.remove("sticky");
    }

});



/* login portal */


