"""
Credit feature engineering module
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()

class CreditFeatureEngineer:
    """
    Feature engineering for credit scoring
    """
    
    def __init__(self):
        """Initialize the credit feature engineer"""
        self.feature_names = [
            'credit_score',
            'income',
            'debt_to_income_ratio',
            'payment_history_score',
            'credit_utilization',
            'age',
            'employment_length',
            'loan_amount',
            'income_to_loan_ratio',
            'credit_score_normalized',
            'income_log',
            'age_squared',
            'employment_stability',
            'payment_consistency',
            'credit_mix_score'
        ]
    
    def extract_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract and engineer features from raw credit data
        
        Args:
            data: Dictionary containing raw credit data
            
        Returns:
            Dictionary containing engineered features
        """
        try:
            features = {}
            
            # Basic features
            features['credit_score'] = data.get('credit_score', 650)
            features['income'] = data.get('income', 50000)
            features['debt_to_income_ratio'] = data.get('debt_to_income_ratio', 0.3)
            features['credit_utilization'] = data.get('credit_utilization', 0.5)
            features['age'] = data.get('age', 35)
            features['employment_length'] = data.get('employment_length', 24)
            features['loan_amount'] = data.get('loan_amount', 10000)
            
            # Payment history features
            payment_history = data.get('payment_history', [0] * 12)
            features['payment_history_score'] = self._calculate_payment_score(payment_history)
            features['payment_consistency'] = self._calculate_payment_consistency(payment_history)
            
            # Derived features
            features['income_to_loan_ratio'] = self._calculate_income_loan_ratio(
                features['income'], features['loan_amount']
            )
            features['credit_score_normalized'] = self._normalize_credit_score(features['credit_score'])
            features['income_log'] = np.log(features['income'] + 1)
            features['age_squared'] = features['age'] ** 2
            features['employment_stability'] = self._calculate_employment_stability(
                features['employment_length']
            )
            
            # Credit mix features (if available)
            credit_accounts = data.get('credit_accounts', {})
            features['credit_mix_score'] = self._calculate_credit_mix_score(credit_accounts)
            
            return features
            
        except Exception as e:
            logger.error("Error extracting credit features", error=str(e), exc_info=True)
            # Return default features in case of error
            return self._get_default_features()
    
    def _calculate_payment_score(self, payment_history: List[int]) -> float:
        """
        Calculate payment history score
        
        Args:
            payment_history: List of payment status (0=on time, 1=late)
            
        Returns:
            Payment score between 0 and 1
        """
        if not payment_history:
            return 0.5
        
        # Weight recent payments more heavily
        weights = np.linspace(0.5, 1.0, len(payment_history))
        weighted_sum = sum(p * w for p, w in zip(payment_history, weights))
        total_weight = sum(weights)
        
        # Convert to score (0 = all late, 1 = all on time)
        return 1 - (weighted_sum / total_weight)
    
    def _calculate_payment_consistency(self, payment_history: List[int]) -> float:
        """
        Calculate payment consistency score
        
        Args:
            payment_history: List of payment status
            
        Returns:
            Consistency score between 0 and 1
        """
        if len(payment_history) < 2:
            return 0.5
        
        # Calculate standard deviation of payment patterns
        std_dev = np.std(payment_history)
        # Convert to consistency score (lower std = higher consistency)
        return max(0, 1 - std_dev)
    
    def _calculate_income_loan_ratio(self, income: float, loan_amount: float) -> float:
        """
        Calculate income to loan amount ratio
        
        Args:
            income: Annual income
            loan_amount: Requested loan amount
            
        Returns:
            Income to loan ratio
        """
        if loan_amount <= 0:
            return 10.0  # Default high ratio for zero loan amount
        
        return income / loan_amount
    
    def _normalize_credit_score(self, credit_score: int) -> float:
        """
        Normalize credit score to 0-1 range
        
        Args:
            credit_score: Raw credit score (300-850)
            
        Returns:
            Normalized credit score
        """
        return (credit_score - 300) / (850 - 300)
    
    def _calculate_employment_stability(self, employment_length: int) -> float:
        """
        Calculate employment stability score
        
        Args:
            employment_length: Employment length in months
            
        Returns:
            Stability score between 0 and 1
        """
        # Convert months to years and calculate stability
        years = employment_length / 12
        
        if years >= 10:
            return 1.0
        elif years >= 5:
            return 0.8
        elif years >= 2:
            return 0.6
        elif years >= 1:
            return 0.4
        else:
            return 0.2
    
    def _calculate_credit_mix_score(self, credit_accounts: Dict[str, int]) -> float:
        """
        Calculate credit mix diversity score
        
        Args:
            credit_accounts: Dictionary of account types and counts
            
        Returns:
            Credit mix score between 0 and 1
        """
        if not credit_accounts:
            return 0.5
        
        # Count different types of accounts
        account_types = len(credit_accounts)
        total_accounts = sum(credit_accounts.values())
        
        if total_accounts == 0:
            return 0.5
        
        # Calculate diversity score
        diversity = account_types / total_accounts
        
        # Normalize to 0-1 range
        return min(1.0, diversity * 2)
    
    def _get_default_features(self) -> Dict[str, float]:
        """Get default feature values"""
        return {
            'credit_score': 650,
            'income': 50000,
            'debt_to_income_ratio': 0.3,
            'payment_history_score': 0.5,
            'credit_utilization': 0.5,
            'age': 35,
            'employment_length': 24,
            'loan_amount': 10000,
            'income_to_loan_ratio': 5.0,
            'credit_score_normalized': 0.5,
            'income_log': 10.8,
            'age_squared': 1225,
            'employment_stability': 0.6,
            'payment_consistency': 0.5,
            'credit_mix_score': 0.5
        }
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names.copy()
    
    def validate_features(self, features: Dict[str, float]) -> bool:
        """
        Validate feature values
        
        Args:
            features: Dictionary of features to validate
            
        Returns:
            True if features are valid, False otherwise
        """
        try:
            for feature_name in self.feature_names:
                if feature_name not in features:
                    logger.warning(f"Missing feature: {feature_name}")
                    return False
                
                value = features[feature_name]
                if not isinstance(value, (int, float)) or np.isnan(value):
                    logger.warning(f"Invalid feature value: {feature_name} = {value}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error validating features", error=str(e), exc_info=True)
            return False
    
    def scale_features(self, features: Dict[str, float], scaler=None) -> Dict[str, float]:
        """
        Scale features using provided scaler
        
        Args:
            features: Dictionary of features to scale
            scaler: Scikit-learn scaler object
            
        Returns:
            Dictionary of scaled features
        """
        if scaler is None:
            return features
        
        try:
            # Convert to DataFrame for scaling
            feature_df = pd.DataFrame([features])
            scaled_df = scaler.transform(feature_df)
            
            # Convert back to dictionary
            scaled_features = dict(zip(features.keys(), scaled_df[0]))
            return scaled_features
            
        except Exception as e:
            logger.error("Error scaling features", error=str(e), exc_info=True)
            return features
