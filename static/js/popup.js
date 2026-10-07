// Modern School Notice Popup Modal Handler
document.addEventListener('DOMContentLoaded', function() {
  const navigationEntries = performance.getEntriesByType('navigation');
  const isRefresh = navigationEntries.length > 0 && navigationEntries[0].type === 'reload';
  const closedKey = 'jaljala_school_popup_closed';
  const dismissedKey = 'jaljala_school_popup_dismissed_notices';

  // A deliberate browser refresh starts a fresh popup session, as before.
  if (isRefresh) {
    sessionStorage.removeItem(closedKey);
    sessionStorage.removeItem(dismissedKey);
  }

  const popupOverlay = document.getElementById('schoolNoticePopup');
  if (!popupOverlay) return;

  const closePopupBtn = document.getElementById('closePopupBtn');
  const closeAllBtn = document.getElementById('closeAllBtn');
  const prevNoticeBtn = document.getElementById('prevNoticeBtn');
  const nextNoticeBtn = document.getElementById('nextNoticeBtn');
  const currentNoticeIndexEl = document.getElementById('currentNoticeIndex');
  const totalNoticesEl = document.getElementById('totalNotices');
  const noticeImagesContainer = document.getElementById('noticeImagesContainer');
  const noticeWrappers = noticeImagesContainer
    ? Array.from(noticeImagesContainer.querySelectorAll('.school-notice-image-wrapper'))
    : [];

  if (!noticeWrappers.length) return;

  let dismissedIds = [];
  try {
    dismissedIds = JSON.parse(sessionStorage.getItem(dismissedKey) || '[]');
    if (!Array.isArray(dismissedIds)) dismissedIds = [];
  } catch (error) {
    dismissedIds = [];
  }

  const dismissedSet = new Set(dismissedIds.map(String));
  let remainingIndexes = noticeWrappers
    .map((wrapper, index) => ({ wrapper, index }))
    .filter(item => !dismissedSet.has(String(item.wrapper.dataset.noticeId)))
    .map(item => item.index);
  let currentNoticeIndex = remainingIndexes[0] ?? -1;

  if (sessionStorage.getItem(closedKey)) remainingIndexes = [];

  function openPopup() {
    popupOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closePopup(closeAll) {
    popupOverlay.classList.remove('active');
    document.body.style.overflow = '';
    if (closeAll) sessionStorage.setItem(closedKey, 'true');
  }

  function updateNavigation() {
    const position = remainingIndexes.indexOf(currentNoticeIndex);
    if (currentNoticeIndexEl && position !== -1) {
      currentNoticeIndexEl.textContent = position + 1;
    }
    if (totalNoticesEl) totalNoticesEl.textContent = remainingIndexes.length;

    if (prevNoticeBtn) {
      prevNoticeBtn.style.opacity = position <= 0 ? '0.3' : '1';
      prevNoticeBtn.style.pointerEvents = position <= 0 ? 'none' : 'auto';
    }
    if (nextNoticeBtn) {
      const atEnd = position === -1 || position >= remainingIndexes.length - 1;
      nextNoticeBtn.style.opacity = atEnd ? '0.3' : '1';
      nextNoticeBtn.style.pointerEvents = atEnd ? 'none' : 'auto';
    }
  }

  function showNotice(index) {
    if (!remainingIndexes.includes(index)) return;
    noticeWrappers.forEach(wrapper => { wrapper.style.display = 'none'; });
    noticeWrappers[index].style.display = 'flex';
    currentNoticeIndex = index;
    updateNavigation();
  }

  function dismissCurrentNotice() {
    if (currentNoticeIndex < 0) return;

    const dismissedPosition = remainingIndexes.indexOf(currentNoticeIndex);
    const noticeId = String(noticeWrappers[currentNoticeIndex].dataset.noticeId);
    dismissedSet.add(noticeId);
    sessionStorage.setItem(dismissedKey, JSON.stringify(Array.from(dismissedSet)));
    remainingIndexes = remainingIndexes.filter(index => index !== currentNoticeIndex);

    if (!remainingIndexes.length) {
      currentNoticeIndex = -1;
      closePopup(false);
      return;
    }

    const nextPosition = Math.min(dismissedPosition, remainingIndexes.length - 1);
    showNotice(remainingIndexes[nextPosition]);
  }

  if (remainingIndexes.length) {
    showNotice(currentNoticeIndex);
    setTimeout(openPopup, 800);
  }

  // The X dismisses only the notice currently on screen.
  if (closePopupBtn) closePopupBtn.addEventListener('click', dismissCurrentNotice);

  // Keep the explicit Close All action for users who want to dismiss the set.
  if (closeAllBtn) closeAllBtn.addEventListener('click', () => closePopup(true));

  // Outside click and Escape dismiss the current notice, just like the X.
  popupOverlay.addEventListener('click', function(event) {
    if (event.target === popupOverlay) dismissCurrentNotice();
  });

  document.addEventListener('keydown', function(event) {
    if (!popupOverlay.classList.contains('active')) return;

    if (event.key === 'Escape') {
      dismissCurrentNotice();
      return;
    }

    const position = remainingIndexes.indexOf(currentNoticeIndex);
    if (event.key === 'ArrowLeft' && position > 0) {
      showNotice(remainingIndexes[position - 1]);
    } else if (event.key === 'ArrowRight' && position < remainingIndexes.length - 1) {
      showNotice(remainingIndexes[position + 1]);
    }
  });

  if (prevNoticeBtn) {
    prevNoticeBtn.addEventListener('click', function() {
      const position = remainingIndexes.indexOf(currentNoticeIndex);
      if (position > 0) showNotice(remainingIndexes[position - 1]);
    });
  }

  if (nextNoticeBtn) {
    nextNoticeBtn.addEventListener('click', function() {
      const position = remainingIndexes.indexOf(currentNoticeIndex);
      if (position >= 0 && position < remainingIndexes.length - 1) {
        showNotice(remainingIndexes[position + 1]);
      }
    });
  }
});
