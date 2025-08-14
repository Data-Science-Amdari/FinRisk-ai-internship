"""
Configuration settings for FinRisk application.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "FinRisk"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Database
    database_url: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: str = "logs/finrisk.log"
    log_max_size: str = "100MB"
    log_backup_count: int = 5
    
    # Model Paths
    credit_model_path: str = "models/credit_risk_model.pkl"
    fraud_model_path: str = "models/fraud_detection_model.pkl"
    
    # Data Paths
    data_directory: str = "data"
    
    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    # CORS Settings
    cors_origins: str = '["http://localhost:3000"]'
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    # Cache Settings
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
