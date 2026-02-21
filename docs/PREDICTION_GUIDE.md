# Machine Health Prediction Guide

## 🎯 Overview
Your predictive maintenance system now includes an AI-powered machine health prediction feature that uses a trained machine learning model (Gradient Boosting Classifier) with **98.6% accuracy** on test data.

## 🚀 How to Use

### Step 1: Start the Application
```bash
python app.py
```
The application will start on `http://localhost:5000` or `http://0.0.0.0:5000`

### Step 2: Login
- **Default credentials:**
  - Username: `admin`
  - Password: `admin123`
  
  OR
  
  - Username: `operator`
  - Password: `operator123`

### Step 3: Navigate to Prediction Page
- From the dashboard, click the **"🤖 AI Prediction"** button in the sidebar
- Or click the **"Try AI Prediction Now →"** button in the banner
- Or directly navigate to: `http://localhost:5000/predict`

### Step 4: Enter Machine Parameters

The prediction form requires 6 parameters:

1. **Machine Type**: Select from dropdown
   - L (Low Quality)
   - M (Medium Quality)  
   - H (High Quality)

2. **Air Temperature (K)**: Normal range 295-305 K
   - Example: 298.5

3. **Process Temperature (K)**: Normal range 305-315 K
   - Example: 308.7

4. **Rotational Speed (rpm)**: Normal range 1200-2500 rpm
   - Example: 1500

5. **Torque (Nm)**: Normal range 20-70 Nm
   - Example: 40.0

6. **Tool Wear (minutes)**: 0-240 minutes
   - Example: 50

### Step 5: Get Prediction
- Click **"🔮 Predict Machine Health"** button
- The system will analyze the data and provide:
  - ✅ **Overall Status**: Good Condition or Failure Predicted
  - 📊 **Failure Probability**: Percentage likelihood of failure
  - 🎯 **Confidence Score**: Model's confidence in the prediction
  - 🚨 **Risk Level**: LOW, MEDIUM, HIGH, or CRITICAL

## 📋 Example Scenarios

### Good Condition Example
```
Type: L (Low Quality)
Air Temperature: 298.5 K
Process Temperature: 308.7 K
Rotational Speed: 1500 rpm
Torque: 40.0 Nm
Tool Wear: 50 min

Expected Result: MACHINE IN GOOD CONDITION ✅
```

### High Risk Example
```
Type: M (Medium Quality)
Air Temperature: 305.0 K
Process Temperature: 315.0 K
Rotational Speed: 1200 rpm
Torque: 60.0 Nm
Tool Wear: 200 min

Expected Result: MACHINE FAILURE PREDICTED ⚠️
```

## 🛠️ Features

### Quick Actions
- **Load Sample Data**: Click to automatically fill form with sample values
- **Reset Form**: Clear all inputs and start fresh
- **Download Report**: Save prediction results as JSON file
- **New Prediction**: Start a new prediction after viewing results

### API Endpoints
You can also use the prediction API programmatically:

#### POST `/api/ml-predict`
```bash
curl -X POST http://localhost:5000/api/ml-predict \
  -H "Content-Type: application/json" \
  -d '{
    "type": "L",
    "air_temp": 298.5,
    "process_temp": 308.7,
    "rotational_speed": 1500,
    "torque": 40.0,
    "tool_wear": 50
  }'
```

#### GET `/api/model-info`
Get information about the loaded ML model:
```bash
curl http://localhost:5000/api/model-info
```

#### GET `/api/batch-predict?samples=10`
Test predictions on random samples from the dataset:
```bash
curl http://localhost:5000/api/batch-predict?samples=10
```

## 📊 Understanding the Results

### Risk Levels
- **LOW**: Failure probability < 40% (Green)
- **MEDIUM**: Failure probability 40-60% (Yellow)
- **HIGH**: Failure probability 60-80% (Orange)
- **CRITICAL**: Failure probability > 80% (Red)

### Confidence Score
- Indicates how certain the model is about its prediction
- Higher confidence = more reliable prediction
- Based on gradient boosting probability distributions

### Failure Probability
- Calculated by the trained Gradient Boosting model
- Shows percentage likelihood of machine failure
- Takes into account all 6 input parameters

## 🔧 Model Information

- **Algorithm**: Gradient Boosting Classifier
- **Training Accuracy**: 98.6%
- **Training Dataset**: 10,000 machine records
- **Features**: 6 input parameters
- **Classes**: Binary (Fail / No Fail)
- **Location**: `trained_models/` directory

## 🎓 Training Your Own Model

To retrain the model with updated data:

```bash
# Update dataset.csv with new data
python train_model.py
```

This will:
1. Load the dataset
2. Preprocess the data
3. Train both Random Forest and Gradient Boosting models
4. Evaluate performance
5. Save the best model

## 🔍 Testing

Run the test suite to verify model performance:

```bash
python test_prediction.py
```

This will test:
- Model loading
- Single predictions
- Batch predictions
- Accuracy metrics

## 💡 Tips

1. **Tool Wear**: Higher values (>150 min) significantly increase failure risk
2. **Temperature**: Process temp >313K combined with high torque = high risk
3. **Speed**: Very low (<1200 rpm) or very high (>2500 rpm) speeds increase risk
4. **Torque**: Values >55 Nm especially with high tool wear = danger zone
5. **Quality**: Low quality (L) machines are more susceptible to failures

## 🆘 Troubleshooting

### Model Not Loading
- Ensure `python train_model.py` was run successfully
- Check that `trained_models/` directory exists
- Verify all .pkl files are present

### Prediction Errors
- Check that all form fields are filled
- Ensure values are within acceptable ranges
- Check browser console for JavaScript errors

### API Issues
- Verify you're logged in (session active)
- Check Flask server is running
- Look at Flask console for error messages

## 📞 Support

For issues or questions:
1. Check Flask console output for errors
2. Review browser console (F12) for JavaScript errors
3. Verify all required packages are installed
4. Ensure dataset.csv is in the root directory

---

**Your ML model is now ready to predict machine failures in real-time! 🎉**
