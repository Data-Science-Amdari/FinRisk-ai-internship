"""
Logging configuration for FinRisk application.
"""

import logging
import sys
from typing import Optional
from .config import settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Log format string
        
    Returns:
        Configured logger instance
    """
    # Use settings if not provided
    level = level or settings.log_level
    format_string = format_string or settings.log_format
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/finrisk.log")
        ]
    )
    
    # Create and return logger
    logger = logging.getLogger("finrisk")
    logger.setLevel(getattr(logging, level.upper()))
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"finrisk.{name}")
