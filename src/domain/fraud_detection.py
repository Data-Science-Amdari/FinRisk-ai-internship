"""
Fraud detection domain service.
"""

import time
from typing import List
from .models import (
    Transaction, FraudDecision, Decision
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class FraudDetectionService:
    """Fraud detection service."""
    
    def __init__(self):
        self.logger = logger
        self.risky_categories = {
            "Online Gambling", "Cryptocurrency", "Adult Entertainment",
            "Foreign Exchange", "High-Risk Investments"
        }
    
    def detect_fraud(self, transaction: Transaction) -> FraudDecision:
        """
        Detect fraud in a transaction.
        
        Args:
            transaction: Transaction data
            
        Returns:
            Fraud decision with risk assessment
        """
        start_time = time.time()
        
        try:
            # Calculate fraud probability
            fraud_probability = self._calculate_fraud_probability(transaction)
            
            # Make decision
            decision = self._make_decision(fraud_probability)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(transaction, fraud_probability)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return FraudDecision(
                transaction=transaction,
                fraud_probability=fraud_probability,
                decision=decision,
                risk_factors=risk_factors,
                processing_time_ms=processing_time_ms,
                model_version="1.0.0"
            )
            
        except Exception as e:
            self.logger.error(f"Error detecting fraud: {str(e)}")
            raise
    
    def _calculate_fraud_probability(self, transaction: Transaction) -> float:
        """Calculate fraud probability based on transaction data."""
        risk_score = 0.1  # Base risk
        
        # Amount-based risk
        if transaction.amount > 5000:
            risk_score += 0.4
        elif transaction.amount > 1000:
            risk_score += 0.2
        elif transaction.amount > 500:
            risk_score += 0.1
        
        # Merchant category risk
        if transaction.merchant_category in self.risky_categories:
            risk_score += 0.3
        
        # Location risk
        if transaction.location:
            if "International" in transaction.location:
                risk_score += 0.2
            elif "High-Risk Region" in transaction.location:
                risk_score += 0.15
        
        # Device risk
        if transaction.device_info:
            if "Mobile" in transaction.device_info:
                risk_score += 0.1
            elif "Unknown Device" in transaction.device_info:
                risk_score += 0.2
            elif "VPN" in transaction.device_info:
                risk_score += 0.15
        
        # Time-based risk (simplified)
        hour = transaction.timestamp.hour
        if hour < 6 or hour > 22:  # Late night transactions
            risk_score += 0.1
        
        return min(0.95, risk_score)
    
    def _make_decision(self, fraud_probability: float) -> Decision:
        """Make fraud decision based on probability."""
        if fraud_probability < 0.3:
            return Decision.ALLOW
        elif fraud_probability < 0.7:
            return Decision.REVIEW
        else:
            return Decision.BLOCK
    
    def _identify_risk_factors(self, transaction: Transaction, probability: float) -> List[str]:
        """Identify risk factors for the transaction."""
        factors = []
        
        # Amount factors
        if transaction.amount > 5000:
            factors.append("high_amount")
        elif transaction.amount > 1000:
            factors.append("moderate_amount")
        
        # Merchant factors
        if transaction.merchant_category in self.risky_categories:
            factors.append("risky_merchant_category")
        
        # Location factors
        if transaction.location:
            if "International" in transaction.location:
                factors.append("international_transaction")
            elif "High-Risk Region" in transaction.location:
                factors.append("high_risk_location")
        
        # Device factors
        if transaction.device_info:
            if "Mobile" in transaction.device_info:
                factors.append("mobile_device")
            elif "Unknown Device" in transaction.device_info:
                factors.append("unknown_device")
            elif "VPN" in transaction.device_info:
                factors.append("vpn_connection")
        
        # Time factors
        hour = transaction.timestamp.hour
        if hour < 6 or hour > 22:
            factors.append("late_night_transaction")
        
        # Probability-based factors
        if probability > 0.7:
            factors.append("high_fraud_probability")
        elif probability > 0.5:
            factors.append("moderate_fraud_probability")
        
        return factors
