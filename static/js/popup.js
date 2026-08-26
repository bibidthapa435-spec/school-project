// Notice Popup Modal Handlern 
document.addEventListener('DOMContentLoaded', function() {
  const popupModalEl = document.getElementById('noticePopupModal');
  if (popupModalEl && typeof bootstrap !== 'undefined') {
    // Check if user already closed popup during current session
    const popupClosed = sessionStorage.getItem('jaljala_popup_closed');
    if (!popupClosed) {
      const popupModal = new bootstrap.Modal(popupModalEl);
      setTimeout(function() {
        popupModal.show();
      }, 1000);

      popupModalEl.addEventListener('hidden.bs.modal', function () {
        sessionStorage.setItem('jaljala_popup_closed', 'true');
      });
    }
  }
});
