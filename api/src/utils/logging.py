"""
Structured logging configuration for the Baker Compliant AI system.

This module provides centralized logging setup following the instructions
from logger_reference.instructions.md with structured logging for compliance.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.typing import FilteringBoundLogger

from .config import get_settings


def setup_logging() -> FilteringBoundLogger:
    """
    Configure structured logging for the application.
    
    Returns:
        FilteringBoundLogger: Configured logger instance
    """
    settings = get_settings()
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.value),
    )
    
    # Configure file handler with rotation
    log_file_path = settings.get_log_file_path()
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        maxBytes=_parse_size(settings.log_rotation_size),
        backupCount=settings.log_retention_days,
    )
    file_handler.setLevel(getattr(logging, settings.log_level.value))
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _add_service_info,
            _add_compliance_context,
            structlog.dev.ConsoleRenderer() if settings.is_development 
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.value)
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    return structlog.get_logger()


def _parse_size(size_str: str) -> int:
    """Parse size string like '10 MB' to bytes."""
    size_str = size_str.strip().upper()
    if size_str.endswith('MB'):
        return int(size_str[:-2].strip()) * 1024 * 1024
    elif size_str.endswith('KB'):
        return int(size_str[:-2].strip()) * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2].strip()) * 1024 * 1024 * 1024
    else:
        return int(size_str)


def _add_service_info(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add service information to log entries."""
    settings = get_settings()
    event_dict["service"] = "baker-compliant-ai"
    event_dict["version"] = settings.api_version
    event_dict["environment"] = settings.environment.value
    return event_dict


def _add_compliance_context(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add compliance context for audit trails."""
    # Add compliance-specific fields if they exist in context
    compliance_fields = ["user_id", "client_id", "action", "resource", "sec_compliant"]
    for field in compliance_fields:
        if field in event_dict:
            event_dict[f"compliance_{field}"] = event_dict[field]
    
    return event_dict


# Create logger instance
logger = setup_logging()


class AuditLogger:
    """
    Specialized logger for SEC compliance audit trails.
    
    All actions that require audit logging should use this class.
    """
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict[str, Any] = None,
        client_id: str = None,
        sec_compliant: bool = True,
    ) -> None:
        """
        Log a user action for audit trail.
        
        Args:
            user_id: ID of the user performing the action
            action: Action being performed (e.g., 'create_message', 'delete_thread')
            resource: Resource being acted upon (e.g., 'message', 'thread')
            details: Additional action details
            client_id: Associated client ID if applicable
            sec_compliant: Whether the action meets SEC compliance
        """
        log_data = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "sec_compliant": sec_compliant,
        }
        
        if client_id:
            log_data["client_id"] = client_id
        
        if details:
            log_data["details"] = details
        
        self.logger.info("User action performed", **log_data)
    
    def log_ai_inference(
        self,
        request_id: str,
        model_used: str,
        user_id: str,
        input_tokens: int = None,
        output_tokens: int = None,
        confidence_score: float = None,
        sec_compliant: bool = True,
        processing_time_ms: int = None,
    ) -> None:
        """
        Log AI inference for audit trail.
        
        Args:
            request_id: Unique request identifier
            model_used: AI model that processed the request
            user_id: User who initiated the request
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            confidence_score: AI confidence score
            sec_compliant: Whether the result meets SEC compliance
            processing_time_ms: Processing time in milliseconds
        """
        log_data = {
            "request_id": request_id,
            "model_used": model_used,
            "user_id": user_id,
            "sec_compliant": sec_compliant,
            "action": "ai_inference",
            "resource": "llm_model",
        }
        
        if input_tokens is not None:
            log_data["input_tokens"] = input_tokens
        if output_tokens is not None:
            log_data["output_tokens"] = output_tokens
        if confidence_score is not None:
            log_data["confidence_score"] = confidence_score
        if processing_time_ms is not None:
            log_data["processing_time_ms"] = processing_time_ms
        
        self.logger.info("AI inference completed", **log_data)
    
    def log_mcp_interaction(
        self,
        tool_name: str,
        action: str,
        user_id: str,
        success: bool,
        data: Dict[str, Any] = None,
        error_message: str = None,
    ) -> None:
        """
        Log MCP tool interaction for audit trail.
        
        Args:
            tool_name: Name of the MCP tool
            action: Action performed
            user_id: User who initiated the interaction
            success: Whether the interaction was successful
            data: Interaction data
            error_message: Error message if failed
        """
        log_data = {
            "tool_name": tool_name,
            "action": f"mcp_{action}",
            "resource": "mcp_tool",
            "user_id": user_id,
            "success": success,
            "sec_compliant": True,  # MCP interactions are always compliant
        }
        
        if data:
            log_data["interaction_data"] = data
        if error_message:
            log_data["error_message"] = error_message
        
        if success:
            self.logger.info("MCP tool interaction successful", **log_data)
        else:
            self.logger.error("MCP tool interaction failed", **log_data)


# Global audit logger instance
audit_logger = AuditLogger()