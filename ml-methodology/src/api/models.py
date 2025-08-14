"""
Pydantic models for API requests and responses
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: bool = True
    message: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Credit Application Models
class CreditApplicationRequest(BaseModel):
    """Credit application request model"""
    customer_id: str = Field(..., description="Unique customer identifier")
    income: float = Field(..., gt=0, description="Annual income")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    debt_to_income_ratio: float = Field(..., ge=0, le=1, description="Debt to income ratio")
    employment_length: int = Field(..., ge=0, description="Employment length in months")
    age: int = Field(..., ge=18, le=100, description="Customer age")
    credit_utilization: float = Field(..., ge=0, le=1, description="Credit utilization ratio")
    payment_history: List[int] = Field(..., description="Payment history (0=on time, 1=late)")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_purpose: str = Field(..., description="Purpose of the loan")
    
    @validator('payment_history')
    def validate_payment_history(cls, v):
        if len(v) < 12:
            raise ValueError('Payment history must contain at least 12 months')
        if not all(x in [0, 1] for x in v):
            raise ValueError('Payment history must contain only 0 or 1 values')
        return v

class CreditApplicationResponse(BaseResponse):
    """Credit application response model"""
    application_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    approval_probability: float = Field(..., ge=0, le=1)
    recommended_loan_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    status: ApplicationStatus
    reasons: List[str] = []
    model_confidence: float = Field(..., ge=0, le=1)

# Fraud Detection Models
class TransactionRequest(BaseModel):
    """Transaction request model for fraud detection"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    customer_id: str = Field(..., description="Customer identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant_category: str = Field(..., description="Merchant category code")
    location: str = Field(..., description="Transaction location")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    device_id: Optional[str] = Field(None, description="Device identifier")
    ip_address: Optional[str] = Field(None, description="IP address")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Transaction amount must be positive')
        return v

class FraudDetectionResponse(BaseResponse):
    """Fraud detection response model"""
    transaction_id: str
    fraud_score: float = Field(..., ge=0, le=1)
    is_fraudulent: bool
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1)
    risk_factors: List[str] = []
    recommended_action: str

# Model Training Models
class ModelTrainingRequest(BaseModel):
    """Model training request model"""
    model_type: str = Field(..., description="Type of model to train")
    dataset_path: str = Field(..., description="Path to training dataset")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Model hyperparameters")
    validation_split: float = Field(0.2, ge=0.1, le=0.5, description="Validation split ratio")

class ModelTrainingResponse(BaseResponse):
    """Model training response model"""
    model_id: str
    model_type: str
    training_status: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    training_time: Optional[float] = None
    model_path: Optional[str] = None

# Feature Engineering Models
class FeatureRequest(BaseModel):
    """Feature engineering request model"""
    data: Dict[str, Any] = Field(..., description="Raw data for feature engineering")
    feature_types: List[str] = Field(..., description="Types of features to generate")

class FeatureResponse(BaseResponse):
    """Feature engineering response model"""
    features: Dict[str, Any] = Field(..., description="Generated features")
    feature_names: List[str] = Field(..., description="Names of generated features")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Feature importance scores")

# Monitoring Models
class ModelPerformanceMetrics(BaseModel):
    """Model performance metrics model"""
    model_id: str
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dataset_size: int
    training_time: float

class DriftDetectionResponse(BaseResponse):
    """Data drift detection response model"""
    model_id: str
    drift_detected: bool
    drift_score: float = Field(..., ge=0, le=1)
    affected_features: List[str] = []
    confidence: float = Field(..., ge=0, le=1)
    recommendation: str

# Batch Processing Models
class BatchProcessingRequest(BaseModel):
    """Batch processing request model"""
    file_path: str = Field(..., description="Path to input file")
    processing_type: str = Field(..., description="Type of processing (credit/fraud)")
    output_format: str = Field(default="csv", description="Output format")
    
    @validator('processing_type')
    def validate_processing_type(cls, v):
        if v not in ['credit', 'fraud']:
            raise ValueError('Processing type must be either "credit" or "fraud"')
        return v

class BatchProcessingResponse(BaseResponse):
    """Batch processing response model"""
    job_id: str
    status: str
    total_records: int
    processed_records: int
    output_path: Optional[str] = None
    processing_time: Optional[float] = None
    errors: List[str] = []

# Configuration Models
class ModelConfiguration(BaseModel):
    """Model configuration model"""
    model_type: str
    hyperparameters: Dict[str, Any]
    threshold: float = Field(..., ge=0, le=1)
    retrain_frequency: str
    feature_columns: List[str]
    target_column: str

class SystemConfiguration(BaseModel):
    """System configuration model"""
    database_url: str
    api_rate_limit: int
    log_level: str
    environment: str
    monitoring_enabled: bool
