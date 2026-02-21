// Real-Time Monitoring Dashboard JavaScript

let machines = [];
let selectedMachines = [];
let autoRefreshInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize
    loadMachines();
    loadPredictions();
    loadAlerts();
    
    // Machine Registration Modal
    const registerModal = document.getElementById('registerModal');
    const showRegisterModal = document.getElementById('showRegisterModal');
    const closeModal = document.getElementById('closeModal');
    const cancelModal = document.getElementById('cancelModal');
    const registerForm = document.getElementById('registerForm');
    
    showRegisterModal.addEventListener('click', () => {
        registerModal.classList.add('active');
    });
    
    closeModal.addEventListener('click', () => {
        registerModal.classList.remove('active');
    });
    
    cancelModal.addEventListener('click', () => {
        registerModal.classList.remove('active');
    });
    
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await registerMachine();
    });
    
    // Data Ingestion Modals
    const ingestionModal = document.getElementById('ingestionModal');
    const singleIngestionBtn = document.getElementById('singleIngestionBtn');
    const closeIngestionModal = document.getElementById('closeIngestionModal');
    const cancelIngestionModal = document.getElementById('cancelIngestionModal');
    const ingestionForm = document.getElementById('ingestionForm');
    
    singleIngestionBtn.addEventListener('click', () => {
        populateMachineSelect();
        ingestionModal.classList.add('active');
    });
    
    closeIngestionModal.addEventListener('click', () => {
        ingestionModal.classList.remove('active');
    });
    
    cancelIngestionModal.addEventListener('click', () => {
        ingestionModal.classList.remove('active');
    });
    
    ingestionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await sendSingleReading();
    });
    
    // Bulk Ingestion
    document.getElementById('bulkIngestionBtn').addEventListener('click', () => {
        showBulkIngestionInfo();
    });
    
    // Simulate Data Stream
    document.getElementById('simulateBtn').addEventListener('click', () => {
        simulateDataStream();
    });
    
    // Auto Refresh
    const autoRefreshCheckbox = document.getElementById('autoRefresh');
    autoRefreshCheckbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Start auto refresh by default
    if (autoRefreshCheckbox.checked) {
        startAutoRefresh();
    }
    
    // Load Charts
    document.getElementById('loadCharts').addEventListener('click', () => {
        loadCharts();
    });
    
    // Compare Machines
    document.getElementById('compareBtn').addEventListener('click', () => {
        compareMachines();
    });
});

async function loadMachines() {
    try {
        const response = await fetch('/api/machines/list');
        const data = await response.json();
        
        if (data.success) {
            machines = data.machines;
            displayMachines(machines);
            populateMachineSelects();
        }
    } catch (error) {
        console.error('Error loading machines:', error);
    }
}

function displayMachines(machinesList) {
    const grid = document.getElementById('machinesGrid');
    
    if (machinesList.length === 0) {
        grid.innerHTML = '<p class="info-text">No machines registered. Click "Register New Machine" to add one.</p>';
        return;
    }
    
    grid.innerHTML = machinesList.map(machine => `
        <div class="machine-card" data-machine-id="${machine.machine_id}" onclick="toggleMachineSelection('${machine.machine_id}')">
            <div class="machine-card-header">
                <div class="machine-info">
                    <h3>${machine.machine_name}</h3>
                    <p>ID: ${machine.machine_id}</p>
                    <p>Type: ${machine.machine_type} | ${machine.location || 'No location'}</p>
                </div>
                <span class="machine-status active">${machine.status}</span>
            </div>
            <div class="machine-stats">
                <div class="stat-item">
                    <div class="stat-value">${machine.total_readings || 0}</div>
                    <div class="stat-label">Readings</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${machine.last_reading ? formatTimeAgo(machine.last_reading) : 'Never'}</div>
                    <div class="stat-label">Last Reading</div>
                </div>
            </div>
        </div>
    `).join('');
}

