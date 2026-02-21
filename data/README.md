# Data

This folder contains datasets used for training and testing the Predictive Maintenance System.

## Files

### dataset.csv
The main training dataset containing machine sensor readings and failure labels.

**Columns:**
- Machine identification (Product ID, Type)
- Sensor readings (Air temperature, Process temperature, Rotational speed, Torque, Tool wear)
- Failure indicators (Machine failure, Various failure types)

**Usage:**
- Used by `../scripts/train_model.py` for training ML models
- Source for batch predictions in testing
- Reference data for simulations

## Data Format

The dataset follows a structured CSV format with numerical and categorical features representing typical industrial IoT sensor data.

## Adding New Data

To add new training data:
1. Ensure the CSV follows the same column structure
2. Update the filename reference in training scripts if needed
3. Retrain models using `python ../scripts/train_model.py`

## Data Privacy

If using real production data, ensure:
- Sensitive information is anonymized
- Data security policies are followed
- Appropriate access controls are in place
