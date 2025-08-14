"""
Tests for credit risk domain service.
"""

import pytest
from datetime import datetime
from src.domain.credit_risk import CreditRiskService
from src.domain.models import (
    CreditApplication, EmploymentStatus, Decision, RiskLevel
)


class TestCreditRiskService:
    """Test cases for CreditRiskService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CreditRiskService()
    
    def test_assess_credit_risk_high_score(self):
        """Test credit risk assessment for high credit score."""
        application = CreditApplication(
            customer_id="CUST001",
            loan_amount=50000,
            annual_income=100000,
            debt_to_income_ratio=0.25,
            credit_score=800,
            employment_status=EmploymentStatus.FULL_TIME,
            years_employed=5
        )
        
        decision = self.service.assess_credit_risk(application)
        
        assert decision.decision == Decision.APPROVE
        assert decision.risk_score.score >= 700
        assert decision.risk_score.level == RiskLevel.LOW
        assert decision.processing_time_ms > 0
    
    def test_assess_credit_risk_low_score(self):
        """Test credit risk assessment for low credit score."""
        application = CreditApplication(
            customer_id="CUST002",
            loan_amount=50000,
            annual_income=50000,
            debt_to_income_ratio=0.6,
            credit_score=550,
            employment_status=EmploymentStatus.SELF_EMPLOYED,
            years_employed=1
        )
        
        decision = self.service.assess_credit_risk(application)
        
        assert decision.decision == Decision.DECLINE
        assert decision.risk_score.score < 600
        assert decision.risk_score.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def test_assess_credit_risk_medium_score(self):
        """Test credit risk assessment for medium credit score."""
        application = CreditApplication(
            customer_id="CUST003",
            loan_amount=30000,
            annual_income=60000,
            debt_to_income_ratio=0.35,
            credit_score=650,
            employment_status=EmploymentStatus.FULL_TIME,
            years_employed=3
        )
        
        decision = self.service.assess_credit_risk(application)
        
        assert decision.decision == Decision.REVIEW
        assert 600 <= decision.risk_score.score < 700
        assert decision.risk_score.level == RiskLevel.MEDIUM
    
    def test_risk_factors_identification(self):
        """Test risk factors identification."""
        application = CreditApplication(
            customer_id="CUST004",
            loan_amount=100000,
            annual_income=80000,
            debt_to_income_ratio=0.45,
            credit_score=580,
            employment_status=EmploymentStatus.PART_TIME,
            years_employed=0.5
        )
        
        decision = self.service.assess_credit_risk(application)
        
        # Should identify multiple risk factors
        assert len(decision.risk_score.factors) > 0
        assert "high_loan_to_income_ratio" in decision.risk_score.factors
        assert "non_standard_employment" in decision.risk_score.factors
        assert "limited_employment_history" in decision.risk_score.factors
