"""
FinRisk API - Main Application
Clean, decoupled FastAPI application for credit risk assessment and fraud detection.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import REGISTRY

from .routes import credit_router, fraud_router
from ..core.config import settings
from ..core.logging import setup_logging

# Setup logging
logger = setup_logging()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Credit Risk Assessment & Fraud Detection Engine - Clean MVP",
    version=settings.app_version,
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

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Middleware to add processing time and metrics."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record metrics
    REQUEST_LATENCY.observe(process_time)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

# Include routers
app.include_router(credit_router)
app.include_router(fraud_router)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"{settings.app_name} API - Credit Risk Assessment & Fraud Detection Engine",
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "finrisk-api",
        "version": settings.app_version
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return JSONResponse(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
