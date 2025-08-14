"""
MLflow client for model management and tracking.
"""

import mlflow
from typing import Optional, Dict, Any
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class MLflowClient:
    """MLflow client for model management."""
    
    def __init__(self, tracking_uri: Optional[str] = None):
        self.tracking_uri = tracking_uri or settings.mlflow_tracking_uri
        self.logger = logger
        
        # Set tracking URI
        mlflow.set_tracking_uri(self.tracking_uri)
    
    def log_credit_decision(self, decision_data: Dict[str, Any]) -> bool:
        """Log credit decision to MLflow."""
        try:
            with mlflow.start_run(run_name="credit_decision"):
                # Log parameters
                mlflow.log_param("customer_id", decision_data.get("customer_id", ""))
                mlflow.log_param("loan_amount", decision_data.get("loan_amount", 0))
                mlflow.log_param("credit_score", decision_data.get("credit_score", 0))
                
                # Log metrics
                mlflow.log_metric("risk_score", decision_data.get("risk_score", 0))
                mlflow.log_metric("confidence", decision_data.get("confidence", 0))
                mlflow.log_metric("processing_time_ms", decision_data.get("processing_time_ms", 0))
                
                # Log decision
                mlflow.log_param("decision", decision_data.get("decision", ""))
                
            self.logger.info(f"Credit decision logged to MLflow: {decision_data.get('customer_id')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging credit decision to MLflow: {str(e)}")
            return False
    
    def log_fraud_decision(self, decision_data: Dict[str, Any]) -> bool:
        """Log fraud decision to MLflow."""
        try:
            with mlflow.start_run(run_name="fraud_decision"):
                # Log parameters
                mlflow.log_param("customer_id", decision_data.get("customer_id", ""))
                mlflow.log_param("transaction_id", decision_data.get("transaction_id", ""))
                mlflow.log_param("amount", decision_data.get("amount", 0))
                mlflow.log_param("merchant_category", decision_data.get("merchant_category", ""))
                
                # Log metrics
                mlflow.log_metric("fraud_probability", decision_data.get("fraud_probability", 0))
                mlflow.log_metric("processing_time_ms", decision_data.get("processing_time_ms", 0))
                
                # Log decision
                mlflow.log_param("decision", decision_data.get("decision", ""))
                
            self.logger.info(f"Fraud decision logged to MLflow: {decision_data.get('transaction_id')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging fraud decision to MLflow: {str(e)}")
            return False
    
    def get_model_version(self, model_name: str) -> Optional[str]:
        """Get the latest model version."""
        try:
            client = mlflow.tracking.MlflowClient()
            latest_version = client.get_latest_versions(model_name, stages=["Production"])
            
            if latest_version:
                return latest_version[0].version
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting model version: {str(e)}")
            return None
