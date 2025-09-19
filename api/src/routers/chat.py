"""
Chat router for handling chat message operations.

Manages chat message creation, retrieval, and processing through
the inference queue system.
"""

from typing import List, Optional
from uuid import uuid4
import math

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models.schemas import (
    Message, MessageCreate, APIResponse, PaginatedResponse,
    InferenceRequest, RequestType, ChatInferenceRequest, MessageUpdate
)
from api.src.services.database import get_database_session
from api.src.services.chat_service import ChatService
from api.src.services.file_service import FileService
from api.src.services.queue_service import QueueService
from api.src.utils.logging import logger, audit_logger
from api.src.utils.auth import get_current_user, get_database_user_id

router = APIRouter()
chat_service = ChatService()
file_service = FileService()
queue_service = QueueService()


@router.post(
    "/messages",
    response_model=APIResponse[Message],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send a message and enqueue for AI processing"
)
async def send_message(
    content: str = Form(...),
    thread_id: str = Form(...),
    custom_gpt_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Send a new chat message and enqueue for AI processing.
    
    This endpoint:
    1. Validates the message and thread.
    2. Processes any file attachments.
    3. Creates the user message in the database.
    4. Enqueues an inference request for the AI to generate a response.
    5. Returns the created user message.
    """
    try:
        logger.debug("Starting message send process", current_user=current_user)
        
        # Map auth user to database user ID
        db_user_id = await get_database_user_id(current_user)
        logger.debug("User mapping result", db_user_id=db_user_id)
        
        if not db_user_id:
            logger.error("User mapping failed", current_user=current_user)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found in database"
            )
        
        logger.debug("Getting thread", thread_id=thread_id)
        thread = await chat_service.get_thread_by_id(db, thread_id)
        logger.debug("Thread retrieved", thread_exists=thread is not None, thread_user_id=thread.user_id if thread else None)
        
        if not thread or thread.user_id != db_user_id:
            logger.error("Thread access denied", thread_exists=thread is not None, thread_user_id=thread.user_id if thread else None, db_user_id=db_user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found or access denied"
            )
        
        attachments = []
        if files:
            for file in files:
                if file.filename:
                    attachment = await file_service.save_attachment(
                        file=file, user_id=str(db_user_id)
                    )
                    attachments.append(attachment)
        
        user_message = await chat_service.create_message(
            db=db,
            thread_id=thread_id,
            content=content,
            role="user",
            user_id=str(db_user_id),
            compliance_flags=[f"attachment:{att.filename}" for att in attachments] if attachments else []
        )
        
        context_messages = await chat_service.get_thread_context(db, thread_id)
        
        # Convert ORM messages to dict format for inference payload
        context_messages_dict = []
        for msg in context_messages:
            context_messages_dict.append({
                "id": msg.id,
                "thread_id": msg.thread_id,
                "content": msg.content,
                "role": msg.role,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None,
                "attachments": [],  # Will be loaded separately if needed
                "compliance_flags": msg.compliance_flags_list  # Use the property that deserializes JSON
            })
        
        inference_payload = ChatInferenceRequest(
            message_id=user_message.id,
            thread_id=thread_id,
            custom_gpt_id=custom_gpt_id or thread.custom_gpt_id,
            content=content,
            attachments=attachments,
            context_messages=context_messages_dict
        )
        
        try:
            await queue_service.enqueue_chat_request(
                db=db,
                message_id=str(user_message.id),
                thread_id=thread_id,
                custom_gpt_id=custom_gpt_id or thread.custom_gpt_id,
                user_message=content,
                context_messages=context_messages_dict,
                attachments=attachments,
                user_id=str(db_user_id)
            )
            
            audit_logger.log_user_action(
                user_id=str(db_user_id),
                action="send_message",
                resource="message",
                details={
                    "thread_id": thread_id,
                    "message_id": user_message.id,
                    "enqueued_for_inference": True
                }
            )
            
        except Exception as queue_error:
            logger.error("Failed to enqueue message for inference", 
                        error=str(queue_error), 
                        message_id=user_message.id,
                        exc_info=True)
            # Continue execution - message is saved but not queued
        
        return APIResponse(
            success=True,
            data=Message.from_orm(user_message),
            message="Message sent and queued for AI processing"
        )
        
    except Exception as e:
        logger.error("Failed to send message", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.post(
    "/messages/create",
    response_model=APIResponse[Message],
    status_code=status.HTTP_201_CREATED,
    summary="Create a message (JSON CRUD endpoint)"
)
async def create_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new message via JSON payload.
    This is a pure CRUD endpoint without AI processing queue.
    """
    try:
        # Validate thread access
        thread = await chat_service.get_thread_by_id(db, message_data.thread_id)
        if not thread or thread.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found or access denied"
            )
        
        # Create message with all provided data
        db_message = await chat_service.create_message(
            db=db,
            thread_id=message_data.thread_id,
            content=message_data.content,
            role=message_data.role,
            user_id=current_user["id"],
            custom_gpt_id=message_data.custom_gpt_id,
            confidence_score=message_data.confidence_score,
            model_used=message_data.model_used,
            processing_time_ms=message_data.processing_time_ms,
            compliance_flags=message_data.compliance_flags,
            sec_compliant=message_data.sec_compliant,
            human_review_required=message_data.human_review_required
        )
        
        # Convert ORM to Pydantic model
        message = Message.from_orm(db_message)
        
        audit_logger.log_user_action(
            user_id=current_user["id"],
            action="create_message",
            resource="message",
            details={
                "thread_id": message_data.thread_id,
                "message_id": message.id,
                "role": message_data.role
            }
        )
        
        return APIResponse(
            success=True,
            data=message,
            message="Message created successfully"
        )
        
    except Exception as e:
        logger.error("Failed to create message", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message"
        )


