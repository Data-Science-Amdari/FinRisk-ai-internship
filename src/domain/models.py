"""
Domain models for FinRisk application.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Decision(str, Enum):
    """Decision enumeration."""
    APPROVE = "APPROVE"
    DECLINE = "DECLINE"
    REVIEW = "REVIEW"
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


class EmploymentStatus(str, Enum):
    """Employment status enumeration."""
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    SELF_EMPLOYED = "Self-employed"
    UNEMPLOYED = "Unemployed"
    RETIRED = "Retired"


class RiskScore(BaseModel):
    """Risk score model."""
    score: float = Field(..., ge=0, le=1000, description="Risk score value")
    level: RiskLevel = Field(..., description="Risk level")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the score")
    factors: List[str] = Field(default_factory=list, description="Risk factors")
    explanation: Dict[str, Any] = Field(default_factory=dict, description="Score explanation")
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        if v < 0 or v > 1000:
            raise ValueError('Score must be between 0 and 1000')
        return v
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class CreditApplication(BaseModel):
    """Credit application model."""
    customer_id: str = Field(..., description="Unique customer identifier")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    annual_income: float = Field(..., gt=0, description="Annual income")
    debt_to_income_ratio: Optional[float] = Field(None, ge=0, le=1, description="Debt to income ratio")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    employment_status: EmploymentStatus = Field(..., description="Employment status")
    years_employed: Optional[float] = Field(None, ge=0, description="Years employed")
    requested_at: datetime = Field(default_factory=lambda: datetime.now(), description="Application timestamp")
    
    @field_validator('debt_to_income_ratio')
    @classmethod
    def validate_dti_ratio(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Debt to income ratio must be between 0 and 1')
        return v


class Transaction(BaseModel):
    """Transaction model for fraud detection."""
    customer_id: str = Field(..., description="Unique customer identifier")
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant_category: str = Field(..., description="Merchant category")
    location: Optional[str] = Field(None, description="Transaction location")
    device_info: Optional[str] = Field(None, description="Device information")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="Transaction timestamp")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class CreditDecision(BaseModel):
    """Credit decision model."""
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        protected_namespaces=()
    )
    
    application: CreditApplication
    risk_score: RiskScore
    decision: Decision
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")
    model_version: Optional[str] = Field(None, description="Model version used")


class FraudDecision(BaseModel):
    """Fraud decision model."""
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        protected_namespaces=()
    )
    
    transaction: Transaction
    fraud_probability: float = Field(..., ge=0, le=1, description="Fraud probability")
    decision: Decision
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")
    model_version: Optional[str] = Field(None, description="Model version used")
