"""
Simplified Database adapter for Baker Compliant AI inference system.

Provides database connectivity and operations for the inference service,
connecting to the shared Baker Compliant AI database using aiosqlite.
This simplified version avoids connection pooling to prevent initialization deadlocks.
"""

import asyncio
import json
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator

import aiosqlite

from inference.src.utils.logging import logger


def get_shared_database_path() -> str:
    """Get the path to the shared database."""
    # Database is in the project root database/ directory
    project_root = Path(__file__).parent.parent.parent.parent  # inference/src/database/ -> project root
    db_path = project_root / "database" / "baker_compliant_ai.db"
    return str(db_path.absolute())


class DatabaseAdapter:
    """
    Simplified database adapter for the inference service.
    
    Connects to the shared Baker Compliant AI database and provides
    inference-specific operations using simple connections (no pooling).
    """
    
    def __init__(self):
        self.database_path = Path(get_shared_database_path())
        self.initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the database adapter."""
        async with self._lock:
            if self.initialized:
                return
            
            try:
                # Ensure database exists
                if not self.database_path.exists():
                    raise FileNotFoundError(
                        f"Shared database not found at {self.database_path}. "
                        f"Please run 'python database/init_database.py' first."
                    )
                
                logger.info(
                    "Initializing inference database adapter", 
                    database_path=str(self.database_path)
                )
                
                # Test database connectivity with a simple connection
                async with aiosqlite.connect(str(self.database_path)) as conn:
                    await conn.execute("SELECT 1")
                
                self.initialized = True
                logger.info(
                    "Inference database adapter initialized",
                    database_path=str(self.database_path)
                )
                
            except Exception as e:
                logger.error(
                    "Failed to initialize inference database adapter",
                    error=str(e),
                    database_path=str(self.database_path),
                    exc_info=True
                )
                raise
    
    @asynccontextmanager
    async def _get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Get a database connection."""
        if not self.initialized:
            await self.initialize()
        
        conn = None
        try:
            conn = await aiosqlite.connect(
                str(self.database_path),
                timeout=30.0
            )
            
            # Configure connection
            conn.row_factory = aiosqlite.Row  # Enable dict-like access
            await conn.execute("PRAGMA foreign_keys = ON")
            await conn.execute("PRAGMA journal_mode = WAL")
            await conn.execute("PRAGMA synchronous = NORMAL")
            
            yield conn
            
        except Exception as e:
            logger.error(
                "Database connection error",
                error=str(e),
                database_path=str(self.database_path),
                exc_info=True
            )
            raise
        finally:
            if conn:
                await conn.close()

    async def close(self) -> None:
        """Close the database adapter (no-op for simplified version)."""
        logger.info("Database adapter close called")
        pass

    # Queue polling and management methods
    async def poll_inference_queue(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Poll the inference queue for pending requests."""
        async with self._get_connection() as conn:
            cursor = await conn.execute("""
                SELECT id, request_type, message_id, custom_gpt_id, user_id, priority, 
                       status, created_at, started_at, completed_at, input_data
                FROM inference_queue 
                WHERE status = 'pending'
                ORDER BY priority ASC, created_at ASC
                LIMIT ?
            """, (limit,))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def claim_inference_request(self, request_id: str) -> bool:
        """Claim a request for processing."""
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    UPDATE inference_queue 
                    SET status = 'processing', started_at = ?
                    WHERE id = ? AND status = 'pending'
                """, (datetime.utcnow().isoformat(), request_id))
                
                await conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.warning(
                "Failed to claim request",
                request_id=request_id,
                error=str(e)
            )
            return False
    
    async def complete_inference_request(
        self,
        request_id: str,
        success: bool,
        response_data: dict,
        error_message: Optional[str] = None
    ) -> bool:
        """Marks a request as completed or failed."""
        status = "completed" if success else "failed"

        # Safely extract content and metadata from response_data
        response_content = response_data.get("content") if response_data else None
        response_metadata = response_data.get("metadata", {}) if response_data else {}

        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    UPDATE inference_queue
                    SET
                        status = ?,
                        completed_at = ?,
                        response_content = ?,
                        response_metadata = ?,
                        error_message = ?
                    WHERE id = ? AND status = 'processing'
                """, (
                    status,
                    datetime.utcnow().isoformat(),
                    response_content,
                    json.dumps(response_metadata),
                    error_message,
                    request_id
                ))
                
                await conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(
                "Failed to complete request",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        async with self._get_connection() as conn:
            # Get counts by status
            cursor = await conn.execute("""
                SELECT status, COUNT(*) as count
                FROM inference_queue 
                GROUP BY status
            """)
            status_counts = dict(await cursor.fetchall())
            
            # Get total count
            cursor = await conn.execute("SELECT COUNT(*) FROM inference_queue")
            total_count = (await cursor.fetchone())[0]
            
            return {
                "total_requests": total_count,
                "pending": status_counts.get("pending", 0),
                "processing": status_counts.get("processing", 0),
                "completed": status_counts.get("completed", 0),
                "failed": status_counts.get("failed", 0)
            }
    
    async def cleanup_old_requests(self, days_old: int) -> int:
        """Clean up old completed/failed requests."""
        async with self._get_connection() as conn:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            cursor = await conn.execute("""
                DELETE FROM inference_queue 
                WHERE status IN ('completed', 'failed') 
                AND created_at < ?
            """, (cutoff_date.isoformat(),))
            
            await conn.commit()
            return cursor.rowcount
    
    async def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute a query and fetch one result."""
        async with self._get_connection() as conn:
            cursor = await conn.execute(query, params or ())
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def create_assistant_message(
        self,
        thread_id: str,
        content: str,
        custom_gpt_id: Optional[str],
        user_id: str,
        confidence_score: Optional[float] = None,
        model_used: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        compliance_flags: Optional[List[str]] = None,
        sec_compliant: bool = True,
        human_review_required: bool = False
    ) -> Optional[str]:
        """
        Create a new assistant message in the messages table.
        
        Args:
            thread_id: Thread identifier
            content: Message content
            custom_gpt_id: Custom GPT identifier (optional)
            user_id: User identifier
            confidence_score: AI confidence score (0.0-1.0)
            model_used: Model identifier used for generation
            processing_time_ms: Processing time in milliseconds
            compliance_flags: List of compliance flags (optional)
            sec_compliant: Whether message is SEC compliant
            human_review_required: Whether human review is required
            
        Returns:
            Message ID if successful, None if failed
        """
        try:
            async with self._get_connection() as conn:
                # Generate message ID
                message_id = None
                compliance_flags_json = json.dumps(compliance_flags or [])
                
                cursor = await conn.execute("""
                    INSERT INTO messages (
                        thread_id, content, role, custom_gpt_id, user_id,
                        confidence_score, model_used, processing_time_ms,
                        compliance_flags, sec_compliant, human_review_required
                    ) VALUES (?, ?, 'assistant', ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    thread_id, content, custom_gpt_id, user_id,
                    confidence_score, model_used, processing_time_ms,
                    compliance_flags_json, sec_compliant, human_review_required
                ))
                
                await conn.commit()
                
                # Get the generated message ID
                cursor = await conn.execute("SELECT last_insert_rowid()")
                row = await cursor.fetchone()
                if row:
                    # Get the actual message ID from the messages table
                    cursor = await conn.execute(
                        "SELECT id FROM messages WHERE rowid = ?", 
                        (row[0],)
                    )
                    result = await cursor.fetchone()
                    if result:
                        message_id = result[0]
                
                logger.debug(
                    "Assistant message created",
                    message_id=message_id,
                    thread_id=thread_id,
                    custom_gpt_id=custom_gpt_id
                )
                
                return message_id
                
        except Exception as e:
            logger.error(
                "Error creating assistant message",
                thread_id=thread_id,
                error=str(e),
                exc_info=True
            )
            return None


    async def create_thread_if_not_exists(
        self,
        thread_id: str,
        title: str,
        custom_gpt_id: str,
        user_id: str,
        client_id: Optional[str] = None
    ) -> bool:
        """
        Create a thread if it doesn't exist.
        
        Args:
            thread_id: Thread identifier
            title: Thread title
            custom_gpt_id: Custom GPT identifier
            user_id: User identifier
            client_id: Optional client identifier
            
        Returns:
            True if thread was created or already exists, False if creation failed
        """
        try:
            async with self._get_connection() as conn:
                # Check if thread exists
                cursor = await conn.execute(
                    "SELECT id FROM threads WHERE id = ?", 
                    (thread_id,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    logger.debug(
                        "Thread already exists",
                        thread_id=thread_id,
                        custom_gpt_id=custom_gpt_id
                    )
                    return True
                
                # Create new thread
                await conn.execute("""
                    INSERT INTO threads (
                        id, title, custom_gpt_id, user_id, client_id,
                        message_count, is_archived, tags, last_message_at
                    ) VALUES (?, ?, ?, ?, ?, 0, FALSE, '[]', CURRENT_TIMESTAMP)
                """, (
                    thread_id, title, custom_gpt_id, user_id, client_id
                ))
                
                await conn.commit()
                
                logger.info(
                    "Thread created successfully",
                    thread_id=thread_id,
                    custom_gpt_id=custom_gpt_id,
                    user_id=user_id
                )
                
                return True
                
        except Exception as e:
            logger.error(
                "Error creating thread",
                thread_id=thread_id,
                custom_gpt_id=custom_gpt_id,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            return False


    async def create_custom_gpt_if_not_exists(
        self,
        custom_gpt_id: str,
        name: str,
        description: str,
        system_prompt: str,
        specialization: str,
        user_id: str
    ) -> bool:
        """
        Create a custom GPT if it doesn't exist.
        
        Args:
            custom_gpt_id: Custom GPT identifier
            name: GPT name
            description: GPT description
            system_prompt: System prompt
            specialization: GPT specialization
            user_id: User who created it
            
        Returns:
            True if custom GPT was created or already exists, False if creation failed
        """
        try:
            async with self._get_connection() as conn:
                # Check if custom GPT exists
                cursor = await conn.execute(
                    "SELECT id FROM custom_gpts WHERE id = ?", 
                    (custom_gpt_id,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    logger.debug(
                        "Custom GPT already exists",
                        custom_gpt_id=custom_gpt_id,
                        specialization=specialization
                    )
                    return True
                
                # Create new custom GPT
                await conn.execute("""
                    INSERT INTO custom_gpts (
                        id, name, description, system_prompt, specialization,
                        color, icon, mcp_tools_enabled, is_active, user_id
                    ) VALUES (?, ?, ?, ?, ?, 'blue', 'Brain', '{"redtail_crm": false, "albridge_portfolio": false, "black_diamond": false}', TRUE, ?)
                """, (
                    custom_gpt_id, name, description, system_prompt, specialization, user_id
                ))
                
                await conn.commit()
                
                logger.info(
                    "Custom GPT created successfully",
                    custom_gpt_id=custom_gpt_id,
                    specialization=specialization,
                    user_id=user_id
                )
                
                return True
                
        except Exception as e:
            logger.error(
                "Error creating custom GPT",
                custom_gpt_id=custom_gpt_id,
                specialization=specialization,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            return False

    async def create_user_if_not_exists(
        self,
        user_id: str,
        email: str = None,
        display_name: str = None
    ) -> bool:
        """Create a user if it doesn't exist."""
        try:
            async with self._get_connection() as conn:
                # Check if user exists
                cursor = await conn.execute(
                    "SELECT id FROM users WHERE id = ?",
                    (user_id,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    logger.debug(
                        "User already exists",
                        user_id=user_id
                    )
                    return True
                
                # Create new user with minimal required fields
                await conn.execute("""
                    INSERT INTO users (
                        id, azure_user_id, email, display_name, role, 
                        first_name, last_name, is_active
                    ) VALUES (?, ?, ?, ?, 'financial_advisor', 'Auto', 'User', TRUE)
                """, (
                    user_id,
                    user_id,  # Use same as azure_user_id 
                    email or f"{user_id}@bakergroup.com",
                    display_name or f"User {user_id}"
                ))
                
                await conn.commit()
                
                logger.info(
                    "User created successfully",
                    user_id=user_id,
                    email=email,
                    display_name=display_name
                )
                
                return True
                
        except Exception as e:
            logger.error(
                "Error creating user",
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            return False


# Global database adapter instance
db_adapter = DatabaseAdapter()


# Backward compatibility functions
async def get_database_service() -> DatabaseAdapter:
    """Get the database adapter instance."""
    if not db_adapter.initialized:
        await db_adapter.initialize()
    return db_adapter


# Alias for compatibility
DatabaseService = DatabaseAdapter