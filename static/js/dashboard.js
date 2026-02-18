// Dashboard State
let updateInterval = null;
let sensorDataBuffer = [];

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    setupEventListeners();
    startAutoUpdate();
});

function initializeDashboard() {
    updateLastRefreshTime();
    loadAllData();
}

function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshButton').addEventListener('click', () => {
        loadAllData();
        showToast('Data refreshed successfully');
    });

    // Time range selector
    document.getElementById('timeRange').addEventListener('change', (e) => {
        loadHistoricalData(e.target.value);
    });

    // Clear all alerts
    document.getElementById('clearAllAlerts').addEventListener('click', () => {
        document.getElementById('alertsList').innerHTML = '<p class="empty-state">No active alerts</p>';
        document.getElementById('alertBadge').textContent = '0';
        showToast('All alerts cleared');
    });

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function startAutoUpdate() {
    // Update every 5 seconds
    updateInterval = setInterval(() => {
        loadAllData();
    }, 5000);
}

async function loadAllData() {
    try {
        await Promise.all([
            loadHealthScores(),
            loadSensorData(),
            loadPredictions(),
            loadAlerts(),
            loadAnomalies()
        ]);
        updateLastRefreshTime();
    } catch (error) {
        console.error('Error loading data:', error);
        showToast('Error loading data', 'error');
    }
}

async function loadHealthScores() {
    try {
        const response = await fetch('/api/health-score');
        const data = await response.json();

        updateHealthCard('pump', data.pump);
        updateHealthCard('motor', data.motor);
        updateHealthCard('hvac', data.hvac);

        // Update summary
        const statuses = Object.values(data);
        const activeCount = statuses.filter(s => s.status === 'healthy').length;
        const warningCount = statuses.filter(s => s.status === 'warning').length;
        const criticalCount = statuses.filter(s => s.status === 'critical').length;

        document.getElementById('active-count').textContent = activeCount;
        document.getElementById('warning-count').textContent = warningCount;
        document.getElementById('critical-count').textContent = criticalCount;
    } catch (error) {
        console.error('Error loading health scores:', error);
    }
}

function updateHealthCard(equipment, data) {
    const scoreElement = document.getElementById(`${equipment}-score`);
    const statusElement = document.getElementById(`${equipment}-status`);

    scoreElement.textContent = data.score;
    
    statusElement.className = `status-indicator ${data.status}`;
    statusElement.innerHTML = `
        <span class="status-dot"></span>
        <span class="status-text">${capitalizeFirst(data.status)}</span>
    `;
}

async function loadSensorData() {
    try {
        const response = await fetch('/api/sensor-data');
        const data = await response.json();

        updateSensorChart(data);
        updateVibrationChart(data);
    } catch (error) {
        console.error('Error loading sensor data:', error);
    }
}

