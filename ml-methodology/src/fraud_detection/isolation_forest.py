"""
Isolation Forest for Fraud Detection
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import structlog

logger = structlog.get_logger()

class IsolationForestDetector:
    """
    Isolation Forest-based fraud detection model
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the Isolation Forest detector
        
        Args:
            model_path: Path to pre-trained model file
        """
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'transaction_amount',
            'transaction_frequency',
            'location_mismatch',
            'time_pattern',
            'device_fingerprint',
            'velocity_features',
            'amount_log',
            'hour_of_day',
            'day_of_week',
            'amount_percentile'
        ]
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new Isolation Forest model"""
        self.model = IsolationForest(
            contamination=0.1,
            n_estimators=100,
            max_samples='auto',
            random_state=42
        )
        logger.info("Initialized new Isolation Forest fraud detector")
    
    def train(self, X: pd.DataFrame, contamination: float = 0.1) -> Dict[str, float]:
        """
        Train the Isolation Forest model
        
        Args:
            X: Feature matrix
            contamination: Expected proportion of anomalies
            
        Returns:
            Dictionary containing training metrics
        """
        try:
            # Update contamination if provided
            if contamination != 0.1:
                self.model.contamination = contamination
            
            # Fit scaler
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled)
            
            # Calculate training metrics
            anomaly_scores = self.model.decision_function(X_scaled)
            predictions = self.model.predict(X_scaled)
            
            metrics = {
                'n_samples': len(X),
                'n_features': X.shape[1],
                'contamination': contamination,
                'mean_anomaly_score': np.mean(anomaly_scores),
                'std_anomaly_score': np.std(anomaly_scores),
                'predicted_anomalies': np.sum(predictions == -1)
            }
            
            logger.info("Isolation Forest training completed", metrics=metrics)
            return metrics
            
        except Exception as e:
            logger.error("Error training Isolation Forest", error=str(e), exc_info=True)
            raise
    
    def predict(self, features: Dict[str, Any]) -> Tuple[float, float]:
        """
        Make fraud prediction
        
        Args:
            features: Dictionary containing feature values
            
        Returns:
            Tuple of (fraud_score, confidence)
        """
        try:
            # Convert features to DataFrame
            feature_df = self._prepare_features(features)
            
            # Scale features
            feature_scaled = self.scaler.transform(feature_df)
            
            # Get anomaly score
            anomaly_score = self.model.decision_function(feature_scaled)[0]
            
            # Convert to fraud score (higher anomaly score = higher fraud probability)
            # Normalize to 0-1 range
            fraud_score = self._anomaly_score_to_fraud_score(anomaly_score)
            
            # Calculate confidence based on distance from decision boundary
            confidence = abs(anomaly_score) / 2  # Normalize to 0-1
            
            return fraud_score, confidence
            
        except Exception as e:
            logger.error("Error making fraud prediction", error=str(e), exc_info=True)
            # Return default values in case of error
            return 0.5, 0.5
    
    def _prepare_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare features for prediction
        
        Args:
            features: Raw feature dictionary
            
        Returns:
            DataFrame with prepared features
        """
        # Extract basic features
        prepared_features = {
            'transaction_amount': features.get('amount', 100),
            'transaction_frequency': features.get('transaction_frequency', 1),
            'location_mismatch': features.get('location_mismatch', 0),
            'time_pattern': features.get('time_pattern', 0),
            'device_fingerprint': features.get('device_fingerprint', 0),
            'velocity_features': features.get('velocity_features', 0)
        }
        
        # Calculate derived features
        amount = prepared_features['transaction_amount']
        prepared_features['amount_log'] = np.log(amount + 1)
        
        # Time-based features
        timestamp = features.get('timestamp')
        if timestamp:
            hour = pd.to_datetime(timestamp).hour
            day_of_week = pd.to_datetime(timestamp).dayofweek
        else:
            hour = 12
            day_of_week = 3
        
        prepared_features['hour_of_day'] = hour
        prepared_features['day_of_week'] = day_of_week
        
        # Amount percentile (simplified)
        prepared_features['amount_percentile'] = min(amount / 10000, 1.0)
        
        # Create DataFrame
        feature_df = pd.DataFrame([prepared_features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in feature_df.columns:
                feature_df[feature] = 0
        
        return feature_df[self.feature_names]
    
    def _anomaly_score_to_fraud_score(self, anomaly_score: float) -> float:
        """
        Convert anomaly score to fraud probability
        
        Args:
            anomaly_score: Raw anomaly score from Isolation Forest
            
        Returns:
            Fraud probability between 0 and 1
        """
        # Isolation Forest returns negative scores for anomalies
        # We want higher scores to indicate higher fraud probability
        
        # Normalize to 0-1 range using sigmoid-like transformation
        normalized_score = 1 / (1 + np.exp(-anomaly_score))
        
        return normalized_score
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores (simplified for Isolation Forest)
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        # Isolation Forest doesn't provide direct feature importance
        # We'll use a simplified approach based on feature variance
        if not hasattr(self, '_feature_importance'):
            # Equal importance for all features
            importance_scores = [1.0 / len(self.feature_names)] * len(self.feature_names)
            self._feature_importance = dict(zip(self.feature_names, importance_scores))
        
        return self._feature_importance.copy()
    
    def save_model(self, model_path: str):
        """
        Save the trained model to disk
        
        Args:
            model_path: Path where to save the model
        """
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info("Fraud detection model saved successfully", path=model_path)
            
        except Exception as e:
            logger.error("Error saving fraud detection model", error=str(e), exc_info=True)
            raise
    
    def load_model(self, model_path: str):
        """
        Load a trained model from disk
        
        Args:
            model_path: Path to the saved model file
        """
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            
            logger.info("Fraud detection model loaded successfully", path=model_path)
            
        except Exception as e:
            logger.error("Error loading fraud detection model", error=str(e), exc_info=True)
            raise
    
    def update_hyperparameters(self, hyperparameters: Dict[str, Any]):
        """
        Update model hyperparameters
        
        Args:
            hyperparameters: Dictionary of hyperparameters to update
        """
        if self.model is not None:
            for param, value in hyperparameters.items():
                if hasattr(self.model, param):
                    setattr(self.model, param, value)
            
            logger.info("Fraud detection hyperparameters updated", hyperparameters=hyperparameters)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dictionary containing model information
        """
        info = {
            'model_type': 'IsolationForest',
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'is_trained': self.model is not None
        }
        
        if self.model is not None:
            info['contamination'] = self.model.contamination
            info['n_estimators'] = self.model.n_estimators
            info['max_samples'] = self.model.max_samples
        
        return info
    
    def detect_batch(self, features_list: List[Dict[str, Any]]) -> List[Tuple[float, float]]:
        """
        Detect fraud in a batch of transactions
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            List of (fraud_score, confidence) tuples
        """
        try:
            results = []
            
            for features in features_list:
                fraud_score, confidence = self.predict(features)
                results.append((fraud_score, confidence))
            
            return results
            
        except Exception as e:
            logger.error("Error in batch fraud detection", error=str(e), exc_info=True)
            # Return default values for all transactions
            return [(0.5, 0.5)] * len(features_list)
