# Predictive Maintenance System

A comprehensive web-based predictive maintenance system for industrial equipment that uses sensor data to predict failures before they happen.

## 🎯 Features

- **Real-Time Monitoring**: Live sensor data visualization for vibration, temperature, and pressure
- **Health Scoring**: Equipment health scores with status indicators (Healthy, Warning, Critical)
- **Failure Prediction**: ML-based predictions with 2-48 hour lead time
- **Anomaly Detection**: Automatic detection of abnormal sensor readings
- **Alert System**: Multi-level alerts (Critical, Warning, Info) with real-time notifications
- **Interactive Dashboard**: Beautiful, responsive UI with Plotly charts
- **User Authentication**: Secure login system with session management
- **Historical Analysis**: View sensor trends over multiple time periods

## 🏗️ Architecture

```
Predictive Maintenance System/
├── app.py                      # Flask application & API endpoints
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   ├── login.html             # Login page
│   └── dashboard.html         # Main dashboard
├── static/
│   ├── css/
│   │   ├── login.css         # Login page styles
│   │   └── dashboard.css     # Dashboard styles
│   └── js/
│       ├── login.js          # Login functionality
│       └── dashboard.js      # Dashboard interactions & charts
└── ml_models/
    ├── __init__.py
    ├── data_simulator.py      # Sensor data generation
    ├── health_calculator.py   # Equipment health scoring
    ├── predictor.py           # Failure prediction models
    ├── anomaly_detector.py    # Anomaly detection algorithms
    └── alert_system.py        # Alert generation & management
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\Sreemsun\Tool analysis"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to: `http://localhost:5000`

### Default Login Credentials

- **Admin User**
  - Username: `admin`
  - Password: `admin123`

- **Operator User**
  - Username: `operator`
  - Password: `operator123`

## 📊 Dashboard Overview

### Health Score Cards
- **Pump A-01**: Industrial pump monitoring
- **Motor B-02**: Electric motor monitoring  
- **HVAC C-03**: HVAC system monitoring
- **System Status**: Overall equipment status summary

### Real-Time Sensor Data
- **Temperature**: Monitor temperature variations (°C)
- **Pressure**: Track pressure levels (PSI)
- **Vibration**: Analyze vibration patterns (mm/s)

### Failure Predictions
- Equipment-specific failure predictions
- Time-to-failure estimates (2-48 hours ahead)
- Confidence scores for each prediction
- Detailed failure analysis

### Anomaly Detection
- Real-time anomaly detection using Z-score method
- Visual markers for detected anomalies
- Pattern analysis and clustering

### Alert System
- **Critical Alerts**: Immediate action required
- **Warning Alerts**: Attention needed
- **Info Alerts**: Informational notifications

## 🔧 Technical Implementation

### Backend (Flask + Python)

**API Endpoints:**
- `POST /login` - User authentication
- `GET /logout` - User logout
- `GET /dashboard` - Main dashboard page
- `GET /api/sensor-data` - Real-time sensor data
- `GET /api/health-score` - Equipment health scores
- `GET /api/predictions` - Failure predictions
- `GET /api/anomalies` - Anomaly detection results
- `GET /api/alerts` - Active alerts
- `GET /api/historical-data` - Historical sensor data

### Frontend (HTML/CSS/JavaScript)

**Technologies:**
- Vanilla JavaScript for interactivity
- Plotly.js for interactive charts
- CSS Grid & Flexbox for responsive layout
- Custom animations and transitions

### Machine Learning Models

**1. Data Simulation**
- Simulates realistic sensor data with noise
- Adds periodic patterns and trends
- Injects anomalies for testing

**2. Health Scoring**
- Multi-factor health calculation
- Weighted scoring based on sensor readings
- Status categorization (Healthy/Warning/Critical)

**3. Failure Prediction**
- Trend analysis on sensor history
- Risk score calculation
- Time-to-failure estimation
- Confidence scoring

**4. Anomaly Detection**
- Z-score based detection
- IQR (Interquartile Range) method
- Moving average analysis
- Pattern recognition

**5. Alert Generation**
- Threshold-based alerts
- Multi-level severity system
- Alert prioritization
- Statistics and analytics

## 📈 Success Metrics

The system tracks three key metrics:

1. **Prediction Accuracy**
   - Precision/Recall of failure events
   - Confusion matrix analysis
   - ROC curve evaluation

2. **Lead Time**
   - Average prediction lead time: 2-48 hours
   - Early warning capability
   - Prediction horizon optimization

3. **False Alarm Rate**
   - Monitoring false positive rate
   - Alert threshold tuning
   - Severity categorization accuracy

## 🔐 Security Features

- Session-based authentication
- Password hashing (SHA-256)
- CSRF protection (Flask built-in)
- Secure cookie handling
- Login rate limiting (can be enhanced)

## 🎨 Customization

### Adding New Equipment

Edit `ml_models/health_calculator.py`:
```python
base_scores = {
    'pump': 85,
    'motor': 92,
    'hvac': 78,
    'new_equipment': 90  # Add here
}
```

### Adjusting Alert Thresholds

Edit `ml_models/alert_system.py`:
```python
thresholds = {
    'vibration': {'warning': 15, 'critical': 20},
    'temperature': {'warning': 85, 'critical': 95},
    'pressure': {'warning': 110, 'critical': 120}
}
```

### Changing Update Frequency

Edit `static/js/dashboard.js`:
```javascript
// Update every 5 seconds (change as needed)
updateInterval = setInterval(() => {
    loadAllData();
}, 5000);  // milliseconds
```

## 🔮 Future Enhancements

1. **Real Data Integration**
   - Connect to actual IoT sensors via MQTT
   - NASA bearing dataset integration
   - Real-time streaming data pipeline

2. **Advanced ML Models**
   - LSTM neural networks for time-series
   - Prophet for seasonal decomposition
   - Isolation Forest for anomaly detection
   - XGBoost for failure classification

3. **Enhanced Features**
   - Email/SMS notifications
   - Mobile app integration
   - Historical data export (CSV/Excel)
   - Maintenance scheduling system
   - Multi-site support

4. **Production Readiness**
   - PostgreSQL database integration
   - Redis for caching
   - Docker containerization
   - Load balancing
   - Comprehensive unit tests

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Module Not Found Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Prophet Installation Issues
```bash
# On Windows, install Prophet dependencies first
pip install pystan==2.19.1.1
pip install prophet
```

## 📝 License

This project is created for educational and demonstration purposes.

## 👤 Author

Created as part of the Predictive Maintenance System project.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

For support and questions, please refer to the project documentation.

---

**Built with ❤️ using Flask, Python, and modern web technologies**
