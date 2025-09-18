"""
Logging utilities for Baker Compliant AI inference system.

Provides structured logging with compliance requirements and
audit trail support using structlog.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory


def configure_logging(log_level: str = "INFO", service_name: str = "Baker-Inference-Service") -> None:
    """
    Configure structured logging for the inference service.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Name of the service for logging context
    """
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(message)s',
        stream=sys.stdout
    )
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Add file handler for persistent logging
    file_handler = logging.FileHandler(
        logs_dir / "baker-inference.log",
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level.upper())),
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=False,
    )
    
    # Set service context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_inference_request(
    request_id: str,
    model: str,
    message_content: str,
    custom_gpt_id: str,
    user_id: str,
    priority: int
) -> None:
    """Log an inference request with audit trail."""
    logger = get_logger("inference.request")
    logger.info(
        "Inference request received",
        request_id=request_id,
        model=model,
        custom_gpt_id=custom_gpt_id,
        user_id=user_id,
        priority=priority,
        message_length=len(message_content),
        event_type="inference_request_start"
    )


def log_inference_response(
    request_id: str,
    success: bool,
    processing_time_ms: int,
    model_used: str,
    confidence_score: Optional[float] = None,
    error_message: Optional[str] = None
) -> None:
    """Log an inference response with audit trail."""
    logger = get_logger("inference.response")
    
    log_data = {
        "request_id": request_id,
        "success": success,
        "processing_time_ms": processing_time_ms,
        "model_used": model_used,
        "event_type": "inference_request_complete"
    }
    
    if confidence_score is not None:
        log_data["confidence_score"] = confidence_score
    
    if success:
        logger.info("Inference request completed successfully", **log_data)
    else:
        log_data["error_message"] = error_message
        logger.error("Inference request failed", **log_data)


def log_queue_operation(
    operation: str,
    request_id: str,
    priority: int,
    queue_size: int,
    processing_time_ms: Optional[int] = None
) -> None:
    """Log queue operations for monitoring."""
    logger = get_logger("inference.queue")
    logger.debug(
        f"Queue operation: {operation}",
        operation=operation,
        request_id=request_id,
        priority=priority,
        queue_size=queue_size,
        processing_time_ms=processing_time_ms,
        event_type="queue_operation"
    )


def log_model_operation(
    operation: str,
    model: str,
    duration_ms: Optional[int] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> None:
    """Log model operations for GPU resource monitoring."""
    logger = get_logger("inference.model")
    
    log_data = {
        "operation": operation,
        "model": model,
        "success": success,
        "event_type": "model_operation"
    }
    
    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms
    
    if success:
        logger.debug(f"Model operation: {operation}", **log_data)
    else:
        log_data["error_message"] = error_message
        logger.error(f"Model operation failed: {operation}", **log_data)


def log_compliance_event(
    event_type: str,
    user_id: str,
    request_id: str,
    details: Dict[str, Any]
) -> None:
    """Log compliance-related events for audit trail."""
    logger = get_logger("inference.compliance")
    logger.info(
        f"Compliance event: {event_type}",
        event_type=event_type,
        user_id=user_id,
        request_id=request_id,
        **details
    )


# Create a default logger instance
logger = get_logger("inference.service")


# Alias functions for backwards compatibility
def log_inference_operation(
    operation: str,
    request_id: str,
    **kwargs
) -> None:
    """Log inference operations (alias for log_inference_request)."""
    logger = get_logger("inference.operation")
    logger.info(
        f"Inference operation: {operation}",
        operation=operation,
        request_id=request_id,
        event_type="inference_operation",
        **kwargs
    )


# Enhanced error handling and compliance logging
def log_error_with_context(
    error_type: str,
    error_message: str,
    request_id: str = None,
    user_id: str = None,
    context: Dict[str, Any] = None,
    exc_info: bool = True
) -> None:
    """
    Log errors with full context for debugging and compliance.
    
    Args:
        error_type: Category of error (validation, model, timeout, etc.)
        error_message: Human-readable error description
        request_id: Optional request identifier
        user_id: Optional user identifier
        context: Additional context data
        exc_info: Whether to include exception traceback
    """
    logger = get_logger("inference.error")
    
    log_data = {
        "error_type": error_type,
        "error_message": error_message,
        "event_type": "error_occurred"
    }
    
    if request_id:
        log_data["request_id"] = request_id
    if user_id:
        log_data["user_id"] = user_id
    if context:
        log_data.update(context)
    
    logger.error(
        f"Error: {error_type}",
        exc_info=exc_info,
        **log_data
    )


def log_compliance_audit(
    action: str,
    user_id: str,
    request_id: str,
    compliance_status: str,
    details: Dict[str, Any] = None
) -> None:
    """
    Log compliance-related actions for SEC audit trail.
    
    Args:
        action: Action performed (chat_request, model_output, compliance_check)
        user_id: User performing the action
        request_id: Associated request ID
        compliance_status: COMPLIANT, NON_COMPLIANT, or REVIEW_REQUIRED
        details: Additional compliance-related data
    """
    logger = get_logger("inference.compliance")
    
    log_data = {
        "action": action,
        "user_id": user_id,
        "request_id": request_id,
        "compliance_status": compliance_status,
        "event_type": "compliance_audit",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data["details"] = details
    
    logger.info(
        f"Compliance audit: {action}",
        **log_data
    )


def log_performance_metric(
    metric_type: str,
    value: float,
    unit: str,
    request_id: str = None,
    context: Dict[str, Any] = None
) -> None:
    """
    Log performance metrics for monitoring and optimization.
    
    Args:
        metric_type: Type of metric (processing_time, queue_wait, gpu_usage)
        value: Numeric value of the metric
        unit: Unit of measurement (ms, seconds, percentage)
        request_id: Optional request identifier
        context: Additional context data
    """
    logger = get_logger("inference.performance")
    
    log_data = {
        "metric_type": metric_type,
        "value": value,
        "unit": unit,
        "event_type": "performance_metric"
    }
    
    if request_id:
        log_data["request_id"] = request_id
    if context:
        log_data.update(context)
    
    logger.info(
        f"Performance metric: {metric_type}",
        **log_data
    )


def log_retry_attempt(
    operation: str,
    attempt_number: int,
    max_attempts: int,
    error_reason: str,
    request_id: str = None
) -> None:
    """
    Log retry attempts for operations.
    
    Args:
        operation: Operation being retried
        attempt_number: Current attempt number (1-based)
        max_attempts: Maximum number of attempts
        error_reason: Reason for the retry
        request_id: Optional request identifier
    """
    logger = get_logger("inference.retry")
    
    log_data = {
        "operation": operation,
        "attempt_number": attempt_number,
        "max_attempts": max_attempts,
        "error_reason": error_reason,
        "event_type": "retry_attempt"
    }
    
    if request_id:
        log_data["request_id"] = request_id
    
    if attempt_number >= max_attempts:
        logger.error(f"Final retry failed: {operation}", **log_data)
    else:
        logger.warning(f"Retry attempt {attempt_number}: {operation}", **log_data)