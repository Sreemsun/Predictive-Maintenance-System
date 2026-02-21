// Machine Health Prediction JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const resultCard = document.getElementById('resultCard');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const predictBtn = document.getElementById('predictBtn');
    const resetBtn = document.getElementById('resetBtn');
    const sampleBtn = document.getElementById('sampleBtn');
    const newPredictionBtn = document.getElementById('newPredictionBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    let lastPrediction = null;

    // Load model information
    loadModelInfo();

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await makePrediction();
    });

    // Reset button
    resetBtn.addEventListener('click', function() {
        form.reset();
        resultCard.style.display = 'none';
    });

    // Sample data button
    sampleBtn.addEventListener('click', function() {
        loadSampleData();
    });

    // New prediction button
    newPredictionBtn.addEventListener('click', function() {
        resultCard.style.display = 'none';
        form.reset();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Download report button
    downloadBtn.addEventListener('click', function() {
        downloadReport();
    });

    async function makePrediction() {
        // Get form data
        const formData = {
            type: document.getElementById('type').value,
            air_temp: parseFloat(document.getElementById('air_temp').value),
            process_temp: parseFloat(document.getElementById('process_temp').value),
            rotational_speed: parseInt(document.getElementById('rotational_speed').value),
            torque: parseFloat(document.getElementById('torque').value),
            tool_wear: parseInt(document.getElementById('tool_wear').value)
        };

        // Validate inputs
        if (!validateInputs(formData)) {
            return;
        }

        // Show loading
        loadingSpinner.style.display = 'flex';
        resultCard.style.display = 'none';
        predictBtn.disabled = true;

        try {
            // Make API call
            const response = await fetch('/api/ml-predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Prediction failed');
            }

            const data = await response.json();
            
            if (data.success) {
                lastPrediction = {
                    input: formData,
                    result: data.prediction,
                    timestamp: data.timestamp
                };
                displayResults(data.prediction, formData);
            } else {
                showError('Prediction failed: ' + (data.error || 'Unknown error'));
            }

        } catch (error) {
            console.error('Error:', error);
            showError('Failed to make prediction. Please try again.');
        } finally {
            loadingSpinner.style.display = 'none';
            predictBtn.disabled = false;
        }
    }

    function validateInputs(data) {
        // Validate temperature ranges
        if (data.air_temp < 290 || data.air_temp > 310) {
            alert('Air temperature should be between 290-310 K');
            return false;
        }
        if (data.process_temp < 300 || data.process_temp > 320) {
            alert('Process temperature should be between 300-320 K');
            return false;
        }
        if (data.rotational_speed < 1000 || data.rotational_speed > 3000) {
            alert('Rotational speed should be between 1000-3000 rpm');
            return false;
        }
        if (data.torque < 0 || data.torque > 100) {
            alert('Torque should be between 0-100 Nm');
            return false;
        }
        if (data.tool_wear < 0 || data.tool_wear > 300) {
            alert('Tool wear should be between 0-300 minutes');
            return false;
        }
        return true;
    }

    function displayResults(prediction, inputData) {
        const statusIcon = document.getElementById('statusIcon');
        const statusTitle = document.getElementById('statusTitle');
        const statusMessage = document.getElementById('statusMessage');
        const resultStatus = document.getElementById('resultStatus');
        
        const failureProbability = document.getElementById('failureProbability');
        const confidenceScore = document.getElementById('confidenceScore');
        const riskBadge = document.getElementById('riskBadge');
        const probabilityBar = document.getElementById('probabilityBar');
        const confidenceBar = document.getElementById('confidenceBar');

        // Set status based on prediction
        if (prediction.will_fail) {
            statusIcon.innerHTML = '⚠️';
            statusTitle.textContent = 'MACHINE FAILURE PREDICTED';
            statusMessage.textContent = 'The machine is likely to fail. Immediate maintenance recommended!';
            resultStatus.className = 'result-status failure';
        } else {
            statusIcon.innerHTML = '✅';
            statusTitle.textContent = 'MACHINE IN GOOD CONDITION';
            statusMessage.textContent = 'The machine is operating normally. No immediate action required.';
            resultStatus.className = 'result-status success';
        }

        // Set metrics
        const probability = (prediction.failure_probability * 100).toFixed(1);
        const confidence = prediction.confidence.toFixed(1);

        failureProbability.textContent = probability + '%';
        confidenceScore.textContent = confidence + '%';

        // Set progress bars
        probabilityBar.style.width = probability + '%';
        confidenceBar.style.width = confidence + '%';

        // Color code probability bar
        if (probability >= 80) {
            probabilityBar.style.backgroundColor = '#e74c3c';
        } else if (probability >= 60) {
            probabilityBar.style.backgroundColor = '#e67e22';
        } else if (probability >= 40) {
            probabilityBar.style.backgroundColor = '#f39c12';
        } else {
            probabilityBar.style.backgroundColor = '#27ae60';
        }

        // Set risk badge
        const riskLevel = prediction.risk_level.toUpperCase();
        riskBadge.textContent = riskLevel;
        riskBadge.className = 'metric-badge risk-' + prediction.risk_level;

        // Display input parameters
        displayInputSummary(inputData);

        // Show results
        resultCard.style.display = 'block';
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function displayInputSummary(data) {
        const detailsGrid = document.getElementById('detailsGrid');
        const typeLabels = { 'L': 'Low Quality', 'M': 'Medium Quality', 'H': 'High Quality' };
        
        detailsGrid.innerHTML = `
            <div class="detail-item">
                <span class="detail-label">Type:</span>
                <span class="detail-value">${typeLabels[data.type] || data.type}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Air Temperature:</span>
                <span class="detail-value">${data.air_temp} K</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Process Temperature:</span>
                <span class="detail-value">${data.process_temp} K</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Rotational Speed:</span>
                <span class="detail-value">${data.rotational_speed} rpm</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Torque:</span>
                <span class="detail-value">${data.torque} Nm</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Tool Wear:</span>
                <span class="detail-value">${data.tool_wear} min</span>
            </div>
        `;
    }

    function loadSampleData() {
        // Load sample data - good condition
        const samples = [
            {
                type: 'L',
                air_temp: 298.5,
                process_temp: 308.7,
                rotational_speed: 1500,
                torque: 40.0,
                tool_wear: 50
            },
            {
                type: 'M',
                air_temp: 305.0,
                process_temp: 315.0,
                rotational_speed: 1200,
                torque: 60.0,
                tool_wear: 200
            },
            {
                type: 'H',
                air_temp: 299.0,
                process_temp: 309.0,
                rotational_speed: 1800,
                torque: 35.0,
                tool_wear: 30
            }
        ];

        const sample = samples[Math.floor(Math.random() * samples.length)];

        document.getElementById('type').value = sample.type;
        document.getElementById('air_temp').value = sample.air_temp;
        document.getElementById('process_temp').value = sample.process_temp;
        document.getElementById('rotational_speed').value = sample.rotational_speed;
        document.getElementById('torque').value = sample.torque;
        document.getElementById('tool_wear').value = sample.tool_wear;
    }

    async function loadModelInfo() {
        try {
            const response = await fetch('/api/model-info');
            const data = await response.json();
            
            const modelInfoContent = document.getElementById('modelInfoContent');
            
            if (data.status === 'loaded') {
                modelInfoContent.innerHTML = `
                    <div class="model-detail">
                        <strong>Status:</strong> <span class="status-badge active">Active</span>
                    </div>
                    <div class="model-detail">
                        <strong>Model Type:</strong> ${data.model_type}
                    </div>
                    <div class="model-detail">
                        <strong>Features:</strong> ${data.feature_count} input parameters
                    </div>
                    <div class="model-detail">
                        <strong>Accuracy:</strong> ~98.6% on test data
                    </div>
                `;
            } else {
                modelInfoContent.innerHTML = '<p>Model information unavailable</p>';
            }
        } catch (error) {
            console.error('Error loading model info:', error);
        }
    }

    function downloadReport() {
        if (!lastPrediction) return;

        const report = {
            timestamp: lastPrediction.timestamp,
            input_parameters: lastPrediction.input,
            prediction: lastPrediction.result
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `machine_prediction_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function showError(message) {
        alert(message);
    }
});
