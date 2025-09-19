"""
Configuration settings for the Baker Compliant AI system.

This module centralizes all configuration management using environment variables
and provides structured settings for different deployment environments.
"""

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Environment(str, Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging level types."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api_title: str = Field(default="Baker Compliant AI API", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=False, env="API_RELOAD")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./database/baker_compliant_ai.db", env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    encryption_enabled: bool = Field(default=False, env="ENCRYPTION_ENABLED")
    
    # Azure Configuration
    azure_tenant_id: str = Field(..., env="AZURE_TENANT_ID")
    azure_client_id: str = Field(..., env="AZURE_CLIENT_ID")
    azure_client_secret: str = Field(..., env="AZURE_CLIENT_SECRET")
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_chat_model: str = Field(default="gemma3:27b-it-qat", env="OLLAMA_CHAT_MODEL")
    ollama_vision_model: str = Field(default="gpt-oss-20b", env="OLLAMA_VISION_MODEL")
    ollama_timeout: int = Field(default=300, env="OLLAMA_TIMEOUT")
    
    # Queue Configuration
    queue_poll_interval: int = Field(default=5, env="QUEUE_POLL_INTERVAL")
    queue_batch_size: int = Field(default=10, env="QUEUE_BATCH_SIZE")
    queue_retry_attempts: int = Field(default=3, env="QUEUE_RETRY_ATTEMPTS")
    queue_retry_delay: int = Field(default=60, env="QUEUE_RETRY_DELAY")
    
    # File Storage
    file_storage_path: str = Field(default="./storage", env="FILE_STORAGE_PATH")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_file_types: str = Field(
        default="pdf,doc,docx,txt,png,jpg,jpeg,gif,mp3,wav,m4a",
        env="ALLOWED_FILE_TYPES"
    )
    
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    log_file_path: str = Field(default="./logs/baker_ai.log", env="LOG_FILE_PATH")
    log_rotation_size: str = Field(default="10 MB", env="LOG_ROTATION_SIZE")
    log_retention_days: int = Field(default=30, env="LOG_RETENTION_DAYS")
    
    # Compliance
    audit_log_retention_days: int = Field(default=2555, env="AUDIT_LOG_RETENTION_DAYS")  # 7 years
    meeting_notes_retention_days: int = Field(default=2190, env="MEETING_NOTES_RETENTION_DAYS")  # 6 years
    compliance_confidence_threshold: float = Field(default=0.8, env="COMPLIANCE_CONFIDENCE_THRESHOLD")
    human_review_threshold: float = Field(default=0.7, env="HUMAN_REVIEW_THRESHOLD")
    
    # Performance
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    inference_timeout: int = Field(default=300, env="INFERENCE_TIMEOUT")
    
    # Development
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")
    cors_origins: str = Field(default="http://localhost:8080,http://192.168.3.5:8080", env="CORS_ORIGINS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_file_types_list(self) -> list[str]:
        """Get allowed file types as a list."""
        return [file_type.strip() for file_type in self.allowed_file_types.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def get_database_path(self) -> Path:
        """Get the shared database file path."""
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            # Convert relative path to absolute path from project root
            if not Path(db_path).is_absolute():
                project_root = Path(__file__).parent.parent.parent.parent
                db_path = project_root / db_path
            return Path(db_path).resolve()
        raise ValueError("Only SQLite databases are supported")
    
    def get_log_file_path(self) -> Path:
        """Get the log file path and ensure directory exists."""
        log_path = Path(self.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path
    
    def get_file_storage_path(self) -> Path:
        """Get the file storage path and ensure directory exists."""
        storage_path = Path(self.file_storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        return storage_path


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Constants
class APITags:
    """API endpoint tags for documentation."""
    HEALTH = "Health"
    CHAT = "Chat"
    THREADS = "Threads"
    CUSTOM_GPTS = "Custom GPTs"
    MESSAGES = "Messages"
    FILES = "Files"
    INFERENCE = "Inference"
    AUDIT = "Audit"


class Permissions:
    """User permission constants."""
    CHAT_READ = "chat:read"
    CHAT_WRITE = "chat:write"
    CUSTOM_GPT_READ = "custom_gpt:read"
    CUSTOM_GPT_WRITE = "custom_gpt:write"
    AUDIT_READ = "audit:read"
    ADMIN = "admin"


class UserRoles:
    """User role constants with associated permissions."""
    FINANCIAL_ADVISOR = {
        "name": "Financial Advisor",
        "permissions": [
            Permissions.CHAT_READ,
            Permissions.CHAT_WRITE,
            Permissions.CUSTOM_GPT_READ,
            Permissions.CUSTOM_GPT_WRITE,
        ]
    }
    
    COMPLIANCE_OFFICER = {
        "name": "Compliance Officer",
        "permissions": [
            Permissions.CHAT_READ,
            Permissions.CHAT_WRITE,
            Permissions.CUSTOM_GPT_READ,
            Permissions.CUSTOM_GPT_WRITE,
            Permissions.AUDIT_READ,
        ]
    }
    
    ADMINISTRATOR = {
        "name": "Administrator",
        "permissions": [
            Permissions.CHAT_READ,
            Permissions.CHAT_WRITE,
            Permissions.CUSTOM_GPT_READ,
            Permissions.CUSTOM_GPT_WRITE,
            Permissions.AUDIT_READ,
            Permissions.ADMIN,
        ]
    }


# Model configurations for different specializations
SPECIALIZATION_CONFIGS = {
    "crm": {
        "model": "gemma3:27b-it-qat",
        "temperature": 0.1,
        "max_tokens": 2048,
        "system_prompt_prefix": "You are a specialized CRM assistant for financial advisors. "
    },
    "portfolio": {
        "model": "gemma3:27b-it-qat",
        "temperature": 0.2,
        "max_tokens": 3072,
        "system_prompt_prefix": "You are a specialized portfolio analysis assistant for wealth management. "
    },
    "compliance": {
        "model": "gemma3:27b-it-qat",
        "temperature": 0.05,  # Very low for compliance
        "max_tokens": 2048,
        "system_prompt_prefix": "You are a specialized compliance assistant for financial advisory firms. "
    },
    "general": {
        "model": "gemma3:27b-it-qat",
        "temperature": 0.3,
        "max_tokens": 2048,
        "system_prompt_prefix": "You are a helpful AI assistant for financial services. "
    },
    "retirement": {
        "model": "gemma3:27b-it-qat",
        "temperature": 0.2,
        "max_tokens": 2048,
        "system_prompt_prefix": "You are a specialized retirement planning assistant. "
    },
    "tax": {
        "model": "gemma3:27b-it-qat",
        "temperature": 0.1,
        "max_tokens": 2048,
        "system_prompt_prefix": "You are a specialized tax planning assistant for financial advisors. "
    }
}