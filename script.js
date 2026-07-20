document.addEventListener("DOMContentLoaded", function () {
    

    // Preloader / Splash Screen Logic
    const preloader = document.getElementById("school-preloader");
    if (preloader) {
        document.body.classList.add("preloader-active");
        
        // Timeout to simulate loading and show the beautiful splash screen brand
        setTimeout(function () {
            preloader.classList.add("fade-out");
            document.body.classList.remove("preloader-active");
        }, 1800);
    }

    // Dark Mode Functionality
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    const isDarkMode = localStorage.getItem("darkMode") === "enabled";

    function enableDarkMode() {
        document.body.classList.add("dark-mode");
        document.documentElement.classList.add("dark-mode");
        localStorage.setItem("darkMode", "enabled");
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
        }
    }

    function disableDarkMode() {
        document.body.classList.remove("dark-mode");
        document.documentElement.classList.remove("dark-mode");
        localStorage.setItem("darkMode", "disabled");
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
        }
    }

    if (isDarkMode) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener("click", function () {
            if (document.body.classList.contains("dark-mode")) {
                disableDarkMode();
            } else {
                enableDarkMode();
            }
        });
    }

    // Home link refresh logic
    const homeLink = document.getElementById("home-link");
    if (homeLink) {
        homeLink.addEventListener("click", function (e) {
            e.preventDefault();
            window.location.reload();
        });
    }

    const slides = document.querySelectorAll(".slide");

    let current = 0;

    if (slides.length > 0) {
        function changeSlide() {
            slides[current].classList.remove("active");

            current = (current + 1) % slides.length;

            slides[current].classList.add("active");
        }

        setInterval(changeSlide, 10000);
    }

    // Mobile Navbar Toggle Logic
    const navToggle = document.getElementById("nav-toggle");
    const navMenu = document.getElementById("nav-menu");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", function (e) {
            e.stopPropagation();
            navMenu.classList.toggle("active");
            
            const icon = navToggle.querySelector("i");
            if (icon) {
                if (icon.classList.contains("fa-bars")) {
                    icon.classList.remove("fa-bars");
                    icon.classList.add("fa-xmark");
                } else {
                    icon.classList.remove("fa-xmark");
                    icon.classList.add("fa-bars");
                }
            }
        });

        // Close menu when clicking outside
        document.addEventListener("click", function (e) {
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                navMenu.classList.remove("active");
                const icon = navToggle.querySelector("i");
                if (icon) {
                    icon.classList.remove("fa-xmark");
                    icon.classList.add("fa-bars");
                }
                document.querySelectorAll(".dropdown").forEach(function (dropdown) {
                    dropdown.classList.remove("active");
                });
            }
        });
    }

    // Mobile Dropdown Click Logic
    const dropdowns = document.querySelectorAll(".dropdown");
    dropdowns.forEach(function (dropdown) {
        const trigger = dropdown.querySelector("a");
        if (trigger) {
            trigger.addEventListener("click", function (e) {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Close other dropdowns
                    dropdowns.forEach(function (other) {
                        if (other !== dropdown) {
                            other.classList.remove("active");
                        }
                    });
                    
                    dropdown.classList.toggle("active");
                }
            });
        }
    });

    // About Section Tabs Switcher & Modal Overlay Controls
    const tabBtns = document.querySelectorAll(".about-tab-btn");
    const tabContents = document.querySelectorAll(".about-tab-content");
    const aboutSection = document.getElementById("about-section");
    const aboutModalClose = document.getElementById("about-modal-close");

    function switchTab(tabId) {
        tabBtns.forEach(btn => {
            if (btn.getAttribute("data-tab") === tabId) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        tabContents.forEach(content => {
            if (content.id === tabId) {
                content.classList.add("active");
            } else {
                content.classList.remove("active");
            }
        });
    }

    function openAboutModal(tabId) {
        if (aboutSection) {
            if (tabId) {
                switchTab(tabId);
            }
            aboutSection.classList.add("show");
            document.body.style.overflow = "hidden"; // Prevent main page scrolling
        }
    }

    function closeAboutModal() {
        if (aboutSection) {
            aboutSection.classList.remove("show");
            document.body.style.overflow = ""; // Restore main page scrolling
        }
    }

    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener("click", function () {
                const tabId = this.getAttribute("data-tab");
                switchTab(tabId);
            });
        });
    }

    // Close buttons logic
    if (aboutModalClose) {
        aboutModalClose.addEventListener("click", closeAboutModal);
    }

    // Click outside to close (backdrop handler)
    if (aboutSection) {
        aboutSection.addEventListener("click", function (e) {
            if (e.target === aboutSection) {
                closeAboutModal();
            }
        });
    }

    // Intercept dropdown links to open modal and switch tabs
    const aboutLinks = document.querySelectorAll("a[data-target-tab]");
    aboutLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const targetTab = this.getAttribute("data-target-tab");
            if (targetTab) {
                openAboutModal(targetTab);
                
                // On mobile, close navbar menu
                if (window.innerWidth <= 768 && navMenu) {
                    navMenu.classList.remove("active");
                    const icon = navToggle?.querySelector("i");
                    if (icon) {
                        icon.classList.remove("fa-xmark");
                        icon.classList.add("fa-bars");
                    }
                }
            }
        });
    });

    // Parent link click logic for desktop (opens introduction modal)
    const aboutParentLink = document.querySelector(".about-us-parent-link");
    if (aboutParentLink) {
        aboutParentLink.addEventListener("click", function (e) {
            if (window.innerWidth > 768) {
                e.preventDefault();
                openAboutModal("introduction");
            }
        });
    }

    // Reset layout on window resize
    window.addEventListener("resize", function () {
        if (window.innerWidth > 768) {
            if (navMenu) {
                navMenu.classList.remove("active");
            }
            if (navToggle) {
                const icon = navToggle.querySelector("i");
                if (icon) {
                    icon.classList.remove("fa-xmark");
                    icon.classList.add("fa-bars");
                }
            }
            dropdowns.forEach(function (dropdown) {
                dropdown.classList.remove("active");
            });
        }
    });


    // ==========================================================
    // SCHOOL MEDIA GALLERY LOGIC
    // ==========================================================
    const mediaPhotosBtn = document.getElementById("media-photos-btn");
    const mediaVideosBtn = document.getElementById("media-videos-btn");
    const photoPanel = document.getElementById("photo-gallery-panel");
    const videoPanel = document.getElementById("video-gallery-panel");

    function setActivePanel(panelType) {
        if (panelType === "photos") {
            mediaPhotosBtn?.classList.add("active");
            mediaVideosBtn?.classList.remove("active");
            photoPanel?.classList.add("active");
            videoPanel?.classList.remove("active");
        } else if (panelType === "videos") {
            mediaPhotosBtn?.classList.remove("active");
            mediaVideosBtn?.classList.add("active");
            photoPanel?.classList.remove("active");
            videoPanel?.classList.add("active");
        }
    }

    if (mediaPhotosBtn) {
        mediaPhotosBtn.addEventListener("click", () => setActivePanel("photos"));
    }
    if (mediaVideosBtn) {
        mediaVideosBtn.addEventListener("click", () => setActivePanel("videos"));
    }

    // Category Filter Logic
    const filterBtns = document.querySelectorAll(".filter-btn");
    const galleryItems = document.querySelectorAll(".gallery-item");

    filterBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            // Remove active from all filter buttons
            filterBtns.forEach(b => b.classList.remove("active"));
            this.classList.add("active");

            const filterValue = this.getAttribute("data-filter");

            galleryItems.forEach(item => {
                const category = item.getAttribute("data-category");
                if (filterValue === "all" || category === filterValue) {
                    item.classList.remove("hidden");
                } else {
                    item.classList.add("hidden");
                }
            });
        });
    });

    // Lightbox Functionality
    const lightbox = document.getElementById("gallery-lightbox");
    const lightboxImg = document.getElementById("lightbox-img");
    const lightboxCaption = document.getElementById("lightbox-caption");
    const lightboxClose = document.getElementById("lightbox-close");
    const lightboxPrev = document.getElementById("lightbox-prev");
    const lightboxNext = document.getElementById("lightbox-next");

    let currentFilteredCards = [];
    let currentLightboxIndex = 0;

    function getVisibleImageCards() {
        // Return only visible cards (not hidden by category filter) and not placeholders
        return Array.from(document.querySelectorAll(".gallery-card-inner")).filter(card => {
            const item = card.closest(".gallery-item");
            const isHidden = item ? item.classList.contains("hidden") : false;
            const isPlaceholder = card.getAttribute("data-is-placeholder") === "true";
            return !isHidden && !isPlaceholder;
        });
    }

    function openLightbox(index) {
        currentFilteredCards = getVisibleImageCards();
        if (currentFilteredCards.length === 0) return;

        currentLightboxIndex = index;
        const card = currentFilteredCards[currentLightboxIndex];
        const src = card.getAttribute("data-src");
        const caption = card.getAttribute("data-caption");

        if (lightboxImg) lightboxImg.src = src;
        if (lightboxCaption) lightboxCaption.textContent = caption;

        lightbox?.classList.add("show");
        document.body.style.overflow = "hidden"; // Lock page scroll
    }

    function closeLightbox() {
        lightbox?.classList.remove("show");
        document.body.style.overflow = ""; // Unlock scroll
        if (lightboxImg) lightboxImg.src = "";
    }

    function slideLightbox(direction) {
        if (currentFilteredCards.length === 0) return;

        if (direction === "next") {
            currentLightboxIndex = (currentLightboxIndex + 1) % currentFilteredCards.length;
        } else if (direction === "prev") {
            currentLightboxIndex = (currentLightboxIndex - 1 + currentFilteredCards.length) % currentFilteredCards.length;
        }

        const card = currentFilteredCards[currentLightboxIndex];
        const src = card.getAttribute("data-src");
        const caption = card.getAttribute("data-caption");

        if (lightboxImg) lightboxImg.src = src;
        if (lightboxCaption) lightboxCaption.textContent = caption;
    }

    // Attach click events to actual gallery images
    document.querySelectorAll(".gallery-card-inner").forEach(card => {
        card.addEventListener("click", function (e) {
            // Placeholders shouldn't trigger full lightbox
            if (this.getAttribute("data-is-placeholder") === "true") return;

            currentFilteredCards = getVisibleImageCards();
            const index = currentFilteredCards.indexOf(this);
            if (index !== -1) {
                openLightbox(index);
            }
        });
    });

    lightboxClose?.addEventListener("click", closeLightbox);
    lightboxPrev?.addEventListener("click", () => slideLightbox("prev"));
    lightboxNext?.addEventListener("click", () => slideLightbox("next"));

    // Close lightbox on click outside the image
    lightbox?.addEventListener("click", function (e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    // Keyboard controls for Lightbox
    document.addEventListener("keydown", function (e) {
        if (lightbox && lightbox.classList.contains("show")) {
            if (e.key === "Escape") {
                closeLightbox();
            } else if (e.key === "ArrowRight") {
                slideLightbox("next");
            } else if (e.key === "ArrowLeft") {
                slideLightbox("prev");
            }
        }
    });

    // Video Player Modal Functionality
    const videoModal = document.getElementById("video-modal");
    const videoIframe = document.getElementById("video-player-iframe");
    const videoModalTitle = document.getElementById("video-modal-title");
    const videoModalClose = document.getElementById("video-modal-close");

    function openVideoModal(videoId, title) {
        if (videoIframe) {
            videoIframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
        }
        if (videoModalTitle) {
            videoModalTitle.textContent = title;
        }
        videoModal?.classList.add("show");
        document.body.style.overflow = "hidden";
    }

    function closeVideoModal() {
        videoModal?.classList.remove("show");
        document.body.style.overflow = "";
        if (videoIframe) {
            videoIframe.src = ""; // Clear iframe to stop video playing
        }
    }

    // Bind play click on video cards
    document.querySelectorAll(".video-card").forEach(card => {
        const thumb = card.querySelector(".video-thumbnail-wrapper");
        const watchBtn = card.querySelector(".watch-video-btn");
        const videoId = card.getAttribute("data-video-id");
        const title = card.getAttribute("data-title");

        const triggerOpen = () => {
            if (videoId) {
                openVideoModal(videoId, title || "School Highlight Video");
            }
        };

        thumb?.addEventListener("click", triggerOpen);
        watchBtn?.addEventListener("click", triggerOpen);
    });

    videoModalClose?.addEventListener("click", closeVideoModal);
    videoModal?.addEventListener("click", function (e) {
        if (e.target === videoModal) {
            closeVideoModal();
        }
    });

    // Keyboard ESC to close video player
    document.addEventListener("keydown", function (e) {
        if (videoModal && videoModal.classList.contains("show")) {
            if (e.key === "Escape") {
                closeVideoModal();
            }
        }
    });

    // Top Navigation gallery item quick action bindings
    const navImageBtn = document.getElementById("nav-image-gallery");
    const navVideoBtn = document.getElementById("nav-video-gallery");
    const galleryParentBtn = document.querySelector(".gallery-parent-link");
    const footerGalleryBtn = document.getElementById("footer-gallery-link");
    const gallerySection = document.getElementById("gallery-section");
    const galleryModalClose = document.getElementById("gallery-modal-close");

    function handleNavGalleryClick(panelType) {
        setActivePanel(panelType);
        
        // Show gallery modal directly without scrolling or jumping the main page
        if (gallerySection) {
            gallerySection.classList.add("show");
            document.body.style.overflow = "hidden"; // Lock page scroll
        }

        // Close mobile nav menu
        if (window.innerWidth <= 768 && navMenu) {
            navMenu.classList.remove("active");
            const icon = navToggle?.querySelector("i");
            if (icon) {
                icon.classList.remove("fa-xmark");
                icon.classList.add("fa-bars");
            }
        }
    }

    function closeGalleryModal() {
        if (gallerySection) {
            gallerySection.classList.remove("show");
            document.body.style.overflow = ""; // Restore page scroll
        }
    }

    navImageBtn?.addEventListener("click", function (e) {
        e.preventDefault();
        handleNavGalleryClick("photos");
    });

    navVideoBtn?.addEventListener("click", function (e) {
        e.preventDefault();
        handleNavGalleryClick("videos");
    });

    galleryParentBtn?.addEventListener("click", function (e) {
        e.preventDefault();
        handleNavGalleryClick("photos");
    });

    footerGalleryBtn?.addEventListener("click", function (e) {
        e.preventDefault();
        handleNavGalleryClick("photos");
    });

    galleryModalClose?.addEventListener("click", closeGalleryModal);

    // ESC key to close Gallery Modal
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeGalleryModal();
        }
    });


    // ==========================================================
    // SCROLL REVEAL ANIMATIONS (INTERSECTION OBSERVER)
    // ==========================================================
    // Dynamically assign reveal classes and responsive staggered delays to gallery items
    const allGalleryItems = document.querySelectorAll(".gallery-item");
    allGalleryItems.forEach((item, index) => {
        item.classList.add("reveal-fade-in");
        // Stagger in groups of 4 columns
        const delayClass = `stagger-delay-${(index % 4) + 1}`;
        item.classList.add(delayClass);
    });

    const revealElements = document.querySelectorAll(
        ".reveal-fade-in, .reveal-fade-up, .reveal-slide-left, .reveal-slide-right"
    );

    if ("IntersectionObserver" in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("active-reveal");
                    // Once animated, unobserve to freeze it in active state
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.01, // highly responsive trigger threshold
            rootMargin: "0px 0px -60px 0px" // triggers when element is 60px above the viewport bottom for maximum visibility
        });

        revealElements.forEach(el => revealObserver.observe(el));
    } else {
        // Fallback for browsers that do not support IntersectionObserver
        revealElements.forEach(el => el.classList.add("active-reveal"));
    }


});
window.addEventListener("scroll", function () {

    const navbar = document.getElementById("navbar-container");

    if (window.scrollY > 200) {
        navbar.classList.add("sticky");
    } else {
        navbar.classList.remove("sticky");
    }

});


