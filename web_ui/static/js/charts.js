/**
 * Charts JavaScript - Handles the creation and updating of charts
 */

// Charts for the performance page
let profitChart, winRateChart, tradeCountChart, drawdownChart;

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initializeProfitChart();
    initializeWinRateChart();
    initializeTradeCountChart();
    initializeDrawdownChart();
    
    // Setup filter handlers
    setupFilterHandlers();
    
    // Initial data load
    refreshCharts();
});

function setupFilterHandlers() {
    // Pair filter change
    const pairFilter = document.getElementById('pairFilter');
    if (pairFilter) {
        pairFilter.addEventListener('change', refreshCharts);
    }
    
    // Timeframe filter change
    const timeframeFilter = document.getElementById('timeframeFilter');
    if (timeframeFilter) {
        timeframeFilter.addEventListener('change', refreshCharts);
    }
    
    // Model filter change
    const modelFilter = document.getElementById('modelFilter');
    if (modelFilter) {
        modelFilter.addEventListener('change', refreshCharts);
    }
    
    // Time period filter change
    const periodFilter = document.getElementById('periodFilter');
    if (periodFilter) {
        periodFilter.addEventListener('change', refreshCharts);
    }
    
    // Refresh button
    const refreshButton = document.getElementById('refreshCharts');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshCharts);
    }
}

function refreshCharts() {
    // Get filter values
    const pairFilter = document.getElementById('pairFilter');
    const timeframeFilter = document.getElementById('timeframeFilter');
    const modelFilter = document.getElementById('modelFilter');
    const periodFilter = document.getElementById('periodFilter');
    
    const pair = pairFilter ? pairFilter.value : '';
    const timeframe = timeframeFilter ? timeframeFilter.value : '';
    const modelId = modelFilter ? modelFilter.value : '';
    const days = periodFilter ? parseInt(periodFilter.value) : 30;
    
    // Show loading message
    showAlert('info', 'Loading performance data...');
    
    // Fetch metrics based on filters
    fetchFilteredMetrics(pair, timeframe, modelId, days);
}

function fetchFilteredMetrics(pair, timeframe, modelId, days) {
    // Build query string
    let queryParams = new URLSearchParams();
    if (pair) queryParams.append('pair', pair);
    if (timeframe) queryParams.append('timeframe', timeframe);
    if (modelId) queryParams.append('model_id', modelId);
    if (days) queryParams.append('days', days);
    
    // Fetch filtered metrics
    fetch(`/api/trading_metrics?${queryParams.toString()}`)
        .then(response => response.json())
        .then(metrics => {
            // Update charts with the metrics data
            updateProfitChart(metrics);
            updateWinRateChart(metrics);
            updateTradeCountChart(metrics);
            updateDrawdownChart(metrics);
            
            // Update summary statistics
            updateSummaryStats(metrics);
            
            // Hide loading message
            const alertsContainer = document.getElementById('alertsContainer');
            if (alertsContainer) {
                alertsContainer.innerHTML = '';
            }
            showAlert('success', 'Performance data updated');
        })
        .catch(error => {
            console.error('Error fetching metrics:', error);
            showAlert('danger', 'Failed to load performance data');
        });
}

function initializeProfitChart() {
    const ctx = document.getElementById('profitChart');
    if (!ctx) return;
    
    profitChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Profit %',
                data: [],
                borderWidth: 2,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function updateProfitChart(metrics) {
    if (!profitChart) return;
    
    // Sort metrics by date
    metrics.sort((a, b) => new Date(a.end_date) - new Date(b.end_date));
    
    // Extract data for chart
    const labels = metrics.map(m => {
        const date = new Date(m.end_date);
        return date.toLocaleDateString();
    });
    
    const profits = metrics.map(m => m.profit_percent);
    
    // Update chart data
    profitChart.data.labels = labels;
    profitChart.data.datasets[0].data = profits;
    profitChart.update();
}

function initializeWinRateChart() {
    const ctx = document.getElementById('winRateChart');
    if (!ctx) return;
    
    winRateChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Win Rate %',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function updateWinRateChart(metrics) {
    if (!winRateChart) return;
    
    // Sort metrics by date
    metrics.sort((a, b) => new Date(a.end_date) - new Date(b.end_date));
    
    // Extract data for chart
    const labels = metrics.map(m => {
        const date = new Date(m.end_date);
        return date.toLocaleDateString();
    });
    
    const winRates = metrics.map(m => m.win_rate);
    
    // Update chart data
    winRateChart.data.labels = labels;
    winRateChart.data.datasets[0].data = winRates;
    winRateChart.update();
}

function initializeTradeCountChart() {
    const ctx = document.getElementById('tradeCountChart');
    if (!ctx) return;
    
    tradeCountChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Win Trades',
                    data: [],
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Loss Trades',
                    data: [],
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: true
                },
                x: {
                    stacked: true
                }
            }
        }
    });
}