function updateSensorChart(data) {
    const traces = [
        {
            x: data.timestamps,
            y: data.temperature,
            name: 'Temperature (°C)',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#ef4444', width: 2 }
        },
        {
            x: data.timestamps,
            y: data.pressure,
            name: 'Pressure (PSI)',
            type: 'scatter',
            mode: 'lines',
            yaxis: 'y2',
            line: { color: '#2563eb', width: 2 }
        }
    ];

    const layout = {
        title: '',
        showlegend: true,
        legend: { orientation: 'h', y: -0.2 },
        xaxis: {
            title: 'Time',
            showgrid: true,
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: 'Temperature (°C)',
            showgrid: true,
            gridcolor: '#f3f4f6'
        },
        yaxis2: {
            title: 'Pressure (PSI)',
            overlaying: 'y',
            side: 'right',
            showgrid: false
        },
        margin: { t: 20, r: 60, b: 60, l: 60 },
        paper_bgcolor: 'white',
        plot_bgcolor: 'white'
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('sensorChart', traces, layout, config);
}

function updateVibrationChart(data) {
    const traces = [
        {
            x: data.timestamps,
            y: data.vibration,
            name: 'Vibration (mm/s)',
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            line: { color: '#10b981', width: 2 },
            fillcolor: 'rgba(16, 185, 129, 0.1)'
        }
    ];

    const layout = {
        title: '',
        showlegend: true,
        legend: { orientation: 'h', y: -0.2 },
        xaxis: {
            title: 'Time',
            showgrid: true,
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: 'Vibration (mm/s)',
            showgrid: true,
            gridcolor: '#f3f4f6'
        },
        shapes: [{
            type: 'line',
            x0: data.timestamps[0],
            x1: data.timestamps[data.timestamps.length - 1],
            y0: 15,
            y1: 15,
            line: {
                color: '#f59e0b',
                width: 2,
                dash: 'dash'
            }
        }],
        annotations: [{
            x: data.timestamps[Math.floor(data.timestamps.length / 2)],
            y: 15,
            text: 'Warning Threshold',
            showarrow: false,
            yshift: 10,
            font: { color: '#f59e0b', size: 10 }
        }],
        margin: { t: 20, r: 40, b: 60, l: 60 },
        paper_bgcolor: 'white',
        plot_bgcolor: 'white'
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('vibrationChart', traces, layout, config);
}

async function loadPredictions() {
    try {
        const response = await fetch('/api/predictions');
        const data = await response.json();

        const predictionsList = document.getElementById('predictionsList');
        
        if (data.predictions.length === 0) {
            predictionsList.innerHTML = '<p class="empty-state">No predictions available</p>';
            return;
        }

        predictionsList.innerHTML = data.predictions.map(pred => `
            <div class="prediction-item">
                <div class="prediction-header">
                    <span class="prediction-title">${pred.equipment}</span>
                    <span class="prediction-time">${pred.timeToFailure}</span>
                </div>
                <div class="prediction-details">${pred.details}</div>
                <div class="prediction-confidence">
                    <div class="confidence-bar">
                        <div class="confidence-fill ${pred.confidenceLevel}" style="width: ${pred.confidence}%"></div>
                    </div>
                    <span class="confidence-text">${pred.confidence}%</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();

        const alertsList = document.getElementById('alertsList');
        const alertBadge = document.getElementById('alertBadge');
        
        alertBadge.textContent = data.alerts.length;

        if (data.alerts.length === 0) {
            alertsList.innerHTML = '<p class="empty-state">No active alerts</p>';
            return;
        }

        alertsList.innerHTML = data.alerts.map(alert => `
            <div class="alert-item">
                <div class="alert-header">
                    <span class="alert-title">${alert.equipment}</span>
                    <span class="severity-badge ${alert.severity}">${alert.severity}</span>
                </div>
                <div class="alert-message">${alert.message}</div>
                <div class="alert-time">${alert.timestamp}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadAnomalies() {
    try {
        const response = await fetch('/api/anomalies');
        const data = await response.json();

        updateAnomalyChart(data);
    } catch (error) {
        console.error('Error loading anomalies:', error);
    }
}

function updateAnomalyChart(data) {
    const normalData = data.timestamps.map((t, i) => 
        data.anomalies[i] ? null : data.values[i]
    );
    
    const anomalyData = data.timestamps.map((t, i) => 
        data.anomalies[i] ? data.values[i] : null
    );

    const traces = [
        {
            x: data.timestamps,
            y: normalData,
            name: 'Normal',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#2563eb', width: 2 }
        },
        {
            x: data.timestamps,
            y: anomalyData,
            name: 'Anomaly',
            type: 'scatter',
            mode: 'markers',
            marker: { color: '#ef4444', size: 8 }
        }
    ];

    const layout = {
        title: '',
        showlegend: true,
        legend: { orientation: 'h', y: -0.2 },
        xaxis: {
            title: 'Time',
            showgrid: true,
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: 'Sensor Value',
            showgrid: true,
            gridcolor: '#f3f4f6'
        },
        margin: { t: 20, r: 40, b: 60, l: 60 },
        paper_bgcolor: 'white',
        plot_bgcolor: 'white'
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('anomalyChart', traces, layout, config);
}

async function loadHistoricalData(hours) {
    try {
        const response = await fetch(`/api/historical-data?hours=${hours}`);
        const data = await response.json();
        
        updateSensorChart(data);
        updateVibrationChart(data);
    } catch (error) {
        console.error('Error loading historical data:', error);
    }
}

function updateLastRefreshTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('lastUpdate').textContent = timeString;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
