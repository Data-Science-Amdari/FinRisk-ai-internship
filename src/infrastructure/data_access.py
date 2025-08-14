"""
Data access layer for FinRisk application.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class DataRepository:
    """Data repository for handling data operations."""
    
    def __init__(self, data_directory: Optional[str] = None):
        self.data_directory = Path(data_directory or settings.data_directory)
        self.logger = logger
        
        # Ensure data directory exists
        self.data_directory.mkdir(exist_ok=True)
    
    def load_credit_applications(self) -> pd.DataFrame:
        """Load credit applications data."""
        file_path = self.data_directory / "credit_applications.csv"
        if file_path.exists():
            return pd.read_csv(file_path)
        else:
            self.logger.warning(f"Credit applications file not found: {file_path}")
            return pd.DataFrame()
    
    def load_customer_profiles(self) -> pd.DataFrame:
        """Load customer profiles data."""
        file_path = self.data_directory / "customer_profiles.csv"
        if file_path.exists():
            return pd.read_csv(file_path)
        else:
            self.logger.warning(f"Customer profiles file not found: {file_path}")
            return pd.DataFrame()
    
    def load_transaction_data(self) -> pd.DataFrame:
        """Load transaction data."""
        file_path = self.data_directory / "transaction_data.csv"
        if file_path.exists():
            return pd.read_csv(file_path)
        else:
            self.logger.warning(f"Transaction data file not found: {file_path}")
            return pd.DataFrame()
    
    def save_credit_decision(self, decision_data: Dict[str, Any]) -> bool:
        """Save credit decision to storage."""
        try:
            file_path = self.data_directory / "credit_decisions.csv"
            
            # Convert to DataFrame
            df = pd.DataFrame([decision_data])
            
            # Append to existing file or create new
            if file_path.exists():
                df.to_csv(file_path, mode='a', header=False, index=False)
            else:
                df.to_csv(file_path, index=False)
            
            self.logger.info(f"Credit decision saved: {decision_data.get('customer_id')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving credit decision: {str(e)}")
            return False
    
    def save_fraud_decision(self, decision_data: Dict[str, Any]) -> bool:
        """Save fraud decision to storage."""
        try:
            file_path = self.data_directory / "fraud_decisions.csv"
            
            # Convert to DataFrame
            df = pd.DataFrame([decision_data])
            
            # Append to existing file or create new
            if file_path.exists():
                df.to_csv(file_path, mode='a', header=False, index=False)
            else:
                df.to_csv(file_path, index=False)
            
            self.logger.info(f"Fraud decision saved: {decision_data.get('transaction_id')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving fraud decision: {str(e)}")
            return False
    
    def get_decision_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get decision history for a customer."""
        try:
            credit_file = self.data_directory / "credit_decisions.csv"
            fraud_file = self.data_directory / "fraud_decisions.csv"
            
            history = []
            
            # Load credit decisions
            if credit_file.exists():
                credit_df = pd.read_csv(credit_file)
                customer_credits = credit_df[credit_df['customer_id'] == customer_id]
                for _, row in customer_credits.iterrows():
                    history.append({
                        'type': 'credit',
                        'timestamp': row.get('timestamp', ''),
                        'decision': row.get('decision', ''),
                        'risk_score': row.get('risk_score', '')
                    })
            
            # Load fraud decisions
            if fraud_file.exists():
                fraud_df = pd.read_csv(fraud_file)
                customer_frauds = fraud_df[fraud_df['customer_id'] == customer_id]
                for _, row in customer_frauds.iterrows():
                    history.append({
                        'type': 'fraud',
                        'timestamp': row.get('timestamp', ''),
                        'decision': row.get('decision', ''),
                        'fraud_probability': row.get('fraud_probability', '')
                    })
            
            return sorted(history, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting decision history: {str(e)}")
            return []
