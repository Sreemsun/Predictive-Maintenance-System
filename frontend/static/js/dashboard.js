// Dashboard State
let updateInterval = null;
let currentExpandedMachine = null;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    setupEventListeners();
    startAutoUpdate();
});

function initializeDashboard() {
    updateLastRefreshTime();
    loadMachines();
}

function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshButton').addEventListener('click', () => {
        loadMachines();
        if (currentExpandedMachine) {
            loadMachineDetails(currentExpandedMachine);
        }
        showToast('Data refreshed successfully');
    });

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!item.getAttribute('href').startsWith('/')) {
                e.preventDefault();
                document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
            }
        });
    });
}

function startAutoUpdate() {
    // Update every 10 seconds
    updateInterval = setInterval(() => {
        loadMachines();
        if (currentExpandedMachine) {
            loadMachineDetails(currentExpandedMachine);
        }
    }, 10000);
}

async function loadMachines() {
    try {
        const response = await fetch('/api/machines/list');
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to load machines');
        }

        // Update summary stats
        const healthyCount = data.machines.filter(m => m.status === 'active').length;
        const warningCount = data.machines.filter(m => m.status === 'warning').length;
        const criticalCount = data.machines.filter(m => m.status === 'critical').length;

        document.getElementById('summary-total').textContent = data.total_count;
        document.getElementById('summary-healthy').textContent = healthyCount;
        document.getElementById('summary-warning').textContent = warningCount;
        document.getElementById('summary-critical').textContent = criticalCount;

        // Display machines
        displayMachines(data.machines);
        updateLastRefreshTime();
    } catch (error) {
        console.error('Error loading machines:', error);
        showToast('Error loading machines', 'error');
    }
}

function displayMachines(machines) {
    const container = document.getElementById('machinesList');

    if (machines.length === 0) {
        container.innerHTML = `
            <div class="card" style="padding: 3rem; text-align: center;">
                <h3 style="color: white;">No Machines Found</h3>
                <p style="color: #6c757d; margin-top: 1rem;">Start sending sensor data to see machines here</p>
                <a href="/predict" style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 8px;">
                    Try AI Prediction
                </a>
            </div>
        `;
        return;
    }

    container.innerHTML = machines.map(machine => createMachineCard(machine)).join('');

    // Add click handlers
    machines.forEach(machine => {
        const card = document.getElementById(`machine-${machine.machine_id}`);
        if (card) {
            card.addEventListener('click', () => toggleMachineDetails(machine.machine_id));
        }
    });
}

