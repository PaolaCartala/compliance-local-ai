"""
Pydantic models for the Baker Compliant AI chat system.

This module defines all data models used throughout the chat API and inference services,
following strict type validation and SEC compliance requirements.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Generic, TypeVar
from uuid import UUID, uuid4
import json

from pydantic import BaseModel, Field, validator, ConfigDict

T = TypeVar('T')


class SpecializationType(str, Enum):
    """Custom GPT specialization types."""
    CRM = "crm"
    PORTFOLIO = "portfolio"
    COMPLIANCE = "compliance"
    GENERAL = "general"
    RETIREMENT = "retirement"
    TAX = "tax"


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class RequestStatus(str, Enum):
    """Inference request status types."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RequestType(str, Enum):
    """Inference request types."""
    CHAT = "chat"
    MEETING_TRANSCRIPTION = "meeting_transcription"
    DOCUMENT_ANALYSIS = "document_analysis"
    COMPLIANCE_CHECK = "compliance_check"


class MCPToolName(str, Enum):
    """Available MCP tool names."""
    REDTAIL_CRM = "redtail-crm"
    ALBRIDGE_PORTFOLIO = "albridge-portfolio"
    BLACK_DIAMOND = "black-diamond"


# Base Models
class BaseEntity(BaseModel):
    """Base entity with common fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Custom GPT Models
class MCPToolsConfig(BaseModel):
    """MCP tools configuration for Custom GPTs."""
    redtail_crm: bool = Field(default=False, description="Enable Redtail CRM integration")
    albridge_portfolio: bool = Field(default=False, description="Enable Albridge portfolio integration")
    black_diamond: bool = Field(default=False, description="Enable Black Diamond integration")


class CustomGPT(BaseEntity):
    """Custom GPT configuration model."""
    name: str = Field(..., min_length=1, max_length=100, description="Custom GPT name")
    description: str = Field(..., min_length=1, max_length=500, description="Custom GPT description")
    system_prompt: str = Field(..., min_length=10, description="System prompt for the Custom GPT")
    specialization: SpecializationType = Field(..., description="Area of specialization")
    color: str = Field(default="blue", description="UI color theme")
    icon: str = Field(default="Brain", description="UI icon name")
    mcp_tools_enabled: MCPToolsConfig = Field(default_factory=MCPToolsConfig)
    is_active: bool = Field(default=True, description="Whether the Custom GPT is active")
    user_id: str = Field(..., description="Owner user ID")

    @validator('mcp_tools_enabled', pre=True, always=True)
    def validate_mcp_tools(cls, v):
        """Ensure mcp_tools_enabled is a valid MCPToolsConfig."""
        if v is None:
            return MCPToolsConfig()
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON for mcp_tools_enabled")
        if isinstance(v, dict):
            return MCPToolsConfig(**v)
        return v
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        """Validate system prompt content."""
        if len(v.strip()) < 10:
            raise ValueError('System prompt must be at least 10 characters')
        return v.strip()


class CustomGPTCreate(BaseModel):
    """Schema for creating a new Custom GPT."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    system_prompt: str = Field(..., min_length=10)
    specialization: SpecializationType
    color: str = Field(default="blue")
    icon: str = Field(default="Brain")
    mcp_tools_enabled: MCPToolsConfig = Field(default_factory=MCPToolsConfig)