function toggleMachineSelection(machineId) {
    const card = document.querySelector(`[data-machine-id="${machineId}"]`);
    
    if (selectedMachines.includes(machineId)) {
        selectedMachines = selectedMachines.filter(id => id !== machineId);
        card.classList.remove('selected');
    } else {
        selectedMachines.push(machineId);
        card.classList.add('selected');
    }
}

function populateMachineSelects() {
    const machineSelect = document.getElementById('machineSelect');
    const ingestMachineId = document.getElementById('ingestMachineId');
    
    const options = machines.map(m => 
        `<option value="${m.machine_id}">${m.machine_name} (${m.machine_id})</option>`
    ).join('');
    
    machineSelect.innerHTML = '<option value="">Select Machine</option>' + options;
    if (ingestMachineId) {
        ingestMachineId.innerHTML = '<option value="">Select Machine</option>' + options;
    }
}

function populateMachineSelect() {
    populateMachineSelects();
}

async function registerMachine() {
    const machineId = document.getElementById('machineId').value;
    const machineName = document.getElementById('machineName').value;
    const machineType = document.getElementById('machineType').value;
    const machineLocation = document.getElementById('machineLocation').value;
    
    try {
        const response = await fetch('/api/machines/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                machine_id: machineId,
                machine_name: machineName,
                machine_type: machineType,
                location: machineLocation
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Machine registered successfully!');
            document.getElementById('registerModal').classList.remove('active');
            document.getElementById('registerForm').reset();
            loadMachines();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error registering machine: ' + error.message);
    }
}

async function sendSingleReading() {
    const machineId = document.getElementById('ingestMachineId').value;
    const machine = machines.find(m => m.machine_id === machineId);
    
    if (!machine) {
        alert('Please select a machine');
        return;
    }
    
    const data = {
        machine_id: machineId,
        type: machine.machine_type,
        air_temp: parseFloat(document.getElementById('ingestAirTemp').value),
        process_temp: parseFloat(document.getElementById('ingestProcessTemp').value),
        rotational_speed: parseInt(document.getElementById('ingestSpeed').value),
        torque: parseFloat(document.getElementById('ingestTorque').value),
        tool_wear: parseInt(document.getElementById('ingestToolWear').value)
    };
    
    try {
        const response = await fetch('/api/data/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Data sent successfully! Prediction: ' + 
                  (result.prediction.will_fail ? 'FAILURE PREDICTED' : 'Machine OK'));
            document.getElementById('ingestionModal').classList.remove('active');
            document.getElementById('ingestionForm').reset();
            loadPredictions();
            loadAlerts();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Error sending data: ' + error.message);
    }
}

function showBulkIngestionInfo() {
    const card = document.getElementById('ingestionCard');
    card.innerHTML = `
        <h3>Bulk Data Ingestion API</h3>
        <p style="margin: 1rem 0;">Send multiple readings at once using the API:</p>
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <strong>POST</strong> <code>/api/data/batch-ingest</code>
            <pre style="margin-top: 1rem; overflow-x: auto; background: white; padding: 1rem; border-radius: 5px;">
{
  "readings": [
    {
      "machine_id": "MACHINE-001",
      "type": "L",
      "air_temp": 298.5,
      "process_temp": 308.7,
      "rotational_speed": 1500,
      "torque": 40.0,
      "tool_wear": 50
    }
  ]
}</pre>
        </div>
        <p style="color: #666;">Use this endpoint to send continuous streams of data from your IoT devices or data pipeline.</p>
    `;
}

async function simulateDataStream() {
    if (machines.length === 0) {
        alert('Please register at least one machine first');
        return;
    }
    
    const confirmed = confirm('This will simulate sending 10 random readings. Continue?');
    if (!confirmed) return;
    
    const readings = [];
    for (let i = 0; i < 10; i++) {
        const machine = machines[Math.floor(Math.random() * machines.length)];
        readings.push({
            machine_id: machine.machine_id,
            type: machine.machine_type,
            air_temp: 295 + Math.random() * 10,
            process_temp: 305 + Math.random() * 10,
            rotational_speed: Math.floor(1200 + Math.random() * 1000),
            torque: 20 + Math.random() * 50,
            tool_wear: Math.floor(Math.random() * 200)
        });
    }
    
    try {
        const response = await fetch('/api/data/batch-ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ readings })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Simulated ${result.successful} readings successfully!`);
            loadPredictions();
            loadAlerts();
        }
    } catch (error) {
        alert('Error simulating data: ' + error.message);
    }
}

async function loadPredictions() {
    try {
        const response = await fetch('/api/data/recent-predictions?limit=20');
        const data = await response.json();
        
        if (data.success) {
            displayPredictions(data.predictions);
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

function displayPredictions(predictions) {
    const feed = document.getElementById('predictionsFeed');
    
    if (predictions.length === 0) {
        feed.innerHTML = '<p class="info-text">No predictions yet. Send some data to see predictions here.</p>';
        return;
    }
    
    feed.innerHTML = predictions.map(pred => `
        <div class="prediction-item ${pred.will_fail ? 'failure' : ''}">
            <div class="prediction-header">
                <span class="prediction-machine">
                    ${pred.machine_id} - ${pred.will_fail ? '⚠️ FAILURE PREDICTED' : '✅ OK'}
                </span>
                <span class="prediction-time">${formatTimeAgo(pred.timestamp)}</span>
            </div>
            <div class="prediction-details">
                <div class="prediction-metric">
                    <strong>Probability:</strong> ${(pred.failure_probability * 100).toFixed(1)}%
                </div>
                <div class="prediction-metric">
                    <strong>Confidence:</strong> ${pred.confidence.toFixed(1)}%
                </div>
                <div class="prediction-metric">
                    <strong>Risk Level:</strong> ${pred.risk_level.toUpperCase()}
                </div>
                <div class="prediction-metric">
                    <strong>Tool Wear:</strong> ${pred.tool_wear} min
                </div>
            </div>
        </div>
    `).join('');
}

async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts/active');
        const data = await response.json();
        
        if (data.success) {
            displayAlerts(data.alerts);
            document.getElementById('alertCount').textContent = data.count;
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function displayAlerts(alerts) {
    const list = document.getElementById('alertsList');
    
    if (alerts.length === 0) {
        list.innerHTML = '<p class="info-text">No active alerts. All systems normal.</p>';
        return;
    }
    
    list.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.severity}">
            <div class="alert-content">
                <div class="alert-message">
                    <strong>${alert.machine_name}:</strong> ${alert.message}
                </div>
                <div class="alert-time">${formatTimeAgo(alert.timestamp)}</div>
            </div>
            <div class="alert-actions">
                <button onclick="acknowledgeAlert(${alert.id})">Acknowledge</button>
            </div>
        </div>
    `).join('');
}

async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/acknowledge/${alertId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadAlerts();
        }
    } catch (error) {
        console.error('Error acknowledging alert:', error);
    }
}

async function loadCharts() {
    const machineId = document.getElementById('machineSelect').value;
    const hours = parseInt(document.getElementById('timeRange').value);
    
    if (!machineId) {
        alert('Please select a machine');
        return;
    }
    
    try {
        const response = await fetch(`/api/data/history/${machineId}?hours=${hours}`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            plotCharts(data.data);
        } else {
            alert('No data available for this machine');
        }
    } catch (error) {
        alert('Error loading chart data: ' + error.message);
    }
}

function plotCharts(data) {
    // Sort by timestamp
    data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    const timestamps = data.map(d => d.timestamp);
    
    // Probability Chart
    const probabilityTrace = {
        x: timestamps,
        y: data.map(d => d.failure_probability * 100),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Failure Probability',
        line: { color: '#e74c3c', width: 2 }
    };
    
    Plotly.newPlot('probabilityChart', [probabilityTrace], {
        title: 'Failure Probability Over Time',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Probability (%)' },
        hovermode: 'closest'
    });
    
    // Temperature Chart
    const airTempTrace = {
        x: timestamps,
        y: data.map(d => d.air_temperature),
        type: 'scatter',
        mode: 'lines',
        name: 'Air Temperature',
        line: { color: '#3498db' }
    };
    
    const processTempTrace = {
        x: timestamps,
        y: data.map(d => d.process_temperature),
        type: 'scatter',
        mode: 'lines',
        name: 'Process Temperature',
        line: { color: '#e74c3c' }
    };
    
    Plotly.newPlot('temperatureChart', [airTempTrace, processTempTrace], {
        title: 'Temperature Trends',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Temperature (K)' },
        hovermode: 'closest'
    });
    
    // Parameters Chart
    const speedTrace = {
        x: timestamps,
        y: data.map(d => d.rotational_speed),
        type: 'scatter',
        mode: 'lines',
        name: 'Rotational Speed',
        yaxis: 'y'
    };
    
    const torqueTrace = {
        x: timestamps,
        y: data.map(d => d.torque),
        type: 'scatter',
        mode: 'lines',
        name: 'Torque',
        yaxis: 'y2'
    };
    
    Plotly.newPlot('parametersChart', [speedTrace, torqueTrace], {
        title: 'Operational Parameters',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Speed (rpm)' },
        yaxis2: { title: 'Torque (Nm)', overlaying: 'y', side: 'right' },
        hovermode: 'closest'
    });
    
    // Risk Distribution
    const riskCounts = {
        'low': 0,
        'medium': 0,
        'high': 0,
        'critical': 0
    };
    
    data.forEach(d => {
        if (d.risk_level) {
            riskCounts[d.risk_level]++;
        }
    });
    
    const riskTrace = {
        x: ['Low', 'Medium', 'High', 'Critical'],
        y: [riskCounts.low, riskCounts.medium, riskCounts.high, riskCounts.critical],
        type: 'bar',
        marker: {
            color: ['#27ae60', '#f39c12', '#e67e22', '#e74c3c']
        }
    };
    
    Plotly.newPlot('riskChart', [riskTrace], {
        title: 'Risk Level Distribution',
        xaxis: { title: 'Risk Level' },
        yaxis: { title: 'Count' }
    });
}

async function compareMachines() {
    if (selectedMachines.length < 2) {
        alert('Please select at least 2 machines to compare');
        return;
    }
    
    const hours = parseInt(document.getElementById('timeRange').value);
    
    try {
        const params = new URLSearchParams();
        selectedMachines.forEach(id => params.append('machine_ids', id));
        params.append('hours', hours);
        
        const response = await fetch(`/api/compare?${params}`);
        const data = await response.json();
        
        if (data.success) {
            displayComparison(data.comparison);
        }
    } catch (error) {
        alert('Error comparing machines: ' + error.message);
    }
}

function displayComparison(comparison) {
    const content = document.getElementById('comparisonContent');
    
    content.innerHTML = `
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f8f9fa;">
                    <th style="padding: 1rem; text-align: left;">Machine</th>
                    <th style="padding: 1rem; text-align: center;">Avg Failure Prob</th>
                    <th style="padding: 1rem; text-align: center;">Avg Tool Wear</th>
                    <th style="padding: 1rem; text-align: center;">Avg Speed</th>
                    <th style="padding: 1rem; text-align: center;">Readings</th>
                </tr>
            </thead>
            <tbody>
                ${comparison.map(m => `
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 1rem;">${m.machine_name}</td>
                        <td style="padding: 1rem; text-align: center;">${(m.avg_failure_prob * 100).toFixed(1)}%</td>
                        <td style="padding: 1rem; text-align: center;">${m.avg_tool_wear.toFixed(1)} min</td>
                        <td style="padding: 1rem; text-align: center;">${m.avg_speed.toFixed(0)} rpm</td>
                        <td style="padding: 1rem; text-align: center;">${m.reading_count}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        loadPredictions();
        loadAlerts();
    }, 5000); // Refresh every 5 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = Math.floor((now - time) / 1000); // seconds
    
    if (diff < 60) return diff + 's ago';
    if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
    if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
    return Math.floor(diff / 86400) + 'd ago';
}
