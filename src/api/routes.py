"""
API routes for FinRisk application.
"""

from fastapi import APIRouter, HTTPException
import logging

from ..core.config import settings
from ..domain.models import CreditApplication, Transaction, CreditDecision, FraudDecision
from ..domain.credit_risk import CreditRiskService
from ..domain.fraud_detection import FraudDetectionService

# Setup logger
logger = logging.getLogger(__name__)

# Create routers
credit_router = APIRouter(prefix="/api", tags=["credit"])
fraud_router = APIRouter(prefix="/api", tags=["fraud"])

# Initialize services
credit_service = CreditRiskService()
fraud_service = FraudDetectionService()


@credit_router.post("/credit/assess", response_model=CreditDecision)
async def assess_credit(application: CreditApplication) -> CreditDecision:
    """
    Assess credit risk for a loan application.
    
    Args:
        application: Credit application data
        
    Returns:
        Credit risk assessment with decision
    """
    try:
        decision = credit_service.assess_credit_risk(application)
        return decision
        
    except Exception as e:
        logger.error(f"Error in credit assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@fraud_router.post("/fraud/detect", response_model=FraudDecision)
async def detect_fraud(transaction: Transaction) -> FraudDecision:
    """
    Detect fraud in a transaction.
    
    Args:
        transaction: Transaction data
        
    Returns:
        Fraud risk assessment with decision
    """
    try:
        decision = fraud_service.detect_fraud(transaction)
        return decision
        
    except Exception as e:
        logger.error(f"Error in fraud detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