class CustomGPTUpdate(BaseModel):
    """Schema for updating a Custom GPT."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    system_prompt: Optional[str] = Field(None, min_length=10)
    specialization: Optional[SpecializationType] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    mcp_tools_enabled: Optional[MCPToolsConfig] = None
    is_active: Optional[bool] = None


# Thread Models
class Thread(BaseEntity):
    """Chat thread model."""
    title: str = Field(..., min_length=1, max_length=200, description="Thread title")
    custom_gpt_id: str = Field(..., description="Associated Custom GPT ID")
    user_id: str = Field(..., description="Owner user ID")
    last_message: Optional[str] = Field(None, max_length=500, description="Last message preview")
    message_count: int = Field(default=0, description="Number of messages in thread")
    is_archived: bool = Field(default=False, description="Whether thread is archived")
    tags: List[str] = Field(default_factory=list, description="Thread tags")

    @validator('tags', pre=True, always=True)
    def validate_tags(cls, v):
        """Ensure tags are loaded from a JSON string if needed."""
        if v is None:
            return []
        if isinstance(v, str):
            try:
                # Intenta decodificar la cadena JSON a una lista
                return json.loads(v)
            except json.JSONDecodeError:
                # Si no es un JSON válido, devuélvelo como una lista con un solo elemento
                return [v]
        return v


class ThreadCreate(BaseModel):
    """Schema for creating a new thread."""
    title: str = Field(..., min_length=1, max_length=200)
    custom_gpt_id: str = Field(..., description="Custom GPT to use for this thread")


class ThreadUpdate(BaseModel):
    """Schema for updating a thread."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    is_archived: Optional[bool] = None
    tags: Optional[List[str]] = None


# File Attachment Models
class FileAttachment(BaseModel):
    """File attachment model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Original filename")
    type: str = Field(..., description="MIME type")
    size: int = Field(..., gt=0, description="File size in bytes")
    url: str = Field(..., description="Storage URL or path")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


# MCP Tool Interaction Models
class MCPToolInteraction(BaseModel):
    """MCP tool interaction record."""
    tool_name: MCPToolName = Field(..., description="Name of the MCP tool used")
    action: str = Field(..., description="Action performed")
    data: Dict[str, Any] = Field(default_factory=dict, description="Tool interaction data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = Field(..., description="Whether the interaction was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# Message Models
class MessageBase(BaseModel):
    """Base model for messages."""
    thread_id: str = Field(..., description="Associated thread ID")
    content: str = Field(..., min_length=1, description="Message content")
    role: MessageRole = Field(..., description="Message role (user/assistant/system)")
    custom_gpt_id: Optional[str] = Field(None, description="Custom GPT that generated this message")
    
    # AI metadata
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence score")
    model_used: Optional[str] = Field(None, description="AI model used")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    # Compliance
    compliance_flags: List[str] = Field(default_factory=list, description="Compliance issues flagged")
    sec_compliant: bool = Field(default=True, description="SEC compliance status")
    human_review_required: bool = Field(default=False, description="Requires human review")


class Message(MessageBase):
    """Chat message model."""
    id: str
    user_id: str = Field(..., description="User who sent the message")
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_orm(cls, obj):
        """Create Message from ORM object with proper JSON deserialization."""
        data = {
            "id": obj.id,
            "thread_id": obj.thread_id,
            "user_id": obj.user_id,
            "content": obj.content,
            "role": obj.role,
            "custom_gpt_id": obj.custom_gpt_id,
            "confidence_score": obj.confidence_score,
            "model_used": obj.model_used,
            "processing_time_ms": obj.processing_time_ms,
            "compliance_flags": obj.compliance_flags_list,  # Use the property we created
            "sec_compliant": obj.sec_compliant,
            "human_review_required": obj.human_review_required,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    thread_id: str = Field(..., description="Thread to add message to")
    content: str = Field(..., min_length=1, description="Message content")
    role: MessageRole = Field(default=MessageRole.USER, description="Message role")
    custom_gpt_id: Optional[str] = Field(None, description="Custom GPT to use for processing")
    
    # AI metadata (optional)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence score")
    model_used: Optional[str] = Field(None, description="AI model used")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    # Compliance (optional)
    compliance_flags: List[str] = Field(default_factory=list, description="Compliance issues flagged")
    sec_compliant: bool = Field(default=True, description="SEC compliance status")
    human_review_required: bool = Field(default=False, description="Requires human review")


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    content: Optional[str] = Field(None, min_length=1, description="Message content")
    custom_gpt_id: Optional[str] = Field(None, description="Custom GPT that generated this message")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence score")
    model_used: Optional[str] = Field(None, description="AI model used")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    compliance_flags: Optional[List[str]] = Field(None, description="Compliance issues flagged")
    sec_compliant: Optional[bool] = Field(None, description="SEC compliance status")
    human_review_required: Optional[bool] = Field(None, description="Requires human review")
    
    class Config:
        from_attributes = True


# Inference Queue Models
class InferenceRequest(BaseEntity):
    """Inference request model for the queue system."""
    request_type: RequestType = Field(..., description="Type of inference request")
    input_data: Dict[str, Any] = Field(..., description="Request input data")
    status: RequestStatus = Field(default=RequestStatus.PENDING, description="Request status")
    priority: int = Field(default=5, ge=1, le=10, description="Request priority (1=highest, 10=lowest)")
    user_id: str = Field(..., description="User who made the request")
    client_id: Optional[str] = Field(None, description="Associated client ID")
    
    # Timing fields
    started_at: Optional[datetime] = Field(None, description="When processing started")
    completed_at: Optional[datetime] = Field(None, description="When processing completed")
    
    # Performance metrics
    queue_wait_time_ms: Optional[int] = Field(None, description="Time spent waiting in queue")
    processing_time_ms: Optional[int] = Field(None, description="Actual processing time")
    total_time_ms: Optional[int] = Field(None, description="Total time from creation to completion")
    
    # AI model metrics
    model_used: Optional[str] = Field(None, description="AI model used for processing")
    model_version: Optional[str] = Field(None, description="Model version")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Token usage
    input_tokens: Optional[int] = Field(None, description="Number of input tokens")
    output_tokens: Optional[int] = Field(None, description="Number of output tokens")
    total_tokens: Optional[int] = Field(None, description="Total tokens used")
    
    # Results and errors
    result_data: Optional[Dict[str, Any]] = Field(None, description="Processing result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Compliance
    sec_compliant: bool = Field(default=False, description="Whether result meets SEC requirements")
    human_review_required: bool = Field(default=False, description="Whether human review is needed")
    
    # System metrics
    server_id: Optional[str] = Field(None, description="Server that processed the request")
    memory_used_mb: Optional[int] = Field(None, description="Memory usage during processing")
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage during processing")


class ChatInferenceRequest(BaseModel):
    """Specific inference request for chat messages."""
    message_id: str = Field(..., description="Message ID to process")
    thread_id: str = Field(..., description="Thread context")
    custom_gpt_id: str = Field(..., description="Custom GPT to use")
    content: str = Field(..., description="User message content")
    attachments: List[FileAttachment] = Field(default_factory=list)
    context_messages: List[Dict[str, Any]] = Field(default_factory=list, description="Previous messages for context")


# API Response Models
class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T] = Field(..., description="Items in current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


# Health Check Models
class ServiceStatus(str, Enum):
    """Service status types."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    NOT_CONFIGURED = "not_configured"


