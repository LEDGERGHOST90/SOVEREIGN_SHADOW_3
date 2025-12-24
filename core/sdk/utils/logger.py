"""
📝 Shadow SDK Logger

Unified logging system for the entire Sovereign Shadow empire.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "shadow_sdk", level: int = logging.INFO, log_file: str = None) -> logging.Logger:
    """
    Set up a logger for Shadow SDK.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get an existing logger or create a new one."""
    return logging.getLogger(name)

