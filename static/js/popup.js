// Modern School Notice Popup Modal Handler
document.addEventListener('DOMContentLoaded', function() {
  // Detect actual browser refresh/reload vs normal navigation
  const navigationEntries = performance.getEntriesByType('navigation');
  const isRefresh = navigationEntries.length > 0 && navigationEntries[0].type === 'reload';
  
  // Only clear session storage on actual browser refresh
  if (isRefresh) {
    sessionStorage.removeItem('jaljala_school_popup_closed');
  }
  
  const popupOverlay = document.getElementById('schoolNoticePopup');
  const closePopupBtn = document.getElementById('closePopupBtn');
  const closeAllBtn = document.getElementById('closeAllBtn');
  const prevNoticeBtn = document.getElementById('prevNoticeBtn');
  const nextNoticeBtn = document.getElementById('nextNoticeBtn');
  const currentNoticeIndexEl = document.getElementById('currentNoticeIndex');
  const totalNoticesEl = document.getElementById('totalNotices');
  const noticeImagesContainer = document.getElementById('noticeImagesContainer');
  
  // Check if popup exists and has notices
  if (!popupOverlay) return;
  
  // Get all notice wrappers
  const noticeWrappers = noticeImagesContainer ? 
    noticeImagesContainer.querySelectorAll('.school-notice-image-wrapper') : [];
  
  const totalNotices = noticeWrappers.length;
  let currentNoticeIndex = 0;
  
  // Check if user already closed popup during current session
  const popupClosed = sessionStorage.getItem('jaljala_school_popup_closed');
  
  if (!popupClosed && totalNotices > 0) {
    // Show popup after a short delay
    setTimeout(function() {
      openPopup();
    }, 800);
  }
  
  // Open popup function
  function openPopup() {
    popupOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  }
  
  // Close popup function
  function closePopup() {
    popupOverlay.classList.remove('active');
    document.body.style.overflow = ''; // Restore scrolling
    
    // Store in sessionStorage that popup was closed
    sessionStorage.setItem('jaljala_school_popup_closed', 'true');
  }
  
  // Close button click handler
  if (closePopupBtn) {
    closePopupBtn.addEventListener('click', closePopup);
  }
  
  // Close All button click handler
  if (closeAllBtn) {
    closeAllBtn.addEventListener('click', closePopup);
  }
  
  // Close on overlay click (outside modal)
  popupOverlay.addEventListener('click', function(e) {
    if (e.target === popupOverlay) {
      closePopup();
    }
  });
  
  // Close on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && popupOverlay.classList.contains('active')) {
      closePopup();
    }
  });
  
  // Navigation functions (if multiple notices)
  function showNotice(index) {
    // Hide all notices
    noticeWrappers.forEach(function(wrapper) {
      wrapper.style.display = 'none';
    });
    
    // Show current notice
    if (noticeWrappers[index]) {
      noticeWrappers[index].style.display = 'flex';
    }
    
    // Update counter
    if (currentNoticeIndexEl) {
      currentNoticeIndexEl.textContent = index + 1;
    }
    
    // Update navigation button states
    if (prevNoticeBtn) {
      prevNoticeBtn.style.opacity = index === 0 ? '0.3' : '1';
      prevNoticeBtn.style.pointerEvents = index === 0 ? 'none' : 'auto';
    }
    
    if (nextNoticeBtn) {
      nextNoticeBtn.style.opacity = index === totalNotices - 1 ? '0.3' : '1';
      nextNoticeBtn.style.pointerEvents = index === totalNotices - 1 ? 'none' : 'auto';
    }
    
    currentNoticeIndex = index;
  }
  
  // Previous notice button
  if (prevNoticeBtn && totalNotices > 1) {
    prevNoticeBtn.addEventListener('click', function() {
      if (currentNoticeIndex > 0) {
        showNotice(currentNoticeIndex - 1);
      }
    });
  }
  
  // Next notice button
  if (nextNoticeBtn && totalNotices > 1) {
    nextNoticeBtn.addEventListener('click', function() {
      if (currentNoticeIndex < totalNotices - 1) {
        showNotice(currentNoticeIndex + 1);
      }
    });
  }
  
  // Keyboard navigation
  document.addEventListener('keydown', function(e) {
    if (!popupOverlay.classList.contains('active')) return;
    
    if (e.key === 'ArrowLeft' && totalNotices > 1) {
      if (currentNoticeIndex > 0) {
        showNotice(currentNoticeIndex - 1);
      }
    } else if (e.key === 'ArrowRight' && totalNotices > 1) {
      if (currentNoticeIndex < totalNotices - 1) {
        showNotice(currentNoticeIndex + 1);
      }
    }
  });
  
  // Initialize first notice
  if (totalNotices > 0) {
    showNotice(0);
  }
});