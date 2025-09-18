"""
Thread management router for Baker Compliant AI.

Handles thread creation, listing, and management endpoints.
"""

from typing import List
import math

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models.schemas import (
    Thread, ThreadCreate, ThreadUpdate, APIResponse, PaginatedResponse
)
from api.src.services.database import get_database_session
from api.src.services.chat_service import ChatService
from api.src.utils.logging import logger
from api.src.utils.auth import get_current_user, get_database_user_id

router = APIRouter()
chat_service = ChatService()


@router.post(
    "/",
    response_model=APIResponse[Thread],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat thread"
)
async def create_thread(
    thread_data: ThreadCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a new chat thread."""
    try:
        # Map auth user to database user ID
        db_user_id = await get_database_user_id(current_user)
        if not db_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found in database"
            )
            
        thread = await chat_service.create_thread(
            db=db,
            thread_data=thread_data,
            user_id=str(db_user_id)
        )
        
        return APIResponse(
            success=True,
            data=thread,
            message="Thread created successfully"
        )
        
    except Exception as e:
        logger.error(
            "Failed to create thread",
            error=str(e),
            user_id=str(db_user_id) if 'db_user_id' in locals() else current_user.get("id", "unknown"),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create thread"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[Thread],
    summary="Get user's chat threads"
)
async def get_user_threads(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all threads for the current user."""
    try:
        threads, total = await chat_service.get_user_threads(
            db, user_id=current_user["id"], offset=offset, limit=limit
        )
        
        page = (offset // limit) + 1
        pages = math.ceil(total / limit) if limit > 0 else 0
        
        return PaginatedResponse(
            items=threads,
            total=total,
            page=page,
            size=limit,
            pages=pages
        )
        
    except Exception as e:
        logger.error(
            "Failed to get user threads",
            error=str(e),
            user_id=current_user["id"],
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve threads"
        )


@router.get(
    "/{thread_id}",
    response_model=APIResponse[Thread],
    summary="Get a specific thread"
)
async def get_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific thread by ID."""
    try:
        thread = await chat_service.get_thread_by_id(db, thread_id)
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread with ID {thread_id} not found"
            )
        
        # Verify user owns this thread
        if thread.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't own this thread"
            )
        
        return APIResponse(
            success=True,
            data=thread,
            message="Thread retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get thread",
            error=str(e),
            thread_id=thread_id,
            user_id=current_user["id"],
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve thread"
        )


@router.put(
    "/{thread_id}",
    response_model=APIResponse[Thread],
    summary="Update a specific thread"
)
async def update_thread(
    thread_id: str,
    thread_data: ThreadUpdate,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_current_user)
):
    """Update a specific thread by ID."""
    try:
        updated_thread = await chat_service.update_thread(
            db=db,
            thread_id=thread_id,
            thread_data=thread_data,
            user_id=current_user["id"]
        )
        
        if not updated_thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread with ID {thread_id} not found or access denied"
            )
        
        return APIResponse(
            success=True,
            data=updated_thread,
            message="Thread updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update thread",
            error=str(e),
            thread_id=thread_id,
            user_id=current_user["id"],
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update thread"
        )
