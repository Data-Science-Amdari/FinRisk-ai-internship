"""
XGBoost Credit Scoring Model
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import structlog

logger = structlog.get_logger()

class XGBoostCreditModel:
    """
    XGBoost-based credit scoring model
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the XGBoost credit model
        
        Args:
            model_path: Path to pre-trained model file
        """
        self.model = None
        self.feature_names = [
            'credit_score',
            'income',
            'debt_to_income_ratio', 
            'payment_history_score',
            'credit_utilization',
            'age',
            'employment_length',
            'loan_amount',
            'income_to_loan_ratio'
        ]
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new XGBoost model with default parameters"""
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        logger.info("Initialized new XGBoost credit model")
    
    def train(self, X: pd.DataFrame, y: pd.Series, validation_split: float = 0.2) -> Dict[str, float]:
        """
        Train the XGBoost model
        
        Args:
            X: Feature matrix
            y: Target variable
            validation_split: Fraction of data to use for validation
            
        Returns:
            Dictionary containing training metrics
        """
        try:
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42, stratify=y
            )
            
            # Train model
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=10,
                verbose=False
            )
            
            # Make predictions
            y_pred = self.model.predict(X_val)
            y_pred_proba = self.model.predict_proba(X_val)[:, 1]
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_val, y_pred),
                'precision': precision_score(y_val, y_pred),
                'recall': recall_score(y_val, y_pred),
                'f1_score': f1_score(y_val, y_pred),
                'auc_roc': roc_auc_score(y_val, y_pred_proba)
            }
            
            logger.info("XGBoost model training completed", metrics=metrics)
            return metrics
            
        except Exception as e:
            logger.error("Error training XGBoost model", error=str(e), exc_info=True)
            raise
    
    def predict(self, features: Dict[str, Any]) -> Tuple[float, float]:
        """
        Make prediction for credit risk
        
        Args:
            features: Dictionary containing feature values
            
        Returns:
            Tuple of (risk_score, confidence)
        """
        try:
            # Convert features to DataFrame
            feature_df = self._prepare_features(features)
            
            # Make prediction
            risk_score = self.model.predict_proba(feature_df)[0, 1]
            
            # Calculate confidence based on prediction probability
            confidence = abs(risk_score - 0.5) * 2  # Scale to 0-1
            
            return risk_score, confidence
            
        except Exception as e:
            logger.error("Error making prediction", error=str(e), exc_info=True)
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
            'credit_score': features.get('credit_score', 650),
            'income': features.get('income', 50000),
            'debt_to_income_ratio': features.get('debt_to_income_ratio', 0.3),
            'credit_utilization': features.get('credit_utilization', 0.5),
            'age': features.get('age', 35),
            'employment_length': features.get('employment_length', 24),
            'loan_amount': features.get('loan_amount', 10000)
        }
        
        # Calculate derived features
        payment_history = features.get('payment_history', [0] * 12)
        prepared_features['payment_history_score'] = 1 - (sum(payment_history) / len(payment_history))
        
        income = prepared_features['income']
        loan_amount = prepared_features['loan_amount']
        prepared_features['income_to_loan_ratio'] = income / loan_amount if loan_amount > 0 else 10
        
        # Create DataFrame
        feature_df = pd.DataFrame([prepared_features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in feature_df.columns:
                feature_df[feature] = 0
        
        return feature_df[self.feature_names]
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            return {}
        
        importance_scores = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importance_scores))
        
        # Sort by importance
        feature_importance = dict(sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return feature_importance
    
    def save_model(self, model_path: str):
        """
        Save the trained model to disk
        
        Args:
            model_path: Path where to save the model
        """
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            logger.info("Model saved successfully", path=model_path)
            
        except Exception as e:
            logger.error("Error saving model", error=str(e), exc_info=True)
            raise
    
    def load_model(self, model_path: str):
        """
        Load a trained model from disk
        
        Args:
            model_path: Path to the saved model file
        """
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            logger.info("Model loaded successfully", path=model_path)
            
        except Exception as e:
            logger.error("Error loading model", error=str(e), exc_info=True)
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
            
            logger.info("Hyperparameters updated", hyperparameters=hyperparameters)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dictionary containing model information
        """
        info = {
            'model_type': 'XGBoost',
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'is_trained': self.model is not None
        }
        
        if self.model is not None:
            info['n_estimators'] = self.model.n_estimators
            info['max_depth'] = self.model.max_depth
            info['learning_rate'] = self.model.learning_rate
        
        return info
