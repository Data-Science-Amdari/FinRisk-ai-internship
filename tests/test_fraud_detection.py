"""
Tests for fraud detection domain service.
"""

import pytest
from datetime import datetime
from src.domain.fraud_detection import FraudDetectionService
from src.domain.models import Transaction, Decision


class TestFraudDetectionService:
    """Test cases for FraudDetectionService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = FraudDetectionService()
    
    def test_detect_fraud_low_risk(self):
        """Test fraud detection for low-risk transaction."""
        transaction = Transaction(
            customer_id="CUST001",
            transaction_id="TXN001",
            amount=100,
            merchant_category="Grocery Store",
            location="Local Store",
            device_info="Desktop Computer"
        )
        
        decision = self.service.detect_fraud(transaction)
        
        assert decision.decision == Decision.ALLOW
        assert decision.fraud_probability < 0.3
        assert decision.processing_time_ms > 0
    
    def test_detect_fraud_high_risk(self):
        """Test fraud detection for high-risk transaction."""
        transaction = Transaction(
            customer_id="CUST002",
            transaction_id="TXN002",
            amount=10000,
            merchant_category="Online Gambling",
            location="International",
            device_info="Unknown Device"
        )
        
        decision = self.service.detect_fraud(transaction)
        
        assert decision.decision == Decision.BLOCK
        assert decision.fraud_probability > 0.7
        assert "risky_merchant_category" in decision.risk_factors
        assert "high_amount" in decision.risk_factors
    
    def test_detect_fraud_medium_risk(self):
        """Test fraud detection for medium-risk transaction."""
        transaction = Transaction(
            customer_id="CUST003",
            transaction_id="TXN003",
            amount=2000,
            merchant_category="Electronics",
            location="International",
            device_info="Mobile Device"
        )
        
        decision = self.service.detect_fraud(transaction)
        
        assert decision.decision == Decision.REVIEW
        assert 0.3 <= decision.fraud_probability <= 0.7
        assert "international_transaction" in decision.risk_factors
        assert "mobile_device" in decision.risk_factors
    
    def test_risk_factors_identification(self):
        """Test risk factors identification."""
        transaction = Transaction(
            customer_id="CUST004",
            transaction_id="TXN004",
            amount=8000,
            merchant_category="Cryptocurrency",
            location="High-Risk Region",
            device_info="VPN Connection"
        )
        
        decision = self.service.detect_fraud(transaction)
        
        # Should identify multiple risk factors
        assert len(decision.risk_factors) > 0
        assert "high_amount" in decision.risk_factors
        assert "risky_merchant_category" in decision.risk_factors
        assert "high_risk_location" in decision.risk_factors
        assert "vpn_connection" in decision.risk_factors
    
    def test_late_night_transaction(self):
        """Test fraud detection for late night transaction."""
        # Create transaction at 2 AM
        timestamp = datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
        
        transaction = Transaction(
            customer_id="CUST005",
            transaction_id="TXN005",
            amount=500,
            merchant_category="Online Shopping",
            location="Local",
            device_info="Mobile Device",
            timestamp=timestamp
        )
        
        decision = self.service.detect_fraud(transaction)
        
        assert "late_night_transaction" in decision.risk_factors