function createMachineCard(machine) {
    const statusColors = {
        'active': '#28a745',
        'warning': '#ffc107',
        'critical': '#dc3545'
    };

    const statusIcons = {
        'active': '✓',
        'warning': '⚠',
        'critical': '✗'
    };

    const machineIcons = {
        'pump': '⚙️',
        'motor': '⚡',
        'compressor': '🔧',
        'hvac': '❄️',
        'default': '🏭'
    };

    // Determine icon based on machine_id instead of machine_type
    const iconKey = Object.keys(machineIcons).find(key => machine.machine_id.toLowerCase().includes(key)) || 'default';
    const icon = machineIcons[iconKey];

    // Convert machine type code to readable name
    const typeNames = { 'L': 'Low Risk Type', 'M': 'Medium Risk Type', 'H': 'High Risk Type' };
    const typeName = typeNames[machine.machine_type] || machine.machine_type;

    const isExpanded = currentExpandedMachine === machine.machine_id;

    return `
        <div class="machine-card card" id="machine-${machine.machine_id}" style="margin-bottom: 1rem; cursor: pointer; transition: all 0.3s; border-left: 4px solid ${statusColors[machine.status]};">
            <div style="display: flex; align-items: center; gap: 1.5rem; padding: 1.5rem;">
                <div style="font-size: 3rem;">${icon}</div>
                <div style="flex: 1;">
                    <h3 style="margin-bottom: 0.5rem; font-size: 1.3rem; color: white;">${machine.machine_name}</h3>
                    <p style="color: #6c757d; margin-bottom: 0.5rem;">${typeName}</p>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        <span style="font-size: 0.9rem; color: #6c757d;">
                            <strong>Readings:</strong> ${machine.total_readings || machine.reading_count}
                        </span>
                        <span style="font-size: 0.9rem; color: #6c757d;">
                            <strong>Last Seen:</strong> ${formatTimestamp(machine.last_seen)}
                        </span>
                    </div>
                </div>
                <div style="text-align: center; padding: 0 2rem; border-left: 1px solid #e0e0e0;">
                    <div style="font-size: 2.5rem; font-weight: bold; color: ${statusColors[machine.status]};">
                        ${machine.health_score}
                    </div>
                    <div style="color: #6c757d; font-size: 0.9rem; margin-top: 0.25rem;">Health Score</div>
                </div>
                <div style="text-align: center; min-width: 120px;">
                    <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 20px; background: ${statusColors[machine.status]}20; color: ${statusColors[machine.status]}; font-weight: bold;">
                        <span style="font-size: 1.2rem;">${statusIcons[machine.status]}</span>
                        <span>${machine.status.toUpperCase()}</span>
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #6c757d;">
                        Risk: ${machine.risk_level}
                    </div>
                </div>
                <div style="font-size: 1.5rem; transform: rotate(${isExpanded ? '180deg' : '0deg'}); transition: transform 0.3s; color: #6c757d;">
                    ▼
                </div>
            </div>
            <div id="details-${machine.machine_id}" style="display: ${isExpanded ? 'block' : 'none'}; border-top: 1px solid #e0e0e0; padding: 2rem; background: #1a1a1a;">
                <div id="charts-${machine.machine_id}">
                    <div style="text-align: center; padding: 2rem;">
                        <div class="loading-spinner"></div>
                        <p style="color: #6c757d;">Loading machine details...</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function toggleMachineDetails(machineId) {
    const detailsDiv = document.getElementById(`details-${machineId}`);
    const wasExpanded = currentExpandedMachine === machineId;

    // Collapse all other machines
    document.querySelectorAll('[id^="details-"]').forEach(div => {
        div.style.display = 'none';
    });

    if (wasExpanded) {
        // Collapse this machine
        detailsDiv.style.display = 'none';
        currentExpandedMachine = null;
    } else {
        // Expand this machine
        detailsDiv.style.display = 'block';
        currentExpandedMachine = machineId;
        loadMachineDetails(machineId);
    }

    // Update arrow rotations
    document.querySelectorAll('.machine-card').forEach(card => {
        const id = card.id.replace('machine-', '');
        const arrow = card.querySelector('[style*="transform: rotate"]');
        if (arrow) {
            arrow.style.transform = id === machineId && !wasExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
        }
    });
}

async function loadMachineDetails(machineId) {
    try {
        const response = await fetch(`/api/machine/${machineId}/details?limit=50`);
        const data = await response.json();

        const chartsDiv = document.getElementById(`charts-${machineId}`);
        
        if (!data.readings.timestamps || data.readings.timestamps.length === 0) {
            chartsDiv.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <h3 style="color: white;">No Data Available</h3>
                    <p style="color: #6c757d;">No recent sensor readings for this machine</p>
                </div>
            `;
            return;
        }

        // Create charts container
        chartsDiv.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
                <div class="card" style="padding: 1rem; background: #2a2a2a;">
                    <h4 style="margin-bottom: 1rem; color: white;">Temperature & Pressure</h4>
                    <div id="temp-chart-${machineId}" style="height: 300px;"></div>
                </div>
                <div class="card" style="padding: 1rem; background: #2a2a2a;">
                    <h4 style="margin-bottom: 1rem; color: white;">Speed & Torque</h4>
                    <div id="speed-chart-${machineId}" style="height: 300px;"></div>
                </div>
            </div>
            <div class="card" style="padding: 1rem; background: #2a2a2a;">
                <h4 style="margin-bottom: 1rem; color: white;">Recent Predictions</h4>
                <div id="predictions-${machineId}"></div>
            </div>
        `;

        // Temperature & Pressure Chart
        Plotly.newPlot(`temp-chart-${machineId}`, [
            {
                x: data.readings.timestamps,
                y: data.readings.temperatures,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Temperature (°C)',
                line: { color: '#dc3545', width: 2 },
                marker: { size: 6 }
            },
            {
                x: data.readings.timestamps,
                y: data.readings.pressures,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Process Temp (°C)',
                line: { color: '#007bff', width: 2 },
                marker: { size: 6 }
            }
        ], {
            margin: { t: 10, r: 10, b: 40, l: 50 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            xaxis: { 
                gridcolor: 'rgba(255,255,255,0.1)',
                showgrid: true
            },
            yaxis: { 
                gridcolor: 'rgba(255,255,255,0.1)',
                title: 'Temperature (°C)'
            },
            legend: { x: 0, y: 1.1, orientation: 'h' }
        }, { responsive: true, displayModeBar: false });

        // Speed & Torque Chart
        Plotly.newPlot(`speed-chart-${machineId}`, [
            {
                x: data.readings.timestamps,
                y: data.readings.speeds,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Speed (RPM)',
                line: { color: '#28a745', width: 2 },
                marker: { size: 6 },
                yaxis: 'y'
            },
            {
                x: data.readings.timestamps,
                y: data.readings.torques,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Torque (Nm)',
                line: { color: '#ffc107', width: 2 },
                marker: { size: 6 },
                yaxis: 'y2'
            }
        ], {
            margin: { t: 10, r: 60, b: 40, l: 50 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            xaxis: { 
                gridcolor: 'rgba(255,255,255,0.1)',
                showgrid: true
            },
            yaxis: { 
                title: 'Speed (RPM)',
                gridcolor: 'rgba(255,255,255,0.1)'
            },
            yaxis2: {
                title: 'Torque (Nm)',
                overlaying: 'y',
                side: 'right'
            },
            legend: { x: 0, y: 1.1, orientation: 'h' }
        }, { responsive: true, displayModeBar: false });

        // Predictions Table
        const predictionsDiv = document.getElementById(`predictions-${machineId}`);
        if (data.predictions.length === 0) {
            predictionsDiv.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 1rem;">No predictions available</p>';
        } else {
            const predictionsHtml = data.predictions.map(pred => {
                const riskLevel = pred.risk_level.toUpperCase();
                const riskColor = riskLevel === 'HIGH' ? '#dc3545' : riskLevel === 'MEDIUM' ? '#ffc107' : '#28a745';
                return `
                    <div style="display: flex; justify-content: space-between; padding: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: white;">
                        <span>${formatTimestamp(pred.timestamp)}</span>
                        <span style="color: ${riskColor}; font-weight: bold;">${pred.failure_probability}% failure risk</span>
                        <span style="color: ${riskColor};">${riskLevel}</span>
                    </div>
                `;
            }).join('');
            predictionsDiv.innerHTML = predictionsHtml;
        }

    } catch (error) {
        console.error('Error loading machine details:', error);
        const chartsDiv = document.getElementById(`charts-${machineId}`);
        chartsDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #dc3545;">
                <h3>Error Loading Data</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = (now - date) / 1000; // seconds

    if (diff < 60) {
        return 'Just now';
    } else if (diff < 3600) {
        return `${Math.floor(diff / 60)} min ago`;
    } else if (diff < 86400) {
        return `${Math.floor(diff / 3600)}h ago`;
    } else {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
}

function updateLastRefreshTime() {
    const now = new Date();
    document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
}

function showToast(message, type = 'success') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
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
