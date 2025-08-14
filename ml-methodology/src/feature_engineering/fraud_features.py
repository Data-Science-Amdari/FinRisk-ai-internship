"""
Fraud feature engineering module
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class FraudFeatureEngineer:
    """
    Feature engineering for fraud detection
    """
    
    def __init__(self):
        """Initialize the fraud feature engineer"""
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
            'amount_percentile',
            'merchant_risk_score',
            'location_risk_score',
            'time_risk_score',
            'device_risk_score',
            'velocity_amount',
            'velocity_frequency',
            'velocity_location'
        ]
    
    def extract_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract and engineer features from raw transaction data
        
        Args:
            data: Dictionary containing raw transaction data
            
        Returns:
            Dictionary containing engineered features
        """
        try:
            features = {}
            
            # Basic features
            features['transaction_amount'] = data.get('amount', 100)
            features['transaction_frequency'] = data.get('transaction_frequency', 1)
            features['location_mismatch'] = data.get('location_mismatch', 0)
            features['time_pattern'] = data.get('time_pattern', 0)
            features['device_fingerprint'] = data.get('device_fingerprint', 0)
            features['velocity_features'] = data.get('velocity_features', 0)
            
            # Derived features
            amount = features['transaction_amount']
            features['amount_log'] = np.log(amount + 1)
            features['amount_percentile'] = min(amount / 10000, 1.0)
            
            # Time-based features
            timestamp = data.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = pd.to_datetime(timestamp)
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
            else:
                hour = 12
                day_of_week = 3
            
            features['hour_of_day'] = hour
            features['day_of_week'] = day_of_week
            
            # Risk scores
            features['merchant_risk_score'] = self._calculate_merchant_risk(data.get('merchant_category', ''))
            features['location_risk_score'] = self._calculate_location_risk(data.get('location', ''))
            features['time_risk_score'] = self._calculate_time_risk(hour, day_of_week)
            features['device_risk_score'] = self._calculate_device_risk(data.get('device_id', ''), data.get('ip_address', ''))
            
            # Velocity features
            features['velocity_amount'] = self._calculate_velocity_amount(amount, data.get('customer_id', ''))
            features['velocity_frequency'] = self._calculate_velocity_frequency(data.get('customer_id', ''))
            features['velocity_location'] = self._calculate_velocity_location(data.get('location', ''), data.get('customer_id', ''))
            
            return features
            
        except Exception as e:
            logger.error("Error extracting fraud features", error=str(e), exc_info=True)
            # Return default features in case of error
            return self._get_default_features()
    
    def _calculate_merchant_risk(self, merchant_category: str) -> float:
        """
        Calculate merchant category risk score
        
        Args:
            merchant_category: Merchant category code
            
        Returns:
            Risk score between 0 and 1
        """
        high_risk_merchants = [
            'electronics_store', 'gaming_site', 'cryptocurrency_exchange',
            'online_gambling', 'adult_content', 'pharmaceutical'
        ]
        
        medium_risk_merchants = [
            'online_retail', 'travel', 'luxury_goods', 'jewelry'
        ]
        
        if merchant_category.lower() in high_risk_merchants:
            return 0.9
        elif merchant_category.lower() in medium_risk_merchants:
            return 0.6
        else:
            return 0.2
    
    def _calculate_location_risk(self, location: str) -> float:
        """
        Calculate location risk score
        
        Args:
            location: Transaction location
            
        Returns:
            Risk score between 0 and 1
        """
        high_risk_locations = ['Unknown', 'International', 'High_Risk_Country']
        
        if location in high_risk_locations:
            return 0.8
        elif location in ['NYC', 'LA', 'Miami']:  # High fraud areas
            return 0.5
        else:
            return 0.2
    
    def _calculate_time_risk(self, hour: int, day_of_week: int) -> float:
        """
        Calculate time-based risk score
        
        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0-6, Monday=0)
            
        Returns:
            Risk score between 0 and 1
        """
        # High risk hours (late night/early morning)
        if 0 <= hour <= 5:
            time_risk = 0.8
        elif 6 <= hour <= 8:
            time_risk = 0.4
        elif 9 <= hour <= 17:
            time_risk = 0.2
        elif 18 <= hour <= 22:
            time_risk = 0.3
        else:
            time_risk = 0.6
        
        # Weekend risk
        if day_of_week >= 5:  # Weekend
            time_risk *= 1.2
        
        return min(time_risk, 1.0)
    
    def _calculate_device_risk(self, device_id: str, ip_address: str) -> float:
        """
        Calculate device risk score
        
        Args:
            device_id: Device identifier
            ip_address: IP address
            
        Returns:
            Risk score between 0 and 1
        """
        risk_score = 0.0
        
        # Check for new device
        if device_id.startswith('NEW_') or device_id == 'Unknown':
            risk_score += 0.4
        
        # Check for suspicious IP patterns
        if ip_address:
            if ip_address.startswith('192.168.') or ip_address.startswith('10.'):
                risk_score += 0.2  # Private IP
            elif ip_address.startswith('0.0.0.') or ip_address == 'Unknown':
                risk_score += 0.6  # Invalid IP
        
        return min(risk_score, 1.0)
    
    def _calculate_velocity_amount(self, amount: float, customer_id: str) -> float:
        """
        Calculate velocity feature for transaction amount
        
        Args:
            amount: Transaction amount
            customer_id: Customer identifier
            
        Returns:
            Velocity score between 0 and 1
        """
        # In a real implementation, this would check historical data
        # For MVP, we'll use a simplified approach
        
        if amount > 10000:
            return 0.8
        elif amount > 5000:
            return 0.6
        elif amount > 1000:
            return 0.4
        else:
            return 0.2
    
    def _calculate_velocity_frequency(self, customer_id: str) -> float:
        """
        Calculate velocity feature for transaction frequency
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Velocity score between 0 and 1
        """
        # In a real implementation, this would check recent transaction history
        # For MVP, we'll use a simplified approach
        
        # Simulate based on customer ID
        if customer_id:
            # Use customer ID to generate consistent but varied scores
            hash_value = hash(customer_id) % 100
            if hash_value > 80:
                return 0.9  # High frequency
            elif hash_value > 60:
                return 0.7  # Medium frequency
            elif hash_value > 40:
                return 0.5  # Normal frequency
            else:
                return 0.3  # Low frequency
        
        return 0.5
    
    def _calculate_velocity_location(self, location: str, customer_id: str) -> float:
        """
        Calculate velocity feature for location changes
        
        Args:
            location: Current transaction location
            customer_id: Customer identifier
            
        Returns:
            Velocity score between 0 and 1
        """
        # In a real implementation, this would check recent location history
        # For MVP, we'll use a simplified approach
        
        if location == 'Unknown':
            return 0.8
        
        # Simulate based on customer ID and location
        if customer_id and location:
            hash_value = hash(f"{customer_id}_{location}") % 100
            if hash_value > 70:
                return 0.6  # Suspicious location change
            else:
                return 0.2  # Normal location
        
        return 0.3
    
    def _get_default_features(self) -> Dict[str, float]:
        """Get default feature values"""
        return {
            'transaction_amount': 100,
            'transaction_frequency': 1,
            'location_mismatch': 0,
            'time_pattern': 0,
            'device_fingerprint': 0,
            'velocity_features': 0,
            'amount_log': 4.6,
            'hour_of_day': 12,
            'day_of_week': 3,
            'amount_percentile': 0.01,
            'merchant_risk_score': 0.2,
            'location_risk_score': 0.2,
            'time_risk_score': 0.2,
            'device_risk_score': 0.2,
            'velocity_amount': 0.2,
            'velocity_frequency': 0.5,
            'velocity_location': 0.3
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
                    logger.warning(f"Missing fraud feature: {feature_name}")
                    return False
                
                value = features[feature_name]
                if not isinstance(value, (int, float)) or np.isnan(value):
                    logger.warning(f"Invalid fraud feature value: {feature_name} = {value}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error validating fraud features", error=str(e), exc_info=True)
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
            logger.error("Error scaling fraud features", error=str(e), exc_info=True)
            return features
