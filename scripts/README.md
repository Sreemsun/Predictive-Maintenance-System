# Scripts

This folder contains utility scripts for training, testing, and simulating the Predictive Maintenance System.

## Scripts

### train_model.py
Trains the machine learning models using the dataset.

**Usage:**
```bash
python train_model.py
```

**What it does:**
- Loads data from `../data/dataset.csv`
- Preprocesses and prepares features
- Trains Random Forest and Gradient Boosting models
- Evaluates model performance
- Saves trained models to `../backend/trained_models/`

### test_prediction.py
Tests the prediction API with sample data.

**Usage:**
```bash
python test_prediction.py
```

**What it does:**
- Makes API calls to the running Flask server
- Tests single predictions with sample data
- Tests batch predictions from the dataset
- Displays results and accuracy metrics

**Note:** Ensure the backend server is running before executing this script.

### continuous_data_sender.py
Simulates continuous machine data streaming to the API.

**Usage:**
```bash
python continuous_data_sender.py
```

**What it does:**
- Logs into the system
- Continuously generates and sends machine sensor data
- Simulates real-world IoT device behavior
- Useful for testing monitoring and alerting features

**Configuration:**
- API_BASE_URL: Set to your Flask server address
- USERNAME/PASSWORD: Admin credentials
- Adjust delay and parameters as needed

## Running Scripts

All scripts should be run from the `scripts` directory:

```bash
cd scripts
python script_name.py
```

## Dependencies

Scripts use the same dependencies as the main application. Ensure you have installed all requirements:

```bash
pip install -r ../requirements.txt
```
