"""
Service layer for handling Custom GPT business logic.
"""
import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from api.src.models.orm import CustomGpt as CustomGptOrm
from api.src.models.schemas import CustomGPTCreate, CustomGPTUpdate, CustomGPT, MCPToolsConfig
from api.src.utils.logging import logger
from api.src.models import orm
from api.src.models import schemas

class CustomGptService:
    """Service for all Custom GPT-related database operations."""

    @staticmethod
    async def create_gpt(db: AsyncSession, gpt_data: schemas.CustomGPTCreate, user_id: str) -> orm.CustomGpt:
        """Creates a new Custom GPT."""
        db_gpt = orm.CustomGpt(
            **gpt_data.model_dump(),
            user_id=user_id
        )
        db.add(db_gpt)
        await db.commit()
        await db.refresh(db_gpt)
        return db_gpt

    @staticmethod
    async def get_gpts_by_user(db: AsyncSession, user_id: str, offset: int, limit: int):
        """Gets all Custom GPTs for a user."""
        result = await db.execute(
            select(orm.CustomGpt)
            .where(orm.CustomGpt.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        gpts = result.scalars().all()
        
        total_result = await db.execute(
            select(orm.CustomGpt).where(orm.CustomGpt.user_id == user_id)
        )
        total = len(total_result.scalars().all())
        
        return gpts, total

    @staticmethod
    async def count_gpts_by_user(db: AsyncSession, user_id: str) -> int:
        """Count the total number of Custom GPTs for a user."""
        try:
            result = await db.execute(
                select(func.count(CustomGptOrm.id))
                .where(CustomGptOrm.user_id == user_id)
            )
            count = result.scalar_one()
            return count
        except Exception as e:
            logger.error("Error counting Custom GPTs", error=str(e), user_id=user_id, exc_info=True)
            raise

    @staticmethod
    async def get_gpt_by_id(db: AsyncSession, gpt_id: str, user_id: str) -> Optional[orm.CustomGpt]:
        """Get a Custom GPT by its ID, ensuring it belongs to the user."""
        try:
            result = await db.execute(
                select(orm.CustomGpt)
                .where(orm.CustomGpt.id == gpt_id)
                .where(orm.CustomGpt.user_id == user_id)
            )
            gpt = result.scalar_one_or_none()
            return gpt
        except Exception as e:
            logger.error(
                "Error retrieving Custom GPT",
                error=str(e),
                gpt_id=gpt_id,
                user_id=user_id,
                exc_info=True
            )
            raise

    @staticmethod
    async def update_gpt(db: AsyncSession, gpt_id: str, user_id: str, gpt_data: schemas.CustomGPTUpdate) -> Optional[orm.CustomGpt]:
        """Update a Custom GPT's information."""
        try:
            # First, get the existing GPT to ensure it belongs to the user
            result = await db.execute(
                select(orm.CustomGpt)
                .where(orm.CustomGpt.id == gpt_id)
                .where(orm.CustomGpt.user_id == user_id)
            )
            gpt = result.scalar_one_or_none()
            
            if not gpt:
                return None
            
            # Update only the provided fields
            update_data = gpt_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(gpt, field, value)
            
            # Update the updated_at timestamp
            from datetime import datetime
            gpt.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(gpt)
            return gpt
            
        except Exception as e:
            logger.error(
                "Error updating Custom GPT",
                error=str(e),
                gpt_id=gpt_id,
                user_id=user_id,
                exc_info=True
            )
            await db.rollback()
            raise

    @staticmethod
    async def delete_gpt(db: AsyncSession, gpt_id: str, user_id: str) -> bool:
        """Delete a Custom GPT."""
        try:
            # First, get the existing GPT to ensure it belongs to the user
            result = await db.execute(
                select(orm.CustomGpt)
                .where(orm.CustomGpt.id == gpt_id)
                .where(orm.CustomGpt.user_id == user_id)
            )
            gpt = result.scalar_one_or_none()
            
            if not gpt:
                return False
            
            await db.delete(gpt)
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(
                "Error deleting Custom GPT",
                error=str(e),
                gpt_id=gpt_id,
                user_id=user_id,
                exc_info=True
            )
            await db.rollback()
            raise

    @staticmethod
    async def get_all_gpts(db: AsyncSession, offset: int, limit: int):
        """Gets all active Custom GPTs (public access)."""
        try:
            result = await db.execute(
                select(orm.CustomGpt)
                .where(orm.CustomGpt.is_active == True)
                .offset(offset)
                .limit(limit)
            )
            gpts = result.scalars().all()
            
            total_result = await db.execute(
                select(func.count(orm.CustomGpt.id))
                .where(orm.CustomGpt.is_active == True)
            )
            total = total_result.scalar_one()
            
            return gpts, total
        except Exception as e:
            logger.error(
                "Error retrieving all Custom GPTs",
                error=str(e),
                exc_info=True
            )
            raise

    @staticmethod
    async def get_gpt_by_id_public(db: AsyncSession, gpt_id: str) -> Optional[orm.CustomGpt]:
        """Get a Custom GPT by its ID (public access)."""
        try:
            result = await db.execute(
                select(orm.CustomGpt)
                .where(orm.CustomGpt.id == gpt_id)
                .where(orm.CustomGpt.is_active == True)
            )
            gpt = result.scalar_one_or_none()
            return gpt
        except Exception as e:
            logger.error(
                "Error retrieving Custom GPT (public)",
                error=str(e),
                gpt_id=gpt_id,
                exc_info=True
            )
            raise

    @staticmethod
    async def update_gpt_public(db: AsyncSession, gpt_id: str, gpt_data: schemas.CustomGPTUpdate) -> Optional[orm.CustomGpt]:
        """Update a Custom GPT's information (public access)."""
        try:
            # Get the existing GPT (public access)
            result = await db.execute(
                select(orm.CustomGpt)
                .where(orm.CustomGpt.id == gpt_id)
                .where(orm.CustomGpt.is_active == True)
            )
            gpt = result.scalar_one_or_none()
            
            if not gpt:
                return None
            
            # Update only the provided fields
            update_data = gpt_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(gpt, field, value)
            
            # Update the updated_at timestamp
            from datetime import datetime
            gpt.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(gpt)
            return gpt
            
        except Exception as e:
            logger.error(
                "Error updating Custom GPT (public)",
                error=str(e),
                gpt_id=gpt_id,
                exc_info=True
            )
            await db.rollback()
            raise

    @staticmethod
    async def delete_gpt_public(db: AsyncSession, gpt_id: str) -> bool:
        """Delete a Custom GPT (public access)."""
        try:
            # Get the existing GPT (public access)
            result = await db.execute(
                select(orm.CustomGpt)
                .where(orm.CustomGpt.id == gpt_id)
                .where(orm.CustomGpt.is_active == True)
            )
            gpt = result.scalar_one_or_none()
            
            if not gpt:
                return False
            
            await db.delete(gpt)
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(
                "Error deleting Custom GPT (public)",
                error=str(e),
                gpt_id=gpt_id,
                exc_info=True
            )
            await db.rollback()
            raise
