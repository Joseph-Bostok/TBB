"""
Logging Configuration

This module sets up structured logging for the therapy bot application.
Proper logging is essential for:
1. Debugging issues
2. Monitoring system health
3. Auditing safety incidents
4. Analyzing usage patterns

We use JSON-formatted logs for easy parsing and analysis.
"""

import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from config import settings


def setup_logging():
    """
    Configure application-wide logging

    This sets up:
    1. Console logging (for development)
    2. File logging (for production/auditing)
    3. JSON formatting (for structured logs)
    4. Appropriate log levels based on environment
    """

    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []

    # ==================== Console Handler ====================
    # Human-readable format for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # ==================== File Handler ====================
    # JSON format for production logging and analysis
    file_handler = logging.FileHandler(settings.log_file)
    file_handler.setLevel(logging.DEBUG)  # Log everything to file

    # JSON formatter includes all log metadata
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
    )
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)

    # ==================== Initial Log Message ====================
    logging.info("="*60)
    logging.info(f"Therapy Bot Starting - Environment: {settings.environment}")
    logging.info(f"Log Level: {settings.log_level}")
    logging.info(f"Log File: {settings.log_file}")
    logging.info("="*60)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module

    Args:
        name: Usually __name__ of the calling module

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
