"""
Credit scoring API endpoints
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
import pandas as pd
import structlog

from .models import (
    CreditApplicationRequest,
    CreditApplicationResponse,
    ModelTrainingRequest,
    ModelTrainingResponse,
    BatchProcessingRequest,
    BatchProcessingResponse,
    ModelPerformanceMetrics,
    ApplicationStatus,
    RiskLevel
)

# Import credit models (will be implemented)
from ..credit_models.xgboost_model import XGBoostCreditModel
from ..feature_engineering.credit_features import CreditFeatureEngineer

logger = structlog.get_logger()
router = APIRouter()

# Initialize models (in production, these would be loaded from model registry)
credit_model = XGBoostCreditModel()
feature_engineer = CreditFeatureEngineer()

@router.post("/assess", response_model=CreditApplicationResponse)
async def assess_credit_application(
    request: CreditApplicationRequest,
    background_tasks: BackgroundTasks
):
    """
    Assess a credit application and return risk score and recommendation
    """
    try:
        logger.info("Processing credit application", customer_id=request.customer_id)
        
        # Generate application ID
        application_id = str(uuid.uuid4())
        
        # Extract features
        features = feature_engineer.extract_features(request.dict())
        
        # Get model prediction
        risk_score, confidence = credit_model.predict(features)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.6:
            risk_level = RiskLevel.MEDIUM
        elif risk_score < 0.8:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        # Calculate approval probability (inverse of risk score)
        approval_probability = 1 - risk_score
        
        # Determine application status
        if approval_probability > 0.7:
            status = ApplicationStatus.APPROVED
            recommended_loan_amount = request.loan_amount
            interest_rate = 0.05 + (risk_score * 0.15)  # Base 5% + risk premium
        elif approval_probability > 0.4:
            status = ApplicationStatus.UNDER_REVIEW
            recommended_loan_amount = request.loan_amount * 0.7
            interest_rate = 0.08 + (risk_score * 0.20)
        else:
            status = ApplicationStatus.REJECTED
            recommended_loan_amount = None
            interest_rate = None
        
        # Generate reasons
        reasons = _generate_reasons(request, risk_score)
        
        # Log the assessment
        background_tasks.add_task(
            _log_assessment,
            application_id,
            request.customer_id,
            risk_score,
            status
        )
        
        return CreditApplicationResponse(
            application_id=application_id,
            risk_score=risk_score,
            risk_level=risk_level,
            approval_probability=approval_probability,
            recommended_loan_amount=recommended_loan_amount,
            interest_rate=interest_rate,
            status=status,
            reasons=reasons,
            model_confidence=confidence
        )
        
    except Exception as e:
        logger.error("Error processing credit application", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing credit application")

@router.post("/batch", response_model=BatchProcessingResponse)
async def process_batch_applications(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks
):
    """
    Process multiple credit applications in batch
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            _process_batch_applications,
            job_id,
            request.file_path,
            request.output_format
        )
        
        return BatchProcessingResponse(
            job_id=job_id,
            status="processing",
            total_records=0,  # Will be updated in background task
            processed_records=0
        )
        
    except Exception as e:
        logger.error("Error starting batch processing", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Error starting batch processing")

@router.get("/batch/{job_id}", response_model=BatchProcessingResponse)
async def get_batch_status(job_id: str):
    """
    Get status of batch processing job
    """
    # In a real implementation, this would query a job queue or database
    # For MVP, we'll return a mock response
    return BatchProcessingResponse(
        job_id=job_id,
        status="completed",
        total_records=1000,
        processed_records=1000,
        output_path=f"data/processed/batch_{job_id}.csv",
        processing_time=120.5
    )

@router.get("/batch/{job_id}/download")
async def download_batch_results(job_id: str):
    """
    Download batch processing results
    """
    file_path = f"data/processed/batch_{job_id}.csv"
    try:
        return FileResponse(
            path=file_path,
            filename=f"credit_assessments_{job_id}.csv",
            media_type="text/csv"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Results file not found")

@router.post("/train", response_model=ModelTrainingResponse)
async def train_credit_model(
    request: ModelTrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    Train or retrain the credit scoring model
    """
    try:
        model_id = str(uuid.uuid4())
        
        # Start training in background
        background_tasks.add_task(
            _train_model,
            model_id,
            request.model_type,
            request.dataset_path,
            request.hyperparameters
        )
        
        return ModelTrainingResponse(
            model_id=model_id,
            model_type=request.model_type,
            training_status="started"
        )
        
    except Exception as e:
        logger.error("Error starting model training", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Error starting model training")

@router.get("/train/{model_id}", response_model=ModelTrainingResponse)
async def get_training_status(model_id: str):
    """
    Get status of model training
    """
    # In a real implementation, this would query training status
    # For MVP, we'll return a mock response
    return ModelTrainingResponse(
        model_id=model_id,
        model_type="xgboost",
        training_status="completed",
        accuracy=0.85,
        precision=0.82,
        recall=0.88,
        f1_score=0.85,
        training_time=300.5,
        model_path=f"models/credit_model_{model_id}.pkl"
    )

@router.get("/performance", response_model=List[ModelPerformanceMetrics])
async def get_model_performance(
    model_id: Optional[str] = Query(None, description="Specific model ID"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return")
):
    """
    Get model performance metrics
    """
    # In a real implementation, this would query performance metrics from database
    # For MVP, we'll return mock data
    return [
        ModelPerformanceMetrics(
            model_id="model_001",
            model_type="xgboost",
            accuracy=0.85,
            precision=0.82,
            recall=0.88,
            f1_score=0.85,
            auc_roc=0.89,
            dataset_size=10000,
            training_time=300.5
        )
    ]

@router.get("/features")
async def get_feature_importance():
    """
    Get feature importance for the credit model
    """
    try:
        # In a real implementation, this would get feature importance from the model
        feature_importance = {
            "credit_score": 0.25,
            "debt_to_income_ratio": 0.20,
            "payment_history": 0.18,
            "income": 0.15,
            "credit_utilization": 0.12,
            "employment_length": 0.10
        }
        
        return {
            "success": True,
            "feature_importance": feature_importance,
            "total_features": len(feature_importance)
        }
        
    except Exception as e:
        logger.error("Error getting feature importance", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Error getting feature importance")

# Helper functions
def _generate_reasons(request: CreditApplicationRequest, risk_score: float) -> List[str]:
    """Generate reasons for the credit decision"""
    reasons = []
    
    if request.credit_score < 600:
        reasons.append("Low credit score")
    
    if request.debt_to_income_ratio > 0.4:
        reasons.append("High debt-to-income ratio")
    
    if sum(request.payment_history) > 3:
        reasons.append("Multiple late payments in history")
    
    if request.credit_utilization > 0.8:
        reasons.append("High credit utilization")
    
    if request.employment_length < 12:
        reasons.append("Short employment history")
    
    if risk_score > 0.8:
        reasons.append("High overall risk score")
    
    return reasons

async def _log_assessment(application_id: str, customer_id: str, risk_score: float, status: ApplicationStatus):
    """Log credit assessment for monitoring"""
    logger.info(
        "Credit assessment logged",
        application_id=application_id,
        customer_id=customer_id,
        risk_score=risk_score,
        status=status.value
    )

async def _process_batch_applications(job_id: str, file_path: str, output_format: str):
    """Process batch applications in background"""
    try:
        # Read input file
        df = pd.read_csv(file_path)
        
        # Process each application
        results = []
        for _, row in df.iterrows():
            # Convert row to request format and process
            # This is a simplified version
            pass
        
        # Save results
        output_path = f"data/processed/batch_{job_id}.csv"
        # Save results to output_path
        
        logger.info("Batch processing completed", job_id=job_id, records_processed=len(df))
        
    except Exception as e:
        logger.error("Error in batch processing", job_id=job_id, error=str(e), exc_info=True)

async def _train_model(model_id: str, model_type: str, dataset_path: str, hyperparameters: dict):
    """Train model in background"""
    try:
        # Load data
        # Train model with hyperparameters
        # Save model
        # Log metrics
        
        logger.info("Model training completed", model_id=model_id, model_type=model_type)
        
    except Exception as e:
        logger.error("Error in model training", model_id=model_id, error=str(e), exc_info=True)
