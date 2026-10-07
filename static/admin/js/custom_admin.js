document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initAnalyticsChart();
  initThemeToggle();
  initNotificationCenter();
  initGlobalSearch();
  initAnimations();
});

function initSidebar() {
  var toggle = document.getElementById('sidebar-toggle');
  var overlay = document.getElementById('sidebar-overlay');
  if (!toggle || !overlay) {
    return;
  }

  function setOpen(isOpen) {
    document.body.classList.toggle('sidebar-open', isOpen);
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    overlay.hidden = !isOpen;
  }

  toggle.addEventListener('click', function () {
    setOpen(!document.body.classList.contains('sidebar-open'));
  });

  overlay.addEventListener('click', function () {
    setOpen(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      setOpen(false);
    }
  });
}

function initAnalyticsChart() {
  var canvas = document.getElementById('visitors-chart');
  if (!canvas || typeof Chart === 'undefined') {
    return;
  }

  var periodSelect = document.getElementById('analytics-period');

  // Get chart data from the json_script output
  var chartDataEl = document.getElementById('chart-data');
  var datasets = {};

  try {
    datasets = chartDataEl ? JSON.parse(chartDataEl.textContent) : { month: { labels: [], visitors: [], page_views: [] } };
  } catch (e) {
    // Fallback to empty data
    datasets = {
      month: { labels: [], visitors: [], page_views: [] },
      week: { labels: [], visitors: [], page_views: [] },
      year: { labels: [], visitors: [], page_views: [] },
    };
  }

  // Ensure datasets has the required structure
  if (!datasets.month) datasets.month = { labels: [], visitors: [], page_views: [] };
  if (!datasets.week) datasets.week = { labels: [], visitors: [], page_views: [] };
  if (!datasets.year) datasets.year = { labels: [], visitors: [], page_views: [] };

  var chart = new Chart(canvas, {
    type: 'line',
    data: buildChartData(datasets.month),
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            padding: 16,
            font: { family: 'Inter, sans-serif', size: 12 },
          },
        },
        tooltip: {
          backgroundColor: '#0f2847',
          titleFont: { family: 'Inter, sans-serif' },
          bodyFont: { family: 'Inter, sans-serif' },
          padding: 12,
          cornerRadius: 8,
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: '#64748b',
            font: { family: 'Inter, sans-serif', size: 11 },
          },
        },
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(15, 40, 71, 0.06)' },
          ticks: {
            color: '#64748b',
            font: { family: 'Inter, sans-serif', size: 11 },
          },
        },
      },
    },
  });

  if (periodSelect) {
    periodSelect.addEventListener('change', function () {
      var selected = datasets[periodSelect.value] || datasets.month;
      chart.data = buildChartData(selected);
      chart.update();
    });
  }
}

function buildChartData(periodData) {
  return {
    labels: periodData.labels,
    datasets: [
      {
        label: 'Visitors',
        data: periodData.visitors,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.08)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointBackgroundColor: '#2563eb',
      },
      {
        label: 'Page Views',
        data: periodData.page_views || periodData.pageViews || [],
        borderColor: '#7dd3fc',
        backgroundColor: 'rgba(125, 211, 252, 0.08)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointBackgroundColor: '#7dd3fc',
      },
    ],
  };
}

/* Theme Toggle */
function initThemeToggle() {
  var toggle = document.getElementById('themeToggle');
  if (!toggle) return;

  var lightBtn = toggle.querySelector('.theme-light');
  var darkBtn = toggle.querySelector('.theme-dark');
  var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  var currentTheme = localStorage.getItem('sjss-theme') || (prefersDark ? 'dark' : 'light');

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.style.colorScheme = theme;
    localStorage.setItem('sjss-theme', theme);

    if (lightBtn && darkBtn) {
      if (theme === 'dark') {
        lightBtn.classList.remove('active');
        darkBtn.classList.add('active');
      } else {
        lightBtn.classList.add('active');
        darkBtn.classList.remove('active');
      }
    }
  }

  // Initialize theme
  setTheme(currentTheme);

  if (lightBtn) {
    lightBtn.addEventListener('click', function() {
      setTheme('light');
    });
  }

  if (darkBtn) {
    darkBtn.addEventListener('click', function() {
      setTheme('dark');
    });
  }
}

/* Notification Center */
function initNotificationCenter() {
  var notificationBtn = document.getElementById('notificationBtn');
  var notificationDropdown = document.getElementById('notificationDropdown');
  
  if (!notificationBtn || !notificationDropdown) return;

  notificationBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    notificationDropdown.classList.toggle('show');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', function(e) {
    if (!notificationDropdown.contains(e.target) && !notificationBtn.contains(e.target)) {
      notificationDropdown.classList.remove('show');
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      notificationDropdown.classList.remove('show');
    }
  });

  // Mark as read on click
  var notificationItems = notificationDropdown.querySelectorAll('.notification-item');
  notificationItems.forEach(function(item) {
    item.addEventListener('click', function() {
      this.classList.remove('unread');
      updateNotificationBadge();
    });
  });
}

function updateNotificationBadge() {
  var badge = document.querySelector('.notification-badge');
  if (!badge) return;
  
  var unreadCount = document.querySelectorAll('.notification-item.unread').length;
  badge.textContent = unreadCount;
  
  if (unreadCount === 0) {
    badge.style.display = 'none';
  } else {
    badge.style.display = 'flex';
  }
}

/* Global Search */
function initGlobalSearch() {
  var searchInput = document.getElementById('globalSearch');
  if (!searchInput) return;

  var shortcut = document.querySelector('.global-search-shortcut');
  
  // Focus search on Ctrl+K or Cmd+K
  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
    
    // Close on Escape
    if (e.key === 'Escape') {
      searchInput.blur();
    }
  });

  // Show/hide shortcut hint
  searchInput.addEventListener('focus', function() {
    if (shortcut) shortcut.style.display = 'none';
  });

  searchInput.addEventListener('blur', function() {
    if (shortcut && this.value === '') {
      shortcut.style.display = 'block';
    }
  });
}

/* Animations */
function initAnimations() {
  // Animate stat cards on scroll
  var statCards = document.querySelectorAll('.stat-card-enhanced');
  
  var observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry, index) {
      if (entry.isIntersecting) {
        var delay = index * 100;
        setTimeout(function() {
          entry.target.classList.add('animate-fade-in-up');
        }, delay);
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  statCards.forEach(function(card) {
    observer.observe(card);
  });

  // Animate progress bars
  var progressBars = document.querySelectorAll('.stat-card-progress-bar');
  progressBars.forEach(function(bar) {
    var width = bar.getAttribute('data-width') || '100';
    setTimeout(function() {
      bar.style.width = width + '%';
    }, 500);
  });
}

/* Chart filter buttons */
function initChartFilters() {
  var filterBtns = document.querySelectorAll('.chart-filter-btn');
  filterBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      filterBtns.forEach(function(b) {
        b.classList.remove('active');
      });
      this.classList.add('active');
    });
  });
}

// Initialize chart filters if they exist
if (document.querySelector('.chart-filter-btn')) {
  initChartFilters();
}
