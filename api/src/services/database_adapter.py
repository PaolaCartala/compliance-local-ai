"""
Database adapter for the API service.

This adapter provides API-specific database operations while connecting
to the shared Baker Compliant AI database. It follows the principle of
separation of concerns by exposing only the operations needed by the API.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional, List, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from api.src.utils.config import get_settings
from api.src.utils.logging import logger


# Base class for all database models
Base = declarative_base()


def get_shared_database_path() -> str:
    """Get the path to the shared database."""
    # Database is in the project root database/ directory
    project_root = Path(__file__).parent.parent.parent.parent  # api/src/services/ -> project root
    db_path = project_root / "database" / "baker_compliant_ai.db"
    return str(db_path.absolute())


class DatabaseAdapter:
    """
    Database adapter for the API service.
    
    Connects to the shared Baker Compliant AI database and provides
    API-specific operations while maintaining separation of concerns.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.async_session_maker = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the database connection and create tables."""
        if self._initialized:
            return
        
        # Use shared database path
        shared_db_path = get_shared_database_path()
        async_database_url = f"sqlite+aiosqlite:///{shared_db_path}"
        
        logger.info(
            "Initializing API database adapter", 
            database_path=shared_db_path,
            url=async_database_url
        )
        
        # Create async engine
        self.engine = create_async_engine(
            async_database_url,
            echo=self.settings.debug,
            connect_args={"check_same_thread": False}
        )
        
        # Create session maker
        self.async_session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self._initialized = True
        logger.info("API database adapter initialized successfully")
    
    async def close(self) -> None:
        """Close the database connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("API database adapter closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error("Database session error", error=str(e), exc_info=True)
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database connection."""
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                row = result.fetchone()
                
                # Get table count
                table_result = await session.execute(
                    text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                )
                table_count = table_result.scalar()
                
                return {
                    "status": "healthy",
                    "connection": "ok",
                    "test_query": "passed",
                    "tables": table_count,
                    "database_path": get_shared_database_path()
                }
        except Exception as e:
            logger.error("Database health check failed", error=str(e), exc_info=True)
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e),
                "database_path": get_shared_database_path()
            }
    
    # ================================================================
    # USER OPERATIONS
    # ================================================================
    
    async def get_user_by_azure_id(self, azure_user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by their Azure AD user ID."""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, azure_user_id, email, display_name, role, 
                               is_active, last_login_at, created_at, updated_at
                        FROM users 
                        WHERE azure_user_id = :azure_user_id AND is_active = 1
                    """),
                    {"azure_user_id": azure_user_id}
                )
                row = result.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "azure_user_id": row[1],
                        "email": row[2],
                        "display_name": row[3],
                        "role": row[4],
                        "is_active": bool(row[5]),
                        "last_login_at": row[6],
                        "created_at": row[7],
                        "updated_at": row[8]
                    }
                return None
        except Exception as e:
            logger.error("Error getting user by Azure ID", azure_user_id=azure_user_id, error=str(e))
            raise
    
    async def update_user_last_login(self, user_id: str) -> None:
        """Update the user's last login timestamp."""
        try:
            async with self.get_session() as session:
                await session.execute(
                    text("""
                        UPDATE users 
                        SET last_login_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :user_id
                    """),
                    {"user_id": user_id}
                )
                await session.commit()
        except Exception as e:
            logger.error("Error updating user last login", user_id=user_id, error=str(e))
            raise
    
    # ================================================================
    # INFERENCE QUEUE OPERATIONS
    # ================================================================
    
    async def create_inference_request(
        self, 
        user_id: str, 
        request_type: str,
        input_data: Dict[str, Any],
        client_id: Optional[str] = None,
        priority: int = 3
    ) -> str:
        """Create a new inference request in the queue."""
        try:
            async with self.get_session() as session:
                # Generate request ID
                result = await session.execute(text("SELECT lower(hex(randomblob(16)))"))
                request_id = result.scalar()
                
                await session.execute(
                    text("""
                        INSERT INTO inference_queue 
                        (id, user_id, client_id, request_type, input_data, priority, status, created_at)
                        VALUES (:id, :user_id, :client_id, :request_type, :input_data, :priority, 'pending', CURRENT_TIMESTAMP)
                    """),
                    {
                        "id": request_id,
                        "user_id": user_id,
                        "client_id": client_id,
                        "request_type": request_type,
                        "input_data": json.dumps(input_data),  # Store as JSON string
                        "priority": priority
                    }
                )
                await session.commit()
                
                logger.info(
                    "Inference request created", 
                    request_id=request_id, 
                    user_id=user_id, 
                    client_id=client_id,
                    request_type=request_type
                )
                return request_id
        except Exception as e:
            logger.error("Error creating inference request", error=str(e))
            raise
    
    async def get_inference_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of an inference request."""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, status, result_data, error_message, 
                               completed_at, processing_time_ms
                        FROM inference_queue
                        WHERE id = :request_id
                    """),
                    {"request_id": request_id}
                )
                row = result.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "status": row[1],
                        "result_data": row[2],
                        "error_message": row[3],
                        "completed_at": row[4],
                        "processing_time_ms": row[5]
                    }
                return None
        except Exception as e:
            logger.error("Error getting inference result", request_id=request_id, error=str(e))
            raise
    
    # ================================================================
    # CHAT OPERATIONS
    # ================================================================
    
    async def get_chat_thread(self, thread_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a chat thread by ID (with user ownership check)."""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, user_id, title, custom_gpt_id, 
                               created_at, updated_at
                        FROM chat_threads
                        WHERE id = :thread_id AND user_id = :user_id
                    """),
                    {"thread_id": thread_id, "user_id": user_id}
                )
                row = result.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "title": row[2],
                        "custom_gpt_id": row[3],
                        "created_at": row[4],
                        "updated_at": row[5]
                    }
                return None
        except Exception as e:
            logger.error("Error getting chat thread", thread_id=thread_id, error=str(e))
            raise
    
    async def create_chat_message(
        self, 
        thread_id: str, 
        content: str, 
        role: str = "user"
    ) -> str:
        """Create a new chat message."""
        try:
            async with self.get_session() as session:
                # Generate message ID
                result = await session.execute(text("SELECT lower(hex(randomblob(16)))"))
                message_id = result.scalar()
                
                await session.execute(
                    text("""
                        INSERT INTO chat_messages 
                        (id, thread_id, role, content, created_at)
                        VALUES (:id, :thread_id, :role, :content, CURRENT_TIMESTAMP)
                    """),
                    {
                        "id": message_id,
                        "thread_id": thread_id,
                        "role": role,
                        "content": content
                    }
                )
                await session.commit()
                
                return message_id
        except Exception as e:
            logger.error("Error creating chat message", error=str(e))
            raise


# Global database adapter instance
db_adapter = DatabaseAdapter()


# Convenience functions for backward compatibility
async def get_database() -> DatabaseAdapter:
    """Get the database adapter instance."""
    if not db_adapter._initialized:
        await db_adapter.initialize()
    return db_adapter


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session (backward compatibility)."""
    async with db_adapter.get_session() as session:
        yield session