"""
Test the trained ML model with sample predictions
"""

from ml_models.predictor import predict_machine_failure, batch_predict_from_csv, get_model_info

def test_single_prediction():
    """Test a single prediction"""
    print("="*60)
    print("TEST 1: Single Machine Prediction")
    print("="*60)
    
    # Test case 1: Low risk machine
    machine_data_1 = {
        'type': 'L',
        'air_temp': 298.5,
        'process_temp': 308.7,
        'rotational_speed': 1500,
        'torque': 40.0,
        'tool_wear': 50
    }
    
    print("\nMachine Configuration 1 (Expected: Low Risk):")
    print(f"  Type: {machine_data_1['type']}")
    print(f"  Air Temperature: {machine_data_1['air_temp']} K")
    print(f"  Process Temperature: {machine_data_1['process_temp']} K")
    print(f"  Rotational Speed: {machine_data_1['rotational_speed']} rpm")
    print(f"  Torque: {machine_data_1['torque']} Nm")
    print(f"  Tool Wear: {machine_data_1['tool_wear']} min")
    
    result_1 = predict_machine_failure(machine_data_1)
    
    print("\nPrediction Result:")
    print(f"  Will Fail: {result_1['will_fail']}")
    print(f"  Failure Probability: {result_1['failure_probability']:.2%}")
    print(f"  Confidence: {result_1['confidence']:.1f}%")
    print(f"  Risk Level: {result_1['risk_level'].upper()}")
    
    # Test case 2: High risk machine
    print("\n" + "-"*60)
    
    machine_data_2 = {
        'type': 'M',
        'air_temp': 305.0,
        'process_temp': 315.0,
        'rotational_speed': 1200,
        'torque': 60.0,
        'tool_wear': 200
    }
    
    print("\nMachine Configuration 2 (Expected: Higher Risk):")
    print(f"  Type: {machine_data_2['type']}")
    print(f"  Air Temperature: {machine_data_2['air_temp']} K")
    print(f"  Process Temperature: {machine_data_2['process_temp']} K")
    print(f"  Rotational Speed: {machine_data_2['rotational_speed']} rpm")
    print(f"  Torque: {machine_data_2['torque']} Nm")
    print(f"  Tool Wear: {machine_data_2['tool_wear']} min")
    
    result_2 = predict_machine_failure(machine_data_2)
    
    print("\nPrediction Result:")
    print(f"  Will Fail: {result_2['will_fail']}")
    print(f"  Failure Probability: {result_2['failure_probability']:.2%}")
    print(f"  Confidence: {result_2['confidence']:.1f}%")
    print(f"  Risk Level: {result_2['risk_level'].upper()}")

def test_batch_prediction():
    """Test batch predictions from dataset"""
    print("\n" + "="*60)
    print("TEST 2: Batch Prediction from Dataset")
    print("="*60)
    
    results = batch_predict_from_csv('../data/dataset.csv', num_samples=20)
    
    print(f"\nTested {len(results)} samples from dataset:")
    print(f"\n{'Product ID':<12} {'Actual':>8} {'Predicted':>10} {'Probability':>12} {'Risk Level':>12}")
    print("-"*60)
    
    correct = 0
    for result in results:
        actual = "FAIL" if result['actual_failure'] == 1 else "OK"
        predicted = "FAIL" if result['will_fail'] else "OK"
        if result['will_fail'] == result['actual_failure']:
            correct += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"{result['product_id']:<12} {actual:>8} {predicted:>10} {result['failure_probability']:>11.1%} {result['risk_level']:>12} {status}")
    
    accuracy = (correct / len(results)) * 100
    print("-"*60)
    print(f"Accuracy: {correct}/{len(results)} = {accuracy:.1f}%")

def test_model_info():
    """Test model information retrieval"""
    print("\n" + "="*60)
    print("TEST 3: Model Information")
    print("="*60)
    
    info = get_model_info()
    
    print("\nLoaded Model Details:")
    for key, value in info.items():
        print(f"  {key}: {value}")

def main():
    """Run all tests"""
    print("\n")
    print("#"*60)
    print("#  PREDICTIVE MAINTENANCE MODEL - TEST SUITE")
    print("#"*60)
    
    try:
        test_model_info()
        test_single_prediction()
        test_batch_prediction()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYour model is ready to use!")
        print("Start the Flask app with: python app.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("Please check if the model was trained successfully.")

if __name__ == "__main__":
    main()
