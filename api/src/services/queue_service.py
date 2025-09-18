"""
Queue service for managing inference requests.

Handles adding requests to the inference queue and managing request lifecycle.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from api.src.models.schemas import InferenceRequest, RequestType
from api.src.utils.logging import logger


class QueueService:
    """Service for managing the inference request queue."""
    
    def __init__(self):
        self.logger = logger
    
    async def enqueue_chat_request(
        self,
        db: AsyncSession,
        message_id: str,
        custom_gpt_id: str,
        user_message: str,
        context_messages: list,
        attachments: Optional[list] = None,
        priority: int = 5,
        user_id: str = "1"
    ) -> str:
        """
        Add a chat inference request to the queue.
        
        Args:
            db: Database session
            message_id: ID of the message to process
            custom_gpt_id: ID of the Custom GPT configuration
            user_message: User's message content
            context_messages: Previous conversation context
            attachments: File attachments if any
            priority: Request priority (1=highest, 10=lowest)
            
        Returns:
            Request ID
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Create input_data JSON payload
            input_data = {
                "message_id": message_id,
                "custom_gpt_id": custom_gpt_id,
                "user_message": user_message,
                "context_messages": context_messages,
                "attachments": attachments or []
            }
            
            self.logger.debug(
                "Attempting to enqueue chat request",
                request_id=request_id,
                message_id=message_id,
                custom_gpt_id=custom_gpt_id,
                user_id=user_id
            )
            
            # Insert into queue using the correct schema
            await db.execute(
                text("""
                INSERT INTO inference_queue (
                    id, request_type, input_data, status, priority, user_id, created_at, message_id
                ) VALUES (
                    :id, :request_type, :input_data, :status, :priority, :user_id, :created_at, :message_id
                )
                """),
                {
                    "id": request_id,
                    "request_type": "chat",
                    "input_data": json.dumps(input_data),
                    "status": "pending",
                    "priority": max(1, min(10, priority)),  # Clamp between 1-10
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "message_id": message_id
                }
            )
            
            self.logger.debug(
                "Database insert executed, attempting commit",
                request_id=request_id
            )
            
            await db.commit()
            
            self.logger.info(
                "Chat request enqueued successfully",
                request_id=request_id,
                message_id=message_id,
                custom_gpt_id=custom_gpt_id,
                priority=priority
            )
            
            return request_id
            
        except Exception as e:
            await db.rollback()
            self.logger.error(
                "Failed to enqueue chat request",
                error=str(e),
                message_id=message_id,
                exc_info=True
            )
            raise
    
    async def get_request_status(
        self,
        db: AsyncSession,
        request_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the status of a request."""
        try:
            result = await db.execute(
                text("""
                SELECT request_id, status, priority, created_at,
                       processing_started_at, completed_at, retry_count,
                       error_message, response_content, response_metadata
                FROM inference_queue 
                WHERE request_id = :request_id
                """),
                {"request_id": request_id}
            )
            
            row = result.fetchone()
            if not row:
                return None
            
            status_data = {
                "request_id": row.request_id,
                "status": row.status,
                "priority": row.priority,
                "created_at": row.created_at,
                "processing_started_at": row.processing_started_at,
                "completed_at": row.completed_at,
                "retry_count": row.retry_count,
                "error_message": row.error_message,
                "response_content": row.response_content,
                "response_metadata": row.response_metadata
            }
            
            # Parse JSON metadata if available
            if status_data["response_metadata"]:
                try:
                    status_data["response_metadata"] = json.loads(
                        status_data["response_metadata"]
                    )
                except json.JSONDecodeError:
                    status_data["response_metadata"] = {}
            
            return status_data
            
        except Exception as e:
            self.logger.error(
                "Failed to get request status",
                error=str(e),
                request_id=request_id,
                exc_info=True
            )
            raise
    
    async def get_queue_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get current queue statistics."""
        try:
            result = await db.execute(
                text("""
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued,
                    SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM inference_queue 
                WHERE created_at > datetime('now', '-24 hours')
                """)
            )
            
            row = result.fetchone()
            
            return {
                "total_requests_24h": row.total_requests or 0,
                "queued": row.queued or 0,
                "processing": row.processing or 0,
                "completed_24h": row.completed or 0,
                "failed_24h": row.failed or 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(
                "Failed to get queue stats",
                error=str(e),
                exc_info=True
            )
            return {
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }