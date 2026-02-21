# Backend

This folder contains all backend application code for the Predictive Maintenance System.

## Contents

- **app.py**: Main Flask application with all API endpoints and routes
- **database.py**: Database operations for storing machine readings and predictions
- **ml_models/**: Machine learning modules
  - `predictor.py`: ML prediction engine
  - `alert_system.py`: Alert notification system
  - `anomaly_detector.py`: Anomaly detection algorithms
  - `health_calculator.py`: Health score calculations
  - `data_simulator.py`: Data generation for testing
- **trained_models/**: Trained ML model files
  - Random Forest and Gradient Boosting models
  - Scaler and Label Encoder
  - Feature columns configuration

## Running the Backend

From the backend directory:
```bash
python app.py
```

The server will start on the configured port (default: 5000).

## API Endpoints

- `/login` - User authentication
- `/dashboard` - Main dashboard
- `/monitor` - Real-time monitoring
- `/predict` - Prediction interface
- `/api/ml-predict` - ML prediction API
- `/api/readings` - Get machine readings
- And more...

See [API Documentation](../docs/API_DOCUMENTATION.md) for complete details.
