"""
Configuration management for Baker Compliant AI inference service.

Handles environment variables, settings validation, and configuration
management for the inference system.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class OllamaSettings(BaseModel):
    """Ollama model configuration."""
    base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Ollama service base URL with OpenAI-compatible API endpoint"
    )
    chat_model: str = Field(
        default="gpt-oss",
        description="Primary chat model for general conversations"
    )
    vision_model: str = Field(
        default="llama3.2-vision:11b", 
        description="Vision-capable model for document analysis"
    )
    request_timeout: int = Field(
        default=300,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed requests"
    )


class DatabaseSettings(BaseModel):
    """Database configuration."""
    path: str = Field(
        default="./database/baker_compliant_ai.db",
        description="Shared SQLite database file path"
    )
    connection_timeout: int = Field(
        default=30,
        description="Database connection timeout in seconds"
    )
    query_timeout: int = Field(
        default=60,
        description="Query execution timeout in seconds"
    )


class ServiceSettings(BaseModel):
    """Service operational configuration."""
    max_concurrent_requests: int = Field(
        default=5,
        description="Maximum concurrent inference requests"
    )
    queue_poll_interval: float = Field(
        default=2.0,
        description="Queue polling interval in seconds"
    )
    max_queue_retries: int = Field(
        default=3,
        description="Maximum retries for queue operations"
    )
    error_retry_delay: float = Field(
        default=5.0,
        description="Delay between error retries in seconds"
    )
    graceful_shutdown_timeout: int = Field(
        default=30,
        description="Graceful shutdown timeout in seconds"
    )
    gpu_timeout_seconds: int = Field(
        default=300,
        description="GPU resource acquisition timeout in seconds (5 minutes)"
    )
    poll_interval_seconds: float = Field(
        default=2.0,
        description="Main loop polling interval in seconds"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Optional log file path"
    )


class MCPSettings(BaseModel):
    """Model Context Protocol (MCP) configuration."""
    enabled: bool = Field(
        default=False,
        description="Enable MCP tools integration"
    )
    redtail_crm_enabled: bool = Field(
        default=False,
        description="Enable Redtail CRM MCP server"
    )
    albridge_enabled: bool = Field(
        default=False,
        description="Enable Albridge MCP server"
    )
    mcp_server_timeout: int = Field(
        default=30,
        description="MCP server request timeout in seconds"
    )


class InferenceSettings(BaseSettings):
    """Main configuration settings for the inference service."""
    
    # Service identification
    service_name: str = Field(
        default="Baker-Inference-Service",
        description="Service name for logging and identification"
    )
    environment: str = Field(
        default="development",
        description="Environment: development, production"
    )
    
    # Nested configurations
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    service: ServiceSettings = Field(default_factory=ServiceSettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    
    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    enable_audit_logging: bool = Field(
        default=True,
        description="Enable audit trail logging for compliance"
    )
    
    class Config:
        env_prefix = "BAKER_INFERENCE_"
        env_nested_delimiter = "__"
        case_sensitive = False
    
    @classmethod
    def from_env(cls) -> "InferenceSettings":
        """Create settings from environment variables."""
        return cls()
    
    def get_absolute_database_path(self) -> Path:
        """Get absolute path to the database file."""
        db_path = Path(self.database.path)
        if not db_path.is_absolute():
            # Make relative to the project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            db_path = project_root / self.database.path
        return db_path.resolve()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for logging."""
        return {
            "service_name": self.service_name,
            "environment": self.environment,
            "ollama_base_url": self.ollama.base_url,
            "chat_model": self.ollama.chat_model,
            "vision_model": self.ollama.vision_model,
            "database_path": str(self.get_absolute_database_path()),
            "mcp_enabled": self.mcp.enabled,
            "log_level": self.log_level
        }
    
    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_dir: Optional[str] = Field(
        default="logs",
        description="Log directory path"
    )
    
    # Model management
    model_warmup: bool = Field(
        default=True,
        description="Warm up models on startup"
    )
    gpu_memory_fraction: float = Field(
        default=0.8,
        description="GPU memory fraction to use"
    )
    
    # Compliance settings
    enable_audit_logging: bool = Field(
        default=True,
        description="Enable compliance audit logging"
    )
    human_review_threshold: float = Field(
        default=0.7,
        description="Confidence threshold for human review"
    )
    
    @classmethod
    def from_env(cls) -> "InferenceSettings":
        """Load settings from environment variables."""
        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            chat_model=os.getenv("CHAT_MODEL", "gpt-oss:latest"),
            vision_model=os.getenv("VISION_MODEL", "llama3.2-vision:11b"),
            database_path=os.getenv("DATABASE_PATH", "../api/database/baker_compliant_ai.db"),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "5")),
            queue_poll_interval=float(os.getenv("QUEUE_POLL_INTERVAL", "1.0")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "300")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_dir=os.getenv("LOG_DIR", "logs"),
            model_warmup=os.getenv("MODEL_WARMUP", "true").lower() == "true",
            gpu_memory_fraction=float(os.getenv("GPU_MEMORY_FRACTION", "0.8")),
            enable_audit_logging=os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true",
            human_review_threshold=float(os.getenv("HUMAN_REVIEW_THRESHOLD", "0.7"))
        )
    
    def get_absolute_database_path(self) -> Path:
        """Get absolute path to shared database file."""
        db_path = Path(self.database_path)
        if not db_path.is_absolute():
            # Make relative to project root directory
            project_root = Path(__file__).parent.parent.parent.parent
            db_path = project_root / db_path
        return db_path.resolve()
    
    def get_log_dir_path(self) -> Optional[Path]:
        """Get log directory path."""
        if not self.log_dir:
            return None
        
        log_path = Path(self.log_dir)
        if not log_path.is_absolute():
            # Make relative to this file's directory
            current_dir = Path(__file__).parent.parent.parent
            log_path = current_dir / log_path
        
        return log_path.resolve()