@router.get(
    "/messages/{thread_id}",
    response_model=PaginatedResponse[Message],
    summary="Get messages for a thread"
)
async def get_thread_messages(
    thread_id: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all messages for a specific thread with pagination."""
    try:
        # Get database user ID from auth user
        db_user_id = await get_database_user_id(current_user)
        
        thread = await chat_service.get_thread_by_id(db, thread_id)
        if not thread or thread.user_id != db_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found or access denied"
            )
            
        messages, total = await chat_service.get_thread_messages(
            db, thread_id=thread_id, offset=offset, limit=limit
        )
        
        # Convert ORM objects to Pydantic models
        pydantic_messages = [Message.from_orm(msg) for msg in messages]
        
        page = (offset // limit) + 1
        pages = math.ceil(total / limit) if limit > 0 else 0
        
        return PaginatedResponse(
            items=pydantic_messages,
            total=total,
            page=page,
            size=limit,
            pages=pages
        )
        
    except Exception as e:
        logger.error(
            "Failed to get thread messages",
            error=str(e),
            thread_id=thread_id,
            auth_user_id=current_user["id"],
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@router.get(
    "/message/{message_id}",
    response_model=APIResponse[Message],
    summary="Get a single message"
)
async def get_message(
    message_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a single message by its ID."""
    try:
        db_message = await chat_service.get_message_by_id(
            db, message_id, current_user["id"]
        )
        if not db_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or access denied"
            )

        # Convert ORM to Pydantic model
        message = Message.from_orm(db_message)
        
        return APIResponse(
            success=True, 
            data=message,
            message="Message retrieved successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(
            "Failed to get message",
            error=str(e),
            message_id=message_id,
            user_id=current_user["id"],
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve message"
        )


@router.put(
    "/message/{message_id}",
    response_model=APIResponse[Message],
    summary="Update a message"
)
async def update_message(
    message_id: str,
    message_data: MessageUpdate,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Update a message's content or status."""
    try:
        message = await chat_service.get_message_by_id(db, message_id, current_user["id"])
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Verify user access - user can only update their own messages
        if message.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied - you can only update your own messages")

        db_updated_message = await chat_service.update_message(db, message_id, message_data, current_user["id"])
        if not db_updated_message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Convert ORM to Pydantic model
        updated_message = Message.from_orm(db_updated_message)

        audit_logger.log_user_action(
            user_id=current_user["id"],
            action="update_message",
            resource="message",
            details={"message_id": message_id}
        )

        return APIResponse(
            success=True,
            data=updated_message,
            message="Message updated successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(
            "Failed to update message",
            error=str(e),
            message_id=message_id,
            user_id=current_user["id"],
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update message"
        )


@router.delete(
    "/message/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a message"
)
async def delete_message(
    message_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Delete a message by its ID."""
    try:
        message = await chat_service.get_message_by_id(db, message_id, current_user["id"])
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Verify user access - user can only delete their own messages
        if message.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied - you can only delete your own messages")

        deleted = await chat_service.delete_message(db, message_id, current_user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Message not found")
        
        audit_logger.log_user_action(
            user_id=current_user["id"],
            action="delete_message",
            resource="message",
            details={"message_id": message_id}
        )
        
        return None
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(
            "Failed to delete message",
            error=str(e),
            message_id=message_id,
            user_id=current_user["id"],
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message"
        )
