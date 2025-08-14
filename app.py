#!/usr/bin/env python3
"""
FinRisk Application Entry Point
Clean, decoupled MVP for credit risk assessment and fraud detection.
"""

import uvicorn
from src.core.config import settings
from src.core.logging import setup_logging

# Setup logging
logger = setup_logging()

def main():
    """Main application entry point."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"API will be available at http://{settings.api_host}:{settings.api_port}")
    logger.info(f"Documentation available at http://{settings.api_host}:{settings.api_port}/docs")
    
    # Start the FastAPI application
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()