function updateTradeCountChart(metrics) {
    if (!tradeCountChart) return;
    
    // Sort metrics by date
    metrics.sort((a, b) => new Date(a.end_date) - new Date(b.end_date));
    
    // Extract data for chart
    const labels = metrics.map(m => {
        const date = new Date(m.end_date);
        return date.toLocaleDateString();
    });
    
    const winTrades = metrics.map(m => m.win_trades);
    const lossTrades = metrics.map(m => m.loss_trades);
    
    // Update chart data
    tradeCountChart.data.labels = labels;
    tradeCountChart.data.datasets[0].data = winTrades;
    tradeCountChart.data.datasets[1].data = lossTrades;
    tradeCountChart.update();
}

function initializeDrawdownChart() {
    const ctx = document.getElementById('drawdownChart');
    if (!ctx) return;
    
    drawdownChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Max Drawdown %',
                data: [],
                borderWidth: 2,
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateDrawdownChart(metrics) {
    if (!drawdownChart) return;
    
    // Sort metrics by date
    metrics.sort((a, b) => new Date(a.end_date) - new Date(b.end_date));
    
    // Extract data for chart
    const labels = metrics.map(m => {
        const date = new Date(m.end_date);
        return date.toLocaleDateString();
    });
    
    const drawdowns = metrics.map(m => m.max_drawdown || 0);
    
    // Update chart data
    drawdownChart.data.labels = labels;
    drawdownChart.data.datasets[0].data = drawdowns;
    drawdownChart.update();
}

function updateSummaryStats(metrics) {
    if (!metrics || metrics.length === 0) return;
    
    // Calculate summary statistics
    const totalProfitEl = document.getElementById('totalProfit');
    const avgWinRateEl = document.getElementById('avgWinRate');
    const totalTradesEl = document.getElementById('totalTrades');
    const avgDrawdownEl = document.getElementById('avgDrawdown');
    
    if (totalProfitEl || avgWinRateEl || totalTradesEl || avgDrawdownEl) {
        // Calculate total profit
        const totalProfit = metrics.reduce((sum, m) => sum + m.profit_percent, 0);
        
        // Calculate average win rate
        const avgWinRate = metrics.reduce((sum, m) => sum + m.win_rate, 0) / metrics.length;
        
        // Calculate total trades
        const totalTrades = metrics.reduce((sum, m) => sum + m.total_trades, 0);
        
        // Calculate average drawdown
        const validDrawdowns = metrics.filter(m => m.max_drawdown !== null);
        const avgDrawdown = validDrawdowns.length > 0 
            ? validDrawdowns.reduce((sum, m) => sum + m.max_drawdown, 0) / validDrawdowns.length
            : 0;
        
        // Update elements
        if (totalProfitEl) totalProfitEl.textContent = totalProfit.toFixed(2) + '%';
        if (avgWinRateEl) avgWinRateEl.textContent = avgWinRate.toFixed(2) + '%';
        if (totalTradesEl) totalTradesEl.textContent = totalTrades;
        if (avgDrawdownEl) avgDrawdownEl.textContent = avgDrawdown.toFixed(2) + '%';
    }
}

function showAlert(type, message) {
    const alertsContainer = document.getElementById('alertsContainer');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            if (alertsContainer.contains(alert)) {
                alertsContainer.removeChild(alert);
            }
        }, 500);
    }, 5000);
}