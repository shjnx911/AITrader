/**
 * Dashboard JavaScript cho AITradeStrategist
 * Xử lý hiển thị biểu đồ, lấy dữ liệu và tương tác người dùng
 */

document.addEventListener('DOMContentLoaded', function() {
    // Kiểm tra trạng thái GPU
    checkGPUStatus();
    
    // Kiểm tra trạng thái kết nối Freqtrade
    checkFreqtradeStatus();
    
    // Lấy dữ liệu tóm tắt hiệu suất
    fetchSummaryData();
    
    // Lấy dữ liệu giao dịch gần đây
    fetchRecentTrades();
    
    // Lấy dữ liệu hiệu suất theo cặp
    fetchPairsPerformance();
    
    // Lấy dữ liệu hiệu suất theo thời gian
    fetchPerformanceHistory();
    
    // Sự kiện làm mới dữ liệu
    document.getElementById('btn-refresh').addEventListener('click', function() {
        fetchSummaryData();
        fetchRecentTrades();
        fetchPairsPerformance();
        fetchPerformanceHistory();
        checkFreqtradeStatus();
    });
});

/**
 * Kiểm tra trạng thái GPU
 */
function checkGPUStatus() {
    fetch('/api/gpu_status')
        .then(response => response.json())
        .then(data => {
            const gpuStatus = document.getElementById('gpu-status');
            if (data.gpu_available) {
                gpuStatus.textContent = data.gpu_type + ' (' + data.acceleration + ')';
                gpuStatus.classList.add('text-success');
            } else {
                gpuStatus.textContent = 'CPU Mode';
                gpuStatus.classList.add('text-warning');
            }
        })
        .catch(error => {
            document.getElementById('gpu-status').textContent = 'Không xác định';
            console.error('Error fetching GPU status:', error);
        });
}

/**
 * Kiểm tra trạng thái kết nối Freqtrade
 */
function checkFreqtradeStatus() {
    fetch('/api/freqtrade/status')
        .then(response => response.json())
        .then(data => {
            const freqtradeStatus = document.getElementById('freqtrade-status');
            if (data.error) {
                freqtradeStatus.textContent = 'Không kết nối';
                freqtradeStatus.classList.add('text-danger');
                return;
            }
            
            freqtradeStatus.textContent = 'Kết nối (v' + data.version + ')';
            freqtradeStatus.classList.add('text-success');
        })
        .catch(error => {
            const freqtradeStatus = document.getElementById('freqtrade-status');
            freqtradeStatus.textContent = 'Không kết nối';
            freqtradeStatus.classList.add('text-danger');
            console.error('Error fetching Freqtrade status:', error);
        });
}

/**
 * Lấy dữ liệu tóm tắt
 */
function fetchSummaryData() {
    fetch('/api/stats/summary')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching summary data:', data.error);
                return;
            }
            
            document.getElementById('total-trades').textContent = data.total_trades;
            document.getElementById('win-rate').textContent = data.win_rate + '%';
            document.getElementById('profit-percent').textContent = data.profit_percent + '%';
            document.getElementById('profit-abs').textContent = data.profit_abs;
        })
        .catch(error => {
            console.error('Error fetching summary data:', error);
        });
}

/**
 * Lấy dữ liệu giao dịch gần đây
 */
function fetchRecentTrades() {
    fetch('/api/stats/recent_trades?limit=10')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching recent trades:', data.error);
                return;
            }
            
            const tableBody = document.getElementById('recent-trades-table');
            tableBody.innerHTML = '';
            
            if (data.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="7" class="text-center">Không có dữ liệu giao dịch</td>`;
                tableBody.appendChild(row);
                return;
            }
            
            data.forEach(trade => {
                const row = document.createElement('tr');
                const profitClass = trade.profit_ratio > 0 ? 'text-success' : 'text-danger';
                
                row.innerHTML = `
                    <td>${trade.pair}</td>
                    <td>${trade.open_date}</td>
                    <td>${trade.is_open ? '-' : trade.close_date}</td>
                    <td>${trade.open_rate}</td>
                    <td>${trade.is_open ? '-' : trade.close_rate}</td>
                    <td class="${trade.is_open ? '' : profitClass}">${trade.is_open ? '-' : trade.profit_ratio + '%'}</td>
                    <td>${trade.is_open ? '<span class="badge bg-info">Mở</span>' : '<span class="badge bg-secondary">Đóng</span>'}</td>
                `;
                
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching recent trades:', error);
        });
}

/**
 * Lấy dữ liệu hiệu suất theo cặp
 */
function fetchPairsPerformance() {
    fetch('/api/stats/pairs_performance')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching pairs performance:', data.error);
                return;
            }
            
            renderPairsChart(data);
        })
        .catch(error => {
            console.error('Error fetching pairs performance:', error);
            
            // Tạm thời dùng dữ liệu mẫu để hiển thị
            const dummyData = [
                { pair_name: 'BTC/USDT', profit_percent: 8.5 },
                { pair_name: 'ETH/USDT', profit_percent: 12.3 },
                { pair_name: 'XRP/USDT', profit_percent: 5.7 },
                { pair_name: 'ADA/USDT', profit_percent: 9.1 },
                { pair_name: 'SOL/USDT', profit_percent: 15.6 }
            ];
            
            renderPairsChart(dummyData);
        });
}

/**
 * Render biểu đồ hiệu suất theo cặp
 */
function renderPairsChart(data) {
    const ctx = document.getElementById('pairs-chart').getContext('2d');
    
    // Chỉ lấy top 5 cặp
    const topPairs = data.slice(0, 5);
    
    // Tạo dữ liệu cho biểu đồ
    const chartData = {
        labels: topPairs.map(p => p.pair_name),
        datasets: [{
            label: 'Lợi nhuận (%)',
            data: topPairs.map(p => p.profit_percent),
            backgroundColor: [
                'rgba(75, 192, 192, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)',
                'rgba(255, 99, 132, 0.6)'
            ],
            borderColor: [
                'rgba(75, 192, 192, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 1
        }]
    };
    
    // Kiểm tra xem biểu đồ đã tồn tại chưa
    if (window.pairsChart) {
        window.pairsChart.data = chartData;
        window.pairsChart.update();
    } else {
        // Tạo biểu đồ mới
        window.pairsChart = new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw}%`;
                            }
                        }
                    }
                }
            }
        });
    }
}

/**
 * Lấy dữ liệu hiệu suất theo thời gian
 */
function fetchPerformanceHistory() {
    // Trong môi trường thực tế, cần thay thế bằng API thực
    // Hiện tại dùng dữ liệu mẫu
    const dummyData = {
        labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10'],
        datasets: [{
            label: 'Lợi nhuận tích lũy (%)',
            data: [0, 1.2, 2.5, 2.1, 3.8, 5.2, 4.8, 6.7, 8.1, 10.5],
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    };
    
    renderPerformanceChart(dummyData);
}

/**
 * Render biểu đồ hiệu suất theo thời gian
 */
function renderPerformanceChart(data) {
    const ctx = document.getElementById('performance-chart').getContext('2d');
    
    // Kiểm tra xem biểu đồ đã tồn tại chưa
    if (window.performanceChart) {
        window.performanceChart.data = data;
        window.performanceChart.update();
    } else {
        // Tạo biểu đồ mới
        window.performanceChart = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
}