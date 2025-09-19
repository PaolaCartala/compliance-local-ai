"""
Chat service for managing chat operations.

Handles business logic for chat threads, messages, and Custom GPT management.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, func, delete, update


from api.src.models.schemas import (
    MessageCreate, Message, Thread, ThreadCreate, CustomGPT, MessageUpdate, ThreadUpdate
)
from api.src.models import orm, schemas
from api.src.utils.logging import logger


class ChatService:
    """Service for managing chat operations."""

    def __init__(self):
        self.logger = logger

    async def create_thread(
        self,
        db: AsyncSession,
        thread_data: ThreadCreate,
        user_id: str
    ) -> orm.Thread:
        """Create a new chat thread."""
        try:
            db_thread = orm.Thread(
                title=thread_data.title,
                custom_gpt_id=thread_data.custom_gpt_id,
                user_id=user_id
            )
            db.add(db_thread)
            await db.commit()
            await db.refresh(db_thread)

            self.logger.info(
                "Thread created successfully",
                thread_id=db_thread.id,
                user_id=user_id,
                custom_gpt_id=thread_data.custom_gpt_id
            )
            return db_thread

        except Exception as e:
            await db.rollback()
            self.logger.error(
                "Failed to create thread",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            raise

    async def get_user_threads(
        self,
        db: AsyncSession,
        user_id: str,
        offset: int = 0,
        limit: int = 20
    ) -> tuple[List[orm.Thread], int]:
        """Get threads for a user with pagination."""
        try:
            query = select(orm.Thread).where(orm.Thread.user_id == user_id).order_by(orm.Thread.updated_at.desc())
            
            count_query = select(func.count()).select_from(orm.Thread).where(orm.Thread.user_id == user_id)
            total = (await db.execute(count_query)).scalar_one()

            result = await db.execute(query.offset(offset).limit(limit))
            threads = result.scalars().all()
            
            return threads, total
            
        except Exception as e:
            self.logger.error(
                "Failed to get user threads",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            raise

    async def get_thread_by_id(self, db: AsyncSession, thread_id: str) -> Optional[orm.Thread]:
        """Get a thread by its ID."""
        try:
            result = await db.execute(
                select(orm.Thread).where(orm.Thread.id == thread_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(
                "Failed to get thread by ID",
                error=str(e),
                thread_id=thread_id,
                exc_info=True
            )
            raise

    async def create_message(
        self,
        db: AsyncSession,
        thread_id: str,
        content: str,
        role: str,
        user_id: str,
        custom_gpt_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
        model_used: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        compliance_flags: Optional[List[str]] = None,
        sec_compliant: bool = True,
        human_review_required: bool = False
    ) -> orm.Message:
        """Create a new message in a thread."""
        try:
            db_message = orm.Message(
                thread_id=thread_id,
                user_id=user_id,
                content=content,
                role=role,
                custom_gpt_id=custom_gpt_id,
                confidence_score=confidence_score,
                model_used=model_used,
                processing_time_ms=processing_time_ms,
                compliance_flags=json.dumps(compliance_flags or []),
                sec_compliant=sec_compliant,
                human_review_required=human_review_required
            )
            db.add(db_message)
            await db.commit()
            await db.refresh(db_message)

            self.logger.info(
                "Message created successfully",
                message_id=db_message.id,
                thread_id=thread_id,
                user_id=user_id,
                role=role
            )
            return db_message

        except Exception as e:
            await db.rollback()
            self.logger.error(
                "Failed to create message",
                error=str(e),
                thread_id=thread_id,
                user_id=user_id,
                exc_info=True
            )
            raise

    async def get_thread_messages(
        self,
        db: AsyncSession,
        thread_id: str,
        offset: int = 0,
        limit: int = 50
    ) -> tuple[List[orm.Message], int]:
        """Get messages from a thread with pagination."""
        try:
            query = select(orm.Message).where(orm.Message.thread_id == thread_id).order_by(orm.Message.created_at.desc())
            
            count_query = select(func.count()).select_from(orm.Message).where(orm.Message.thread_id == thread_id)
            total = (await db.execute(count_query)).scalar_one()

            result = await db.execute(query.offset(offset).limit(limit))
            messages = result.scalars().all()
            
            return messages, total
            
        except Exception as e:
            self.logger.error(
                "Failed to get thread messages",
                error=str(e),
                thread_id=thread_id,
                exc_info=True
            )
            raise

    async def get_thread_context(
        self,
        db: AsyncSession,
        thread_id: str,
        limit: int = 10
    ) -> List[orm.Message]:
        """Get the last N messages from a thread for context."""
        try:
            result = await db.execute(
                select(orm.Message)
                .where(orm.Message.thread_id == thread_id)
                .order_by(orm.Message.created_at.desc())
                .limit(limit)
            )
            messages = result.scalars().all()
            return list(reversed(messages))  # Return in chronological order
        except Exception as e:
            self.logger.error(
                "Failed to get thread context",
                error=str(e),
                thread_id=thread_id,
                exc_info=True
            )
            raise

    async def get_message_by_id(self, db: AsyncSession, message_id: str, user_id: str) -> Optional[orm.Message]:
        """Get a message by its ID, ensuring the user owns the parent thread."""
        try:
            # Join with Thread to verify user ownership
            result = await db.execute(
                select(orm.Message)
                .join(orm.Thread, orm.Message.thread_id == orm.Thread.id)
                .where(
                    orm.Message.id == message_id,
                    orm.Thread.user_id == user_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(
                "Failed to get message by ID",
                error=str(e),
                message_id=message_id,
                user_id=user_id,
                exc_info=True
            )
            raise

    # async def update_thread(
    #     self, 
    #     db: AsyncSession, 
    #     thread_id: str, 
    #     thread_data: ThreadUpdate,
    #     user_id: str
    # ) -> Optional[orm.Thread]:
    #     """Update an existing thread."""
    #     try:
    #         # First, get the thread and verify ownership
    #         thread = await self.get_thread_by_id(db, thread_id)
    #         if not thread:
    #             return None
            
    #         # Verify user owns this thread
    #         if thread.user_id != user_id:
    #             self.logger.warning(
    #                 "User attempted to update thread they don't own",
    #                 user_id=user_id,
    #                 thread_id=thread_id,
    #                 thread_owner=thread.user_id
    #             )
    #             return None
            
    #         # Prepare update data - only include fields that are not None
    #         update_data = {}
    #         if thread_data.title is not None:
    #             update_data["title"] = thread_data.title
    #         if thread_data.is_archived is not None:
    #             update_data["is_archived"] = thread_data.is_archived
    #         if thread_data.tags is not None:
    #             update_data["tags"] = thread_data.tags
            
    #         if not update_data:
    #             # No updates to perform
    #             return thread
            
    #         # Update the thread
    #         update_data["updated_at"] = datetime.utcnow()
            
    #         stmt = (
    #             update(orm.Thread)
    #             .where(orm.Thread.id == thread_id)
    #             .values(**update_data)
    #             .returning(orm.Thread)
    #         )
            
    #         result = await db.execute(stmt)
    #         await db.commit()
            
    #         updated_thread = result.scalar_one_or_none()
            
    #         if updated_thread:
    #             self.logger.info(
    #                 "Thread updated successfully",
    #                 thread_id=thread_id,
    #                 user_id=user_id,
    #                 updated_fields=list(update_data.keys())
    #             )
            
    #         return updated_thread
            
    #     except Exception as e:
    #         await db.rollback()
    #         self.logger.error(
    #             "Failed to update thread",
    #             error=str(e),
    #             thread_id=thread_id,
    #             user_id=user_id,
    #             exc_info=True
    #         )
    #         raise
    async def update_thread(
        self, db: AsyncSession, thread_id: str, thread_data: schemas.ThreadUpdate, user_id: str
    ) -> orm.Thread | None:
        """Updates a thread's details safely."""
        try:
            db_thread = await self.get_thread_by_id(db, thread_id)

            if not db_thread:
                self.logger.warning("Update failed: Thread not found", thread_id=thread_id, user_id=user_id)
                return None
            
            # Verify user owns this thread
            if db_thread.user_id != user_id:
                self.logger.warning("Update failed: Access denied", thread_id=thread_id, user_id=user_id, thread_owner=db_thread.user_id)
                return None

            update_data = thread_data.model_dump(exclude_unset=True)
            if not update_data:
                return db_thread
                
            for key, value in update_data.items():
                # Special handling for tags field - convert list to JSON string
                if key == 'tags' and isinstance(value, list):
                    setattr(db_thread, key, json.dumps(value))
                else:
                    setattr(db_thread, key, value)
            
            await db.commit()
            await db.refresh(db_thread)
            
            self.logger.info("Thread updated successfully", thread_id=thread_id)
            return db_thread
        except Exception as e:
            await db.rollback()
            self.logger.error("Failed to update thread", error=str(e), thread_id=thread_id, exc_info=True)
            raise

    async def update_message(
        self, 
        db: AsyncSession, 
        message_id: str, 
        message_data: MessageUpdate,
        user_id: str
    ) -> Optional[orm.Message]:
        """Update an existing message."""
        try:
            # First, get the message and verify user ownership through thread
            message = await self.get_message_by_id(db, message_id, user_id)
            if not message:
                return None
            
            # Prepare update data - only include fields that are not None
            update_data = {}
            if message_data.content is not None:
                update_data["content"] = message_data.content
            
            if not update_data:
                # No updates to perform
                return message
            
            # Update the message
            update_data["updated_at"] = datetime.utcnow()
            
            for key, value in update_data.items():
                setattr(message, key, value)
            
            await db.commit()
            await db.refresh(message)
            
            self.logger.info(
                "Message updated successfully",
                message_id=message_id,
                user_id=user_id,
                updated_fields=list(update_data.keys())
            )
            
            return message
            
        except Exception as e:
            await db.rollback()
            self.logger.error(
                "Failed to update message",
                error=str(e),
                message_id=message_id,
                user_id=user_id,
                exc_info=True
            )
            raise

    async def delete_message(
        self, 
        db: AsyncSession, 
        message_id: str, 
        user_id: str
    ) -> bool:
        """Delete a message."""
        try:
            # First, verify the message exists and user owns it through thread
            message = await self.get_message_by_id(db, message_id, user_id)
            if not message:
                return False
            
            # Delete the message
            await db.delete(message)
            await db.commit()
            
            self.logger.info(
                "Message deleted successfully",
                message_id=message_id,
                user_id=user_id
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            self.logger.error(
                "Failed to delete message",
                error=str(e),
                message_id=message_id,
                user_id=user_id,
                exc_info=True
            )
            raise

    async def delete_thread(
        self, 
        db: AsyncSession, 
        thread_id: str, 
        user_id: str
    ) -> bool:
        """Delete a thread and all its messages."""
        try:
            # First, verify the thread exists and user owns it
            thread = await self.get_thread_by_id(db, thread_id)
            if not thread or thread.user_id != user_id:
                return False
            
            # Delete all messages in the thread first (due to foreign key constraints)
            await db.execute(
                delete(orm.Message).where(orm.Message.thread_id == thread_id)
            )
            
            # Delete the thread
            await db.delete(thread)
            await db.commit()
            
            self.logger.info(
                "Thread deleted successfully",
                thread_id=thread_id,
                user_id=user_id
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            self.logger.error(
                "Failed to delete thread",
                error=str(e),
                thread_id=thread_id,
                user_id=user_id,
                exc_info=True
            )
            raise
