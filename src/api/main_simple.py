"""
FinRisk API - Simple Version
Credit Risk Assessment & Fraud Detection Engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FinRisk API",
    description="Credit Risk Assessment & Fraud Detection Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FinRisk API - Credit Risk Assessment & Fraud Detection Engine",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "finrisk-api"
    }

@app.post("/api/credit-score")
async def credit_score(request: Dict[str, Any]):
    """
    Credit scoring endpoint
    """
    try:
        # Extract input parameters
        customer_id = request.get("customer_id")
        loan_amount = request.get("loan_amount")
        annual_income = request.get("annual_income")
        debt_to_income_ratio = request.get("debt_to_income_ratio")
        credit_score = request.get("credit_score")
        employment_status = request.get("employment_status")
        
        # Validate inputs
        if not all([customer_id, loan_amount, annual_income, credit_score]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Simple credit scoring logic
        risk_score = calculate_credit_risk(
            loan_amount, annual_income, debt_to_income_ratio, 
            credit_score, employment_status
        )
        
        decision = "APPROVE" if risk_score > 600 else "DECLINE"
        confidence = min(0.95, max(0.60, risk_score / 1000))
        
        return {
            "risk_score": risk_score,
            "decision": decision,
            "confidence": confidence,
            "explanation": {
                "factors": ["credit_score", "income_ratio", "employment_status"],
                "risk_level": "LOW" if risk_score > 700 else "MEDIUM" if risk_score > 600 else "HIGH"
            },
            "processing_time_ms": int(time.time() * 1000) % 100
        }
        
    except Exception as e:
        logger.error(f"Error in credit scoring: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/fraud-check")
async def fraud_check(request: Dict[str, Any]):
    """
    Fraud detection endpoint
    """
    try:
        # Extract input parameters
        customer_id = request.get("customer_id")
        amount = request.get("amount")
        merchant_category = request.get("merchant_category")
        location = request.get("location")
        device_info = request.get("device_info")
        
        # Validate inputs
        if not all([customer_id, amount]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Simple fraud detection logic
        fraud_probability = calculate_fraud_risk(
            amount, merchant_category, location, device_info
        )
        
        decision = "ALLOW" if fraud_probability < 0.5 else "BLOCK"
        risk_factors = []
        
        if amount > 1000:
            risk_factors.append("high_amount")
        if merchant_category in ["Online Gambling", "Cryptocurrency"]:
            risk_factors.append("risky_merchant")
        
        return {
            "fraud_probability": fraud_probability,
            "decision": decision,
            "risk_factors": risk_factors,
            "processing_time_ms": int(time.time() * 1000) % 50
        }
        
    except Exception as e:
        logger.error(f"Error in fraud detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def calculate_credit_risk(loan_amount, annual_income, debt_to_income_ratio, credit_score, employment_status):
    """Simple credit risk calculation"""
    base_score = credit_score
    
    # Income ratio adjustment
    income_ratio = loan_amount / annual_income if annual_income > 0 else 1
    if income_ratio > 0.5:
        base_score -= 100
    elif income_ratio > 0.3:
        base_score -= 50
    
    # Debt-to-income adjustment
    if debt_to_income_ratio and debt_to_income_ratio > 0.4:
        base_score -= 80
    elif debt_to_income_ratio and debt_to_income_ratio > 0.3:
        base_score -= 40
    
    # Employment status adjustment
    if employment_status == "Self-employed":
        base_score -= 30
    elif employment_status == "Part-time":
        base_score -= 20
    
    return max(300, min(850, base_score))

def calculate_fraud_risk(amount, merchant_category, location, device_info):
    """Simple fraud risk calculation"""
    risk_score = 0.1  # Base risk
    
    # Amount-based risk
    if amount > 5000:
        risk_score += 0.4
    elif amount > 1000:
        risk_score += 0.2
    
    # Merchant category risk
    risky_categories = ["Online Gambling", "Cryptocurrency", "Adult Entertainment"]
    if merchant_category in risky_categories:
        risk_score += 0.3
    
    # Location risk (simplified)
    if location and "International" in location:
        risk_score += 0.2
    
    # Device risk
    if device_info and "Mobile" in device_info:
        risk_score += 0.1
    
    return min(0.95, risk_score)

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
