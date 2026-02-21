# Continuous Monitoring API Documentation

## 🚀 Overview

This API enables continuous data ingestion, real-time predictions, and historical data visualization for predictive maintenance. All data is stored in a SQLite database for analysis and plotting.

## 📋 Base URL

```
http://localhost:5000
```

## 🔐 Authentication

All API endpoints require authentication. You must be logged in to use them.

### Login

**POST** `/login`

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful"
}
```

---

## 🤖 Machine Management

### Register a Machine

**POST** `/api/machines/register`

Register a new machine for monitoring.

**Request Body:**
```json
{
  "machine_id": "PUMP-001",
  "machine_name": "Hydraulic Pump A",
  "machine_type": "L",
  "location": "Factory Floor A"
}
```

**Parameters:**
- `machine_id` (string, required): Unique identifier for the machine
- `machine_name` (string, required): Human-readable name
- `machine_type` (string, required): L (Low), M (Medium), or H (High) quality
- `location` (string, optional): Physical location

**Response:**
```json
{
  "success": true,
  "message": "Machine PUMP-001 registered successfully"
}
```

### List All Machines

**GET** `/api/machines/list`

Get all registered machines.

**Response:**
```json
{
  "success": true,
  "machines": [
    {
      "id": 1,
      "machine_id": "PUMP-001",
      "machine_name": "Hydraulic Pump A",
      "machine_type": "L",
      "location": "Factory Floor A",
      "status": "active",
      "total_readings": 150,
      "last_reading": "2024-01-15T14:30:00"
    }
  ],
  "total": 1
}
```

---

## 📥 Data Ingestion

### Send Single Reading

**POST** `/api/data/ingest`

Send a single machine reading and get instant prediction.

**Request Body:**
```json
{
  "machine_id": "PUMP-001",
  "type": "L",
  "air_temp": 298.5,
  "process_temp": 308.7,
  "rotational_speed": 1500,
  "torque": 40.0,
  "tool_wear": 50,
  "timestamp": "2024-01-15T14:30:00"
}
```

**Parameters:**
- `machine_id` (string, required): Machine identifier
- `type` (string, required): Machine type (L/M/H)
- `air_temp` (float, required): Air temperature in Kelvin (290-310)
- `process_temp` (float, required): Process temperature in Kelvin (300-320)
- `rotational_speed` (int, required): Speed in rpm (1000-3000)
- `torque` (float, required): Torque in Nm (0-100)
- `tool_wear` (int, required): Tool wear in minutes (0-300)
- `timestamp` (string, optional): ISO format timestamp

**Response:**
```json
{
  "success": true,
  "reading_id": 123,
  "prediction_id": 456,
  "prediction": {
    "will_fail": false,
    "failure_probability": 0.05,
    "confidence": 95.0,
    "risk_level": "low"
  },
  "timestamp": "2024-01-15T14:30:00"
}
```

### Send Batch Readings

**POST** `/api/data/batch-ingest`

Send multiple readings at once for efficient bulk ingestion.

**Request Body:**
```json
{
  "readings": [
    {
      "machine_id": "PUMP-001",
      "type": "L",
      "air_temp": 298.5,
      "process_temp": 308.7,
      "rotational_speed": 1500,
      "torque": 40.0,
      "tool_wear": 50
    },
    {
      "machine_id": "MOTOR-001",
      "type": "M",
      "air_temp": 299.0,
      "process_temp": 309.0,
      "rotational_speed": 1600,
      "torque": 45.0,
      "tool_wear": 75
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "processed": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "machine_id": "PUMP-001",
      "reading_id": 123,
      "prediction_id": 456,
      "success": true
    }
  ]
}
```

---

## 📊 Data Retrieval

### Get Machine History

**GET** `/api/data/history/{machine_id}?hours=24&limit=1000`

Get historical readings and predictions for a specific machine.

**Query Parameters:**
- `hours` (int, optional): Time window in hours (default: 24)
- `limit` (int, optional): Maximum number of records (default: 1000)

**Response:**
```json
{
  "success": true,
  "machine_id": "PUMP-001",
  "data": [
    {
      "id": 123,
      "machine_type": "L",
      "air_temperature": 298.5,
      "process_temperature": 308.7,
      "rotational_speed": 1500,
      "torque": 40.0,
      "tool_wear": 50,
      "timestamp": "2024-01-15T14:30:00",
      "will_fail": 0,
      "failure_probability": 0.05,
      "confidence": 95.0,
      "risk_level": "low"
    }
  ],
  "count": 1,
  "hours": 24
}
```

### Get Recent Predictions

**GET** `/api/data/recent-predictions?limit=50`

Get recent predictions across all machines.

**Query Parameters:**
- `limit` (int, optional): Maximum number of predictions (default: 50)

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "id": 456,
      "machine_id": "PUMP-001",
      "will_fail": 0,
      "failure_probability": 0.05,
      "confidence": 95.0,
      "risk_level": "low",
      "timestamp": "2024-01-15T14:30:00"
    }
  ],
  "count": 1
}
```

---

## 🚨 Alerts Management

### Get Active Alerts

**GET** `/api/alerts/active?limit=50`

Get all unacknowledged alerts.

