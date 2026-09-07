document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initAnalyticsChart();
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
