"""
Main FastAPI application for FinRisk API
"""

import os
import yaml
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import structlog

from .credit_endpoints import router as credit_router
from .fraud_endpoints import router as fraud_router
from .models import HealthResponse, ErrorResponse

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Load configuration
def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.yaml")
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.warning("Configuration file not found, using defaults")
        return {}

config = load_config()

# Security
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    if not config.get('api', {}).get('authentication', {}).get('enabled', False):
        return True
    
    # In a real implementation, you would verify the JWT token here
    # For MVP, we'll just check if the token exists
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Create FastAPI app
app = FastAPI(
    title="FinRisk API",
    description="Financial Risk Management API for credit scoring and fraud detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('api', {}).get('cors_origins', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Include routers
app.include_router(
    credit_router,
    prefix="/api/v1/credit",
    tags=["credit"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    fraud_router,
    prefix="/api/v1/fraud",
    tags=["fraud"],
    dependencies=[Depends(verify_token)]
)

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check"""
    return HealthResponse(
        status="healthy",
        message="FinRisk API is running",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Service is operational",
        version="1.0.0"
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return ErrorResponse(
        error=True,
        message=exc.detail,
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    logger.error(
        "Unexpected error occurred",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return ErrorResponse(
        error=True,
        message="Internal server error",
        status_code=500
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.get('app', {}).get('host', '0.0.0.0'),
        port=config.get('app', {}).get('port', 8000),
        reload=config.get('app', {}).get('debug', False)
    )
