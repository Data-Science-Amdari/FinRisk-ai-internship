"""
Credit risk domain service.
"""

import time
from typing import List
from .models import (
    CreditApplication, CreditDecision, RiskScore, 
    Decision, RiskLevel, EmploymentStatus
)
from ..core.logging import get_logger
from ..core.exceptions import ValidationError

logger = get_logger(__name__)


class CreditRiskService:
    """Credit risk assessment service."""
    
    def __init__(self):
        self.logger = logger
    
    def assess_credit_risk(self, application: CreditApplication) -> CreditDecision:
        """
        Assess credit risk for a loan application.
        
        Args:
            application: Credit application data
            
        Returns:
            Credit decision with risk assessment
        """
        start_time = time.time()
        
        try:
            # Calculate risk score
            risk_score = self._calculate_risk_score(application)
            
            # Make decision
            decision = self._make_decision(risk_score)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return CreditDecision(
                application=application,
                risk_score=risk_score,
                decision=decision,
                processing_time_ms=processing_time_ms,
                model_version="1.0.0"
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing credit risk: {str(e)}")
            raise
    
    def _calculate_risk_score(self, application: CreditApplication) -> RiskScore:
        """Calculate risk score based on application data."""
        base_score = application.credit_score
        
        # Income ratio adjustment
        income_ratio = application.loan_amount / application.annual_income
        if income_ratio > 0.5:
            base_score -= 100
        elif income_ratio > 0.3:
            base_score -= 50
        
        # Debt-to-income adjustment
        if application.debt_to_income_ratio:
            if application.debt_to_income_ratio > 0.4:
                base_score -= 80
            elif application.debt_to_income_ratio > 0.3:
                base_score -= 40
        
        # Employment status adjustment
        employment_adjustments = {
            EmploymentStatus.SELF_EMPLOYED: -30,
            EmploymentStatus.PART_TIME: -20,
            EmploymentStatus.UNEMPLOYED: -100,
            EmploymentStatus.RETIRED: -10
        }
        
        base_score += employment_adjustments.get(application.employment_status, 0)
        
        # Years employed adjustment
        if application.years_employed:
            if application.years_employed < 1:
                base_score -= 50
            elif application.years_employed < 2:
                base_score -= 25
        
        # Ensure score is within bounds
        final_score = max(300, min(850, base_score))
        
        # Determine risk level
        if final_score >= 750:
            risk_level = RiskLevel.LOW
        elif final_score >= 650:
            risk_level = RiskLevel.MEDIUM
        elif final_score >= 550:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        # Calculate confidence
        confidence = min(0.95, max(0.60, final_score / 1000))
        
        # Identify risk factors
        factors = self._identify_risk_factors(application, final_score)
        
        # Create explanation
        explanation = {
            "base_credit_score": application.credit_score,
            "income_ratio_impact": income_ratio,
            "employment_impact": application.employment_status.value,
            "final_score": final_score,
            "risk_level": risk_level.value
        }
        
        return RiskScore(
            score=final_score,
            level=risk_level,
            confidence=confidence,
            factors=factors,
            explanation=explanation
        )
    
    def _make_decision(self, risk_score: RiskScore) -> Decision:
        """Make credit decision based on risk score."""
        if risk_score.score >= 700:
            return Decision.APPROVE
        elif risk_score.score >= 600:
            return Decision.REVIEW
        else:
            return Decision.DECLINE
    
    def _identify_risk_factors(self, application: CreditApplication, score: float) -> List[str]:
        """Identify risk factors for the application."""
        factors = []
        
        # Income ratio factors
        income_ratio = application.loan_amount / application.annual_income
        if income_ratio > 0.5:
            factors.append("high_loan_to_income_ratio")
        elif income_ratio > 0.3:
            factors.append("moderate_loan_to_income_ratio")
        
        # Debt-to-income factors
        if application.debt_to_income_ratio:
            if application.debt_to_income_ratio > 0.4:
                factors.append("high_debt_to_income_ratio")
            elif application.debt_to_income_ratio > 0.3:
                factors.append("moderate_debt_to_income_ratio")
        
        # Employment factors
        if application.employment_status in [EmploymentStatus.SELF_EMPLOYED, EmploymentStatus.PART_TIME]:
            factors.append("non_standard_employment")
        
        if application.employment_status == EmploymentStatus.UNEMPLOYED:
            factors.append("unemployed")
        
        # Credit score factors
        if application.credit_score < 600:
            factors.append("low_credit_score")
        elif application.credit_score < 650:
            factors.append("moderate_credit_score")
        
        # Years employed factors
        if application.years_employed and application.years_employed < 2:
            factors.append("limited_employment_history")
        
        return factors
