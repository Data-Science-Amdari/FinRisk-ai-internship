"""
Basic tests for FinRisk MVP
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from credit_models.xgboost_model import XGBoostCreditModel
from fraud_detection.isolation_forest import IsolationForestDetector
from feature_engineering.credit_features import CreditFeatureEngineer
from feature_engineering.fraud_features import FraudFeatureEngineer

def test_credit_model_initialization():
    """Test credit model initialization"""
    model = XGBoostCreditModel()
    assert model is not None
    assert hasattr(model, 'feature_names')
    assert len(model.feature_names) > 0

def test_fraud_model_initialization():
    """Test fraud detection model initialization"""
    model = IsolationForestDetector()
    assert model is not None
    assert hasattr(model, 'feature_names')
    assert len(model.feature_names) > 0

def test_credit_feature_engineering():
    """Test credit feature engineering"""
    engineer = CreditFeatureEngineer()
    
    # Test with sample data
    sample_data = {
        'credit_score': 700,
        'income': 50000,
        'debt_to_income_ratio': 0.3,
        'credit_utilization': 0.5,
        'age': 35,
        'employment_length': 24,
        'loan_amount': 10000,
        'payment_history': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    
    features = engineer.extract_features(sample_data)
    assert features is not None
    assert len(features) > 0
    assert 'credit_score' in features
    assert 'income' in features

def test_fraud_feature_engineering():
    """Test fraud feature engineering"""
    engineer = FraudFeatureEngineer()
    
    # Test with sample data
    sample_data = {
        'amount': 1000,
        'merchant_category': 'retail',
        'location': 'NYC',
        'timestamp': '2023-01-01T12:00:00',
        'device_id': 'DEV_001',
        'ip_address': '192.168.1.1'
    }
    
    features = engineer.extract_features(sample_data)
    assert features is not None
    assert len(features) > 0
    assert 'transaction_amount' in features
    assert 'merchant_risk_score' in features

def test_credit_model_prediction():
    """Test credit model prediction"""
    model = XGBoostCreditModel()
    
    # Test with sample features
    sample_features = {
        'credit_score': 700,
        'income': 50000,
        'debt_to_income_ratio': 0.3,
        'payment_history_score': 0.9,
        'credit_utilization': 0.5,
        'age': 35,
        'employment_length': 24,
        'loan_amount': 10000,
        'income_to_loan_ratio': 5.0
    }
    
    # This should work even without training (returns default values)
    risk_score, confidence = model.predict(sample_features)
    assert isinstance(risk_score, float)
    assert isinstance(confidence, float)
    assert 0 <= risk_score <= 1
    assert 0 <= confidence <= 1

def test_fraud_model_prediction():
    """Test fraud model prediction"""
    model = IsolationForestDetector()
    
    # Test with sample features
    sample_features = {
        'amount': 1000,
        'merchant_category': 'retail',
        'location': 'NYC',
        'timestamp': '2023-01-01T12:00:00',
        'device_id': 'DEV_001',
        'ip_address': '192.168.1.1'
    }
    
    # This should work even without training (returns default values)
    fraud_score, confidence = model.predict(sample_features)
    assert isinstance(fraud_score, float)
    assert isinstance(confidence, float)
    assert 0 <= fraud_score <= 1
    assert 0 <= confidence <= 1

if __name__ == "__main__":
    pytest.main([__file__])
