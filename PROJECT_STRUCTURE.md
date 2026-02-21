# Project Structure

This document describes the organized folder structure of the Predictive Maintenance System.

## Folder Organization

```
Tool analysis/
│
├── backend/                      # Backend application code
│   ├── app.py                    # Main Flask application
│   ├── database.py               # Database operations
│   ├── ml_models/                # Machine learning modules
│   │   ├── __init__.py
│   │   ├── alert_system.py       # Alert notification system
│   │   ├── anomaly_detector.py   # Anomaly detection algorithms
│   │   ├── data_simulator.py     # Data generation for testing
│   │   ├── health_calculator.py  # Health score calculations
│   │   └── predictor.py          # ML prediction engine
│   └── trained_models/           # Trained ML model files
│       ├── random_forest_model.pkl
│       ├── gradient_boosting_model.pkl
│       ├── scaler.pkl
│       ├── label_encoder.pkl
│       └── feature_columns.txt
│
├── frontend/                     # Frontend assets
│   ├── static/                   # Static files (CSS, JS)
│   │   ├── css/                  # Stylesheets
│   │   │   ├── dashboard.css
│   │   │   ├── login.css
│   │   │   ├── monitor.css
│   │   │   └── predict.css
│   │   └── js/                   # JavaScript files
│   │       ├── dashboard.js
│   │       ├── login.js
│   │       ├── monitor.js
│   │       ├── predict.js
│   │       └── register.js
│   └── templates/                # HTML templates
│       ├── dashboard.html
│       ├── login.html
│       ├── monitor.html
│       ├── predict.html
│       └── register.html
│
├── scripts/                      # Utility and training scripts
│   ├── train_model.py            # Model training script
│   ├── test_prediction.py        # Prediction testing script
│   └── continuous_data_sender.py # Continuous monitoring simulator
│
├── data/                         # Data files
│   └── dataset.csv               # Training dataset
│
├── docs/                         # Documentation
│   ├── API_DOCUMENTATION.md      # API documentation
│   ├── CONTINUOUS_MONITORING_GUIDE.md
│   ├── PREDICTION_GUIDE.md
│   ├── PROJECT_OVERVIEW.md
│   ├── SETUP_GUIDE.md
│   └── SYSTEM_SUMMARY.md
│
├── predictive_maintenance.db     # SQLite database
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
└── README.md                     # Main README

```

## Running the Application

### Start the Backend Server
```bash
cd backend
python app.py
```

### Train the ML Model
```bash
cd scripts
python train_model.py
```

### Test Predictions
```bash
cd scripts
python test_prediction.py
```

### Run Continuous Monitoring
```bash
cd scripts
python continuous_data_sender.py
```

## Key Benefits of This Structure

1. **Separation of Concerns**: Frontend, backend, and scripts are clearly separated
2. **Easy Navigation**: Each folder has a specific purpose
3. **Scalability**: Easy to add new modules or features
4. **Maintainability**: Clear organization makes maintenance easier
5. **Documentation**: All docs in one place for easy reference

## Notes

- The backend application automatically references the correct frontend folders
- All scripts have been updated to use correct relative paths
- Database file remains in the root for easy access
- Trained models are stored within the backend structure for logical grouping
