document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('sidebar-toggle');
  var overlay = document.getElementById('sidebar-overlay');
  if (!toggle || !overlay) {
    return;
  }

  toggle.addEventListener('click', function () {
    document.body.classList.toggle('sidebar-open');
  });

  overlay.addEventListener('click', function () {
    document.body.classList.remove('sidebar-open');
  });
});
