"""
Custom GPT management router for Baker Compliant AI.

Handles Custom GPT creation, configuration, and management endpoints.
"""

import math
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models.schemas import (
    CustomGPT, CustomGPTCreate, CustomGPTUpdate, APIResponse, PaginatedResponse
)
from api.src.services.database import get_database_session
from api.src.services.custom_gpt import CustomGptService
from api.src.utils.logging import logger
from api.src.utils.auth import get_current_user

router = APIRouter()


# @router.get(
#     "/",
#     response_model=PaginatedResponse[CustomGPT],
#     summary="Get user's Custom GPTs"
# )
# async def get_custom_gpts(
#     limit: int = 20,
#     offset: int = 0,
#     db: AsyncSession = Depends(get_database_session),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get all Custom GPTs for the current user."""
#     try:
#         gpts, total = await CustomGptService.get_gpts_by_user(
#             db, user_id=current_user["id"], offset=offset, limit=limit
#         )
#         return PaginatedResponse(
#             success=True,
#             data=gpts,
#             total=total,
#             limit=limit,
#             offset=offset,
#             message="Custom GPTs retrieved successfully"
#         )
#     except Exception as e:
#         logger.error(
#             "Failed to get Custom GPTs",
#             error=str(e),
#             user_id=current_user["id"],
#             exc_info=True
#         )
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve Custom GPTs"
#         )
@router.get(
    "/",
    response_model=PaginatedResponse[CustomGPT],
    summary="Get all Custom GPTs (public access)"
)
async def get_custom_gpts(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all active Custom GPTs. Public access - no authentication required."""
    try:
        gpts, total = await CustomGptService.get_all_gpts(
            db, offset=offset, limit=limit
        )
        
        page = (offset // limit) + 1
        pages = math.ceil(total / limit) if limit > 0 else 0
        
        return PaginatedResponse(
            items=gpts,
            total=total,
            page=page,
            size=limit,
            pages=pages
        )

    except Exception as e:
        logger.error(
            "Failed to get Custom GPTs",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Custom GPTs"
        )


@router.post(
    "/",
    response_model=APIResponse[CustomGPT],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Custom GPT (public access)"
)
async def create_custom_gpt(
    gpt_data: CustomGPTCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new Custom GPT configuration. Public access - no authentication required."""
    try:
        # For public creation, we'll use a default user_id (could be configurable)
        default_user_id = "1"  # This should be configurable or handled differently
        new_gpt = await CustomGptService.create_gpt(
            db, gpt_data=gpt_data, user_id=default_user_id
        )
        return APIResponse(
            success=True,
            data=new_gpt,
            message="Custom GPT created successfully"
        )
    except Exception as e:
        logger.error(
            "Failed to create Custom GPT",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Custom GPT"
        )


@router.get(
    "/{gpt_id}",
    response_model=APIResponse[CustomGPT],
    summary="Get a specific Custom GPT (public access)"
)
async def get_custom_gpt(
    gpt_id: str,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a specific Custom GPT by ID. Public access - no authentication required."""
    try:
        # Get the Custom GPT by ID (public access)
        gpt = await CustomGptService.get_gpt_by_id_public(db, gpt_id)
        
        if not gpt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom GPT not found or access denied"
            )
        
        # Convert ORM to Pydantic model
        gpt_response = CustomGPT.from_orm(gpt)
        
        return APIResponse(
            success=True,
            data=gpt_response,
            message="Custom GPT retrieved successfully"
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(
            "Failed to get Custom GPT",
            error=str(e),
            gpt_id=gpt_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Custom GPT"
        )


@router.put(
    "/{gpt_id}",
    response_model=APIResponse[CustomGPT],
    summary="Update a specific Custom GPT (public access)"
)
async def update_custom_gpt(
    gpt_id: str,
    gpt_data: CustomGPTUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a specific Custom GPT by ID. Public access - no authentication required."""
    try:
        # Update the Custom GPT (public access)
        updated_gpt = await CustomGptService.update_gpt_public(db, gpt_id, gpt_data)
        
        if not updated_gpt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom GPT not found or access denied"
            )
        
        # Convert ORM to Pydantic model
        gpt_response = CustomGPT.from_orm(updated_gpt)
        
        return APIResponse(
            success=True,
            data=gpt_response,
            message="Custom GPT updated successfully"
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(
            "Failed to update Custom GPT",
            error=str(e),
            gpt_id=gpt_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update Custom GPT"
        )


@router.delete(
    "/{gpt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific Custom GPT (public access)"
)
async def delete_custom_gpt(
    gpt_id: str,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a specific Custom GPT by ID. Public access - no authentication required."""
    try:
        # Delete the Custom GPT (public access)
        deleted = await CustomGptService.delete_gpt_public(db, gpt_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom GPT not found or access denied"
            )
        
        # 204 No Content - successful deletion
        return
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(
            "Failed to delete Custom GPT",
            error=str(e),
            gpt_id=gpt_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete Custom GPT"
        )
