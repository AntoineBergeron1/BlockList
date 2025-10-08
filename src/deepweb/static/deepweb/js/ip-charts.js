/**
 * IP Address Report Charts - Chart.js Integration
 * Handles dynamic chart rendering with view switching (Timeline, Threat Types, Top Users)
 */

class IPChartManager {
  constructor(ipAddress) {
    this.ipAddress = ipAddress;
    this.chart = null;
    this.chartData = null;
    this.currentView = 'timeline';
    this.canvas = document.getElementById('ip-chart');
    this.loadingEl = document.getElementById('chart-loading');
    this.errorEl = document.getElementById('chart-error');

    this.init();
  }

  async init() {
    await this.loadChartData();
    if (this.chartData) {
      this.createChart();
      this.attachEventListeners();
    }
  }

  async loadChartData() {
    try {
      this.showLoading(true);
      const url = `/api/chart/${this.ipAddress}/`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      this.chartData = await response.json();
      this.showLoading(false);

      // Check if all datasets are empty
      if (this.isAllDataEmpty()) {
        this.showError('Aucune donnée disponible pour afficher les graphiques.');
        return;
      }
    } catch (error) {
      console.error('Failed to load chart data:', error);
      this.showError('Impossible de charger les données du graphique.');
      this.showLoading(false);
    }
  }

  isAllDataEmpty() {
    return (
      this.chartData.timeline.data.length === 0 &&
      this.chartData.threatTypes.data.length === 0 &&
      this.chartData.topUsers.data.length === 0
    );
  }

  createChart() {
    const ctx = this.canvas.getContext('2d');

    this.chart = new Chart(ctx, {
      type: 'line',
      data: this.getChartDataForView('timeline'),
      options: this.getChartOptions('timeline')
    });
  }

  getChartDataForView(view) {
    const colors = {
      timeline: 'rgb(220, 53, 69)',       // Bootstrap danger
      threatTypes: 'rgb(13, 110, 253)',   // Bootstrap primary
      topUsers: 'rgb(25, 135, 84)'        // Bootstrap success
    };

    switch (view) {
      case 'timeline':
        return {
          labels: this.chartData.timeline.labels,
          datasets: [{
            label: 'Signalements',
            data: this.chartData.timeline.data,
            borderColor: colors.timeline,
            backgroundColor: colors.timeline.replace('rgb', 'rgba').replace(')', ', 0.1)'),
            tension: 0.3,
            fill: true
          }]
        };

      case 'threatTypes':
        return {
          labels: this.chartData.threatTypes.labels,
          datasets: [{
            label: 'Types de menaces',
            data: this.chartData.threatTypes.data,
            backgroundColor: this.generateColors(this.chartData.threatTypes.labels.length),
            borderWidth: 1
          }]
        };

      case 'topUsers':
        return {
          labels: this.chartData.topUsers.labels,
          datasets: [{
            label: 'Signalements',
            data: this.chartData.topUsers.data,
            backgroundColor: colors.topUsers,
            borderWidth: 1
          }]
        };
    }
  }

  getChartOptions(view) {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 300
      },
      plugins: {
        legend: {
          display: view === 'threatTypes',
          position: 'bottom'
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: { size: 14 },
          bodyFont: { size: 13 }
        }
      }
    };

    if (view === 'timeline') {
      return {
        ...baseOptions,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              precision: 0
            }
          },
          x: {
            ticks: {
              maxRotation: 45,
              minRotation: 0
            }
          }
        }
      };
    } else if (view === 'topUsers') {
      return {
        ...baseOptions,
        indexAxis: 'y',
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              precision: 0
            }
          }
        }
      };
    }

    return baseOptions;
  }

  switchView(view) {
    if (view === this.currentView || !this.chart) return;

    this.currentView = view;

    // Update chart type based on view
    const chartType = view === 'threatTypes' ? 'doughnut' :
                      view === 'topUsers' ? 'bar' : 'line';

    this.chart.config.type = chartType;
    this.chart.data = this.getChartDataForView(view);
    this.chart.options = this.getChartOptions(view);
    this.chart.update('active');

    // Update active button state
    document.querySelectorAll('.chart-view-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
  }

  attachEventListeners() {
    document.querySelectorAll('.chart-view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = e.currentTarget.dataset.view;
        this.switchView(view);
      });
    });
  }

  generateColors(count) {
    const baseColors = [
      'rgba(220, 53, 69, 0.8)',   // Red
      'rgba(255, 193, 7, 0.8)',   // Yellow
      'rgba(13, 110, 253, 0.8)',  // Blue
      'rgba(25, 135, 84, 0.8)',   // Green
      'rgba(108, 117, 125, 0.8)', // Gray
      'rgba(111, 66, 193, 0.8)',  // Purple
      'rgba(13, 202, 240, 0.8)',  // Cyan
      'rgba(253, 126, 20, 0.8)'   // Orange
    ];

    const colors = [];
    for (let i = 0; i < count; i++) {
      colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
  }

  showLoading(show) {
    if (this.loadingEl) {
      this.loadingEl.style.display = show ? 'flex' : 'none';
    }
    if (this.canvas) {
      this.canvas.style.display = show ? 'none' : 'block';
    }
  }

  showError(message) {
    if (this.errorEl) {
      this.errorEl.textContent = message;
      this.errorEl.style.display = 'block';
    }
    if (this.canvas) {
      this.canvas.style.display = 'none';
    }
  }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  const chartContainer = document.getElementById('chart-container');
  if (chartContainer) {
    const ipAddress = chartContainer.dataset.ipAddress;
    if (ipAddress) {
      new IPChartManager(ipAddress);
    }
  }
});