document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("noticeModal");
  const closeBtn = document.getElementById("closeNotice");

  const notices = [
    {
      title: "भर्ना सम्बन्धी सूचना",
      text: "शैक्षिक सत्र २०८३ का लागि नयाँ विद्यार्थी भर्ना तथा प्रवेश परीक्षाको आवेदन खुला गरिएको छ।",
      image: "schoolnotices.png"
    },
    {
      title: "परीक्षा सम्बन्धी सूचना",
      text: "कक्षा ११ को प्रथम त्रैमासिक परीक्षा साउन २५ गतेदेखि सञ्चालन हुनेछ।",
      image: "examnotice.png"
    }
  ];

  let current = 0;

  const title = document.getElementById("noticeTitle");
  const text = document.getElementById("noticeText");
  const image = document.getElementById("noticeImage");
  const count = document.getElementById("noticeCount");

  function showNotice(index) {
    if (title) title.innerHTML = notices[index].title;
    if (text) text.innerHTML = notices[index].text;
    if (image) image.src = notices[index].image;
    if (count) count.innerHTML = `${index + 1} / ${notices.length}`;
  }

  if (title && text && image && count) {
    showNotice(current);
  }

  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");

  if (nextBtn) {
    nextBtn.onclick = () => {
      current++;
      if (current >= notices.length) current = 0;
      showNotice(current);
    };
  }

  if (prevBtn) {
    prevBtn.onclick = () => {
      current--;
      if (current < 0) current = notices.length - 1;
      showNotice(current);
    };
  }

  // Show the modal slightly after the page loads for a smoother transition
  setTimeout(() => {
    if (modal) modal.classList.add("active");
  }, 500);

  // Close modal when clicking the 'X' button
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      if (modal) modal.classList.remove("active");
    });
  }

  // Close modal when clicking anywhere outside the white modal box
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.remove("active");
      }
    });
  }
});



