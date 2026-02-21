"""
Train ML Model for Predictive Maintenance
This script trains a machine learning model to predict machine failures
using the dataset.csv file
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

def load_and_prepare_data(filepath='../data/dataset.csv'):
    """Load and prepare the dataset"""
    print("Loading dataset...")
    df = pd.read_csv(filepath)
    
    print(f"Dataset shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    # Check for missing values
    print(f"\nMissing values:\n{df.isnull().sum()}")
    
    # Check class distribution
    print(f"\nMachine failure distribution:")
    print(df['Machine failure'].value_counts())
    
    return df

def preprocess_data(df):
    """Preprocess the data for model training"""
    print("\nPreprocessing data...")
    
    # Encode categorical variable 'Type' (L, M, H)
    le = LabelEncoder()
    df['Type_encoded'] = le.fit_transform(df['Type'])
    
    # Select features for prediction
    feature_columns = [
        'Type_encoded',
        'Air temperature [K]',
        'Process temperature [K]',
        'Rotational speed [rpm]',
        'Torque [Nm]',
        'Tool wear [min]'
    ]
    
    X = df[feature_columns]
    y = df['Machine failure']
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Testing set size: {X_test.shape[0]}")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, le, feature_columns

def train_random_forest(X_train, y_train):
    """Train Random Forest model"""
    print("\nTraining Random Forest model...")
    
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=4,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    print("Random Forest training completed!")
    
    return rf_model

def train_gradient_boosting(X_train, y_train):
    """Train Gradient Boosting model"""
    print("\nTraining Gradient Boosting model...")
    
    gb_model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42
    )
    
    gb_model.fit(X_train, y_train)
    print("Gradient Boosting training completed!")
    
    return gb_model

def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model performance"""
    print(f"\n{'='*50}")
    print(f"Evaluating {model_name}")
    print(f"{'='*50}")
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.4f}")
    
    # Classification report
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return accuracy

def save_models(rf_model, gb_model, scaler, label_encoder, feature_columns):
    """Save trained models and preprocessing objects"""
    print("\nSaving models...")
    
    # Create models directory if it doesn't exist
    os.makedirs('../backend/trained_models', exist_ok=True)
    
    # Save models
    joblib.dump(rf_model, '../backend/trained_models/random_forest_model.pkl')
    joblib.dump(gb_model, '../backend/trained_models/gradient_boosting_model.pkl')
    joblib.dump(scaler, '../backend/trained_models/scaler.pkl')
    joblib.dump(label_encoder, '../backend/trained_models/label_encoder.pkl')
    
    # Save feature columns for later use
    with open('../backend/trained_models/feature_columns.txt', 'w') as f:
        f.write(','.join(feature_columns))
    
    print("Models saved successfully in 'backend/trained_models' directory!")

def main():
    """Main function to train and save models"""
    print("="*60)
    print("PREDICTIVE MAINTENANCE MODEL TRAINING")
    print("="*60)
    
    # Load data
    df = load_and_prepare_data('dataset.csv')
    
    # Preprocess data
    X_train, X_test, y_train, y_test, scaler, label_encoder, feature_columns = preprocess_data(df)
    
    # Train models
    rf_model = train_random_forest(X_train, y_train)
    gb_model = train_gradient_boosting(X_train, y_train)
    
    # Evaluate models
    rf_accuracy = evaluate_model(rf_model, X_test, y_test, "Random Forest")
    gb_accuracy = evaluate_model(gb_model, X_test, y_test, "Gradient Boosting")
    
    # Save models
    save_models(rf_model, gb_model, scaler, label_encoder, feature_columns)
    
    # Summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Random Forest Accuracy: {rf_accuracy:.4f}")
    print(f"Gradient Boosting Accuracy: {gb_accuracy:.4f}")
    
    if rf_accuracy > gb_accuracy:
        print("\nRandom Forest performed better!")
    else:
        print("\nGradient Boosting performed better!")
    
    print("\nAll models have been trained and saved successfully!")
    print("You can now use these models for predictions in your application.")
    print("="*60)

if __name__ == "__main__":
    main()
