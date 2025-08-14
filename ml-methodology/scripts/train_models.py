#!/usr/bin/env python3
"""
Model training script for FinRisk
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import structlog

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from credit_models.xgboost_model import XGBoostCreditModel
from fraud_detection.isolation_forest import IsolationForestDetector
from feature_engineering.credit_features import CreditFeatureEngineer
from feature_engineering.fraud_features import FraudFeatureEngineer

logger = structlog.get_logger()

def load_data():
    """Load training data"""
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    # Load credit data
    credit_data = None
    if (data_dir / "credit_applications.csv").exists():
        credit_data = pd.read_csv(data_dir / "credit_applications.csv")
        logger.info("Loaded credit applications data", shape=credit_data.shape)
    
    # Load fraud data
    fraud_data = None
    if (data_dir / "transaction_data.csv").exists():
        fraud_data = pd.read_csv(data_dir / "transaction_data.csv")
        logger.info("Loaded transaction data", shape=fraud_data.shape)
    
    return credit_data, fraud_data

def generate_synthetic_credit_data(n_samples=10000):
    """Generate synthetic credit data for training"""
    np.random.seed(42)
    
    data = {
        'customer_id': [f'CUST_{i:06d}' for i in range(n_samples)],
        'credit_score': np.random.normal(650, 100, n_samples).astype(int),
        'income': np.random.lognormal(10.5, 0.5, n_samples),
        'debt_to_income_ratio': np.random.beta(2, 5, n_samples),
        'credit_utilization': np.random.beta(2, 3, n_samples),
        'age': np.random.normal(45, 15, n_samples).astype(int),
        'employment_length': np.random.exponential(60, n_samples).astype(int),
        'loan_amount': np.random.lognormal(9, 0.8, n_samples),
        'payment_history': [
            np.random.choice([0, 1], 12, p=[0.8, 0.2]).tolist() 
            for _ in range(n_samples)
        ]
    }
    
    # Create target variable (credit risk)
    credit_score_norm = (data['credit_score'] - 300) / (850 - 300)
    income_norm = (data['income'] - data['income'].min()) / (data['income'].max() - data['income'].min())
    
    # Simple risk model
    risk_score = (
        0.3 * (1 - credit_score_norm) +
        0.2 * data['debt_to_income_ratio'] +
        0.2 * data['credit_utilization'] +
        0.15 * (1 - income_norm) +
        0.15 * np.random.random(n_samples)
    )
    
    data['is_high_risk'] = (risk_score > 0.6).astype(int)
    
    return pd.DataFrame(data)

def generate_synthetic_fraud_data(n_samples=10000):
    """Generate synthetic fraud data for training"""
    np.random.seed(42)
    
    # Generate normal transactions
    normal_data = {
        'transaction_id': [f'TXN_{i:08d}' for i in range(n_samples)],
        'customer_id': [f'CUST_{np.random.randint(0, 1000):06d}' for _ in range(n_samples)],
        'amount': np.random.lognormal(4, 1, n_samples),
        'merchant_category': np.random.choice(['retail', 'restaurant', 'gas', 'online'], n_samples),
        'location': np.random.choice(['NYC', 'LA', 'Chicago', 'Miami'], n_samples),
        'timestamp': pd.date_range('2023-01-01', periods=n_samples, freq='H'),
        'device_id': [f'DEV_{np.random.randint(0, 100):03d}' for _ in range(n_samples)],
        'ip_address': [f'192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}' for _ in range(n_samples)]
    }
    
    # Add some fraudulent transactions
    fraud_indices = np.random.choice(n_samples, size=int(n_samples * 0.1), replace=False)
    
    for idx in fraud_indices:
        # Make some transactions suspicious
        if np.random.random() > 0.5:
            normal_data['amount'][idx] *= np.random.uniform(5, 20)  # High amount
        if np.random.random() > 0.5:
            normal_data['merchant_category'][idx] = np.random.choice(['electronics_store', 'gaming_site'])
        if np.random.random() > 0.5:
            normal_data['location'][idx] = 'Unknown'
    
    data = pd.DataFrame(normal_data)
    data['is_fraudulent'] = data.index.isin(fraud_indices).astype(int)
    
    return data

def train_credit_model(data):
    """Train credit scoring model"""
    logger.info("Training credit scoring model...")
    
    # Feature engineering
    feature_engineer = CreditFeatureEngineer()
    
    # Prepare features
    features_list = []
    targets = []
    
    for _, row in data.iterrows():
        features = feature_engineer.extract_features(row.to_dict())
        features_list.append(features)
        targets.append(row['is_high_risk'])
    
    # Convert to DataFrame
    X = pd.DataFrame(features_list)
    y = pd.Series(targets)
    
    # Train model
    model = XGBoostCreditModel()
    metrics = model.train(X, y, validation_split=0.2)
    
    # Save model
    model_path = Path(__file__).parent.parent / "models" / "credit_model.pkl"
    model.save_model(str(model_path))
    
    logger.info("Credit model training completed", metrics=metrics)
    return model, metrics

def train_fraud_model(data):
    """Train fraud detection model"""
    logger.info("Training fraud detection model...")
    
    # Feature engineering
    feature_engineer = FraudFeatureEngineer()
    
    # Prepare features
    features_list = []
    
    for _, row in data.iterrows():
        features = feature_engineer.extract_features(row.to_dict())
        features_list.append(features)
    
    # Convert to DataFrame
    X = pd.DataFrame(features_list)
    
    # Train model
    model = IsolationForestDetector()
    metrics = model.train(X, contamination=0.1)
    
    # Save model
    model_path = Path(__file__).parent.parent / "models" / "fraud_model.pkl"
    model.save_model(str(model_path))
    
    logger.info("Fraud model training completed", metrics=metrics)
    return model, metrics

def main():
    """Main training function"""
    logger.info("Starting model training...")
    
    # Load or generate data
    credit_data, fraud_data = load_data()
    
    if credit_data is None:
        logger.info("No credit data found, generating synthetic data...")
        credit_data = generate_synthetic_credit_data()
        
        # Save synthetic data
        output_dir = Path(__file__).parent.parent / "data" / "synthetic"
        output_dir.mkdir(exist_ok=True)
        credit_data.to_csv(output_dir / "synthetic_credit_data.csv", index=False)
    
    if fraud_data is None:
        logger.info("No fraud data found, generating synthetic data...")
        fraud_data = generate_synthetic_fraud_data()
        
        # Save synthetic data
        output_dir = Path(__file__).parent.parent / "data" / "synthetic"
        output_dir.mkdir(exist_ok=True)
        fraud_data.to_csv(output_dir / "synthetic_fraud_data.csv", index=False)
    
    # Create models directory
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Train models
    try:
        credit_model, credit_metrics = train_credit_model(credit_data)
        fraud_model, fraud_metrics = train_fraud_model(fraud_data)
        
        logger.info("All models trained successfully!")
        logger.info("Credit model metrics", metrics=credit_metrics)
        logger.info("Fraud model metrics", metrics=fraud_metrics)
        
    except Exception as e:
        logger.error("Error training models", error=str(e), exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