**Response:**
```json
{
  "success": true,
  "alerts": [
    {
      "id": 1,
      "machine_id": "PUMP-001",
      "machine_name": "Hydraulic Pump A",
      "alert_type": "failure_prediction",
      "severity": "critical",
      "message": "Machine PUMP-001 predicted to fail with 85.5% probability",
      "acknowledged": 0,
      "timestamp": "2024-01-15T14:30:00"
    }
  ],
  "count": 1
}
```

### Acknowledge Alert

**POST** `/api/alerts/acknowledge/{alert_id}`

Mark an alert as acknowledged.

**Response:**
```json
{
  "success": true,
  "message": "Alert 1 acknowledged"
}
```

---

## 📈 Statistics & Comparison

### Get Statistics

**GET** `/api/statistics?machine_id=PUMP-001&hours=24`

Get statistical summary for a machine or all machines.

**Query Parameters:**
- `machine_id` (string, optional): Specific machine (if omitted, returns global stats)
- `hours` (int, optional): Time window in hours (default: 24)

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_readings": 150,
    "avg_failure_prob": 0.15,
    "max_failure_prob": 0.85,
    "failure_predictions": 5,
    "critical_count": 2,
    "high_count": 3
  },
  "machine_id": "PUMP-001",
  "hours": 24
}
```

### Compare Machines

**GET** `/api/compare?machine_ids=PUMP-001&machine_ids=MOTOR-001&hours=24`

Compare performance metrics across multiple machines.

**Query Parameters:**
- `machine_ids` (array, required): List of machine IDs to compare
- `hours` (int, optional): Time window (default: 24)

**Response:**
```json
{
  "success": true,
  "comparison": [
    {
      "machine_id": "PUMP-001",
      "machine_name": "Hydraulic Pump A",
      "avg_failure_prob": 0.12,
      "max_failure_prob": 0.45,
      "avg_air_temp": 298.5,
      "avg_process_temp": 308.7,
      "avg_speed": 1500,
      "avg_torque": 40.0,
      "avg_tool_wear": 75.5,
      "reading_count": 150
    }
  ],
  "machine_count": 1,
  "hours": 24
}
```

---

## 🔍 Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (missing/invalid parameters)
- `401`: Unauthorized (not logged in)
- `404`: Not Found
- `409`: Conflict (e.g., machine already registered)
- `500`: Internal Server Error

---

## 💡 Usage Examples

### Python Example

```python
import requests

# Login
session = requests.Session()
session.post('http://localhost:5000/login', 
             json={'username': 'admin', 'password': 'admin123'})

# Register machine
session.post('http://localhost:5000/api/machines/register',
             json={
                 'machine_id': 'PUMP-001',
                 'machine_name': 'Hydraulic Pump A',
                 'machine_type': 'L'
             })

# Send reading
response = session.post('http://localhost:5000/api/data/ingest',
                       json={
                           'machine_id': 'PUMP-001',
                           'type': 'L',
                           'air_temp': 298.5,
                           'process_temp': 308.7,
                           'rotational_speed': 1500,
                           'torque': 40.0,
                           'tool_wear': 50
                       })

print(response.json())
```

### cURL Example

```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# Send reading
curl -X POST http://localhost:5000/api/data/ingest \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "machine_id": "PUMP-001",
    "type": "L",
    "air_temp": 298.5,
    "process_temp": 308.7,
    "rotational_speed": 1500,
    "torque": 40.0,
    "tool_wear": 50
  }'
```

### JavaScript Example

```javascript
// Login
await fetch('http://localhost:5000/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  }),
  credentials: 'include'
});

// Send reading
const response = await fetch('http://localhost:5000/api/data/ingest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    machine_id: 'PUMP-001',
    type: 'L',
    air_temp: 298.5,
    process_temp: 308.7,
    rotational_speed: 1500,
    torque: 40.0,
    tool_wear: 50
  })
});

const data = await response.json();
console.log(data);
```

---

## 📊 Web Interface

Access the real-time monitoring dashboard:

```
http://localhost:5000/monitor
```

Features:
- ✅ Machine registration and management
- ✅ Single and bulk data ingestion
- ✅ Live predictions feed with auto-refresh
- ✅ Interactive charts and visualizations
- ✅ Machine performance comparison
- ✅ Active alerts management

---

## 🗄️ Database Structure

Data is stored in SQLite database: `predictive_maintenance.db`

**Tables:**
- `machines`: Registered machines
- `machine_readings`: All sensor readings
- `predictions`: ML model predictions
- `alerts`: Generated alerts

**Data Retention:**
- All historical data is retained
- Query with time filters for recent data
- Database can be backed up easily (single file)

---

## 🔄 Continuous Integration

For IoT devices or data pipelines, use the batch ingestion endpoint for efficient data streaming:

1. **Collect readings** in memory buffer
2. **Send batch** every N seconds or M readings
3. **Handle responses** and retry on failure
4. **Monitor alerts** via alerts API

See `continuous_data_sender.py` for a complete example.

---

## 🎯 Best Practices

1. **Use batch ingestion** for high-frequency data (>1 reading/second)
2. **Set timestamps** explicitly for accurate time-series analysis
3. **Register machines** before sending data
4. **Monitor alerts API** for critical predictions
5. **Use machine comparison** to identify anomalies across fleet
6. **Keep sessions alive** or handle re-authentication

---

## 📞 Support

For issues or questions:
- Check Flask console for error logs
- Verify database file exists: `predictive_maintenance.db`
- Ensure all required packages are installed
- Test with `continuous_data_sender.py` example

**Model Accuracy: 98.6%** on test dataset