class ServiceHealthDetail(BaseModel):
    """Detailed health information for a specific service."""
    status: ServiceStatus = Field(..., description="Service status")
    message: Optional[str] = Field(None, description="Status message or error details")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(None, description="Additional service-specific details")


class HealthCheck(BaseModel):
    """Comprehensive health check response model."""
    status: ServiceStatus = Field(..., description="Overall system status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Service version")
    
    # Core Services
    database: ServiceHealthDetail = Field(..., description="Database service health")
    ollama: ServiceHealthDetail = Field(..., description="Ollama AI service health")
    queue: ServiceHealthDetail = Field(..., description="Message queue service health")
    file_storage: ServiceHealthDetail = Field(..., description="File storage service health")
    
    # MCP Services
    mcp_services: Dict[str, ServiceHealthDetail] = Field(
        default_factory=dict,
        description="MCP service health details"
    )
    
    # System Metrics
    queue_depth: Optional[int] = Field(None, description="Current queue depth")
    active_connections: Optional[int] = Field(None, description="Active database connections")
    disk_usage_percent: Optional[float] = Field(None, description="Disk usage percentage")
    memory_usage_percent: Optional[float] = Field(None, description="Memory usage percentage")
    
    # Legacy fields for backwards compatibility
    database_status: Optional[str] = Field(None, description="Legacy database status")
    ollama_status: Optional[str] = Field(None, description="Legacy Ollama status")
    gpu_utilization: Optional[float] = Field(None, description="GPU utilization percentage")