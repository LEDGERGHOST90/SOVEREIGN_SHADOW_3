"""
📝 Logging Configuration
========================

Centralized logging configuration for the Neural Orchestrator.
Provides structured logging with proper formatting and levels.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured logging for the Neural Orchestrator."""
    
    # Configure structlog
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
    
    # Configure standard logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Set specific logger levels
    loggers = {
        "uvicorn": "INFO",
        "uvicorn.access": "INFO",
        "fastapi": "INFO",
        "neural_orchestrator": "DEBUG",
        "websockets": "WARNING",
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(getattr(logging, level))
    
    # Create main logger
    logger = structlog.get_logger("neural_orchestrator")
    logger.info("🧠 Neural Orchestrator logging initialized", level=log_level)


def get_logger(name: str) -> Any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_system_event(
    event_type: str,
    system_name: str,
    message: str,
    extra_data: Dict[str, Any] = None
) -> None:
    """Log a system-specific event."""
    logger = get_logger("system_events")
    
    log_data = {
        "event_type": event_type,
        "system_name": system_name,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    logger.info("System event", **log_data)


def log_trading_event(
    action: str,
    symbol: str,
    amount: float,
    system: str,
    success: bool,
    extra_data: Dict[str, Any] = None
) -> None:
    """Log a trading event."""
    logger = get_logger("trading_events")
    
    log_data = {
        "action": action,
        "symbol": symbol,
        "amount": amount,
        "system": system,
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    if success:
        logger.info("Trading event", **log_data)
    else:
        logger.warning("Trading event failed", **log_data)


def log_consciousness_update(
    total_value: float,
    change_24h: float,
    change_7d: float,
    extra_data: Dict[str, Any] = None
) -> None:
    """Log a consciousness value update."""
    logger = get_logger("consciousness")
    
    log_data = {
        "total_value": total_value,
        "change_24h": change_24h,
        "change_7d": change_7d,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    logger.info("Consciousness update", **log_data)


def log_websocket_event(
    event_type: str,
    connection_count: int,
    message_type: str = None,
    extra_data: Dict[str, Any] = None
) -> None:
    """Log a WebSocket event."""
    logger = get_logger("websocket")
    
    log_data = {
        "event_type": event_type,
        "connection_count": connection_count,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if message_type:
        log_data["message_type"] = message_type
    
    if extra_data:
        log_data.update(extra_data)
    
    logger.info("WebSocket event", **log_data)


def log_error(
    error_type: str,
    error_message: str,
    system_name: str = None,
    extra_data: Dict[str, Any] = None
) -> None:
    """Log an error event."""
    logger = get_logger("errors")
    
    log_data = {
        "error_type": error_type,
        "error_message": error_message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if system_name:
        log_data["system_name"] = system_name
    
    if extra_data:
        log_data.update(extra_data)
    
    logger.error("Error occurred", **log_data)


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str,
    system_name: str = None,
    extra_data: Dict[str, Any] = None
) -> None:
    """Log a performance metric."""
    logger = get_logger("performance")
    
    log_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if system_name:
        log_data["system_name"] = system_name
    
    if extra_data:
        log_data.update(extra_data)
    
    logger.info("Performance metric", **log_data)
