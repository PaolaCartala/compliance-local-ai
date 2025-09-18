"""
Database adapter for Baker Compliant AI inference system.

Provides database connectivity and operations for the inference service,
connecting to the shared Baker Compliant AI database using aiosqlite.
This adapter exposes only the operations needed by the inference service.
"""

import asyncio
import json
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
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
    Database adapter for the inference service.
    
    Connects to the shared Baker Compliant AI database and provides
    inference-specific operations while maintaining separation of concerns.
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
    
    async def _create_connection(self) -> aiosqlite.Connection:
        """Create a new async database connection."""
        conn = await aiosqlite.connect(
            str(self.database_path),
            timeout=30.0
        )
        
        # Configure connection
        conn.row_factory = aiosqlite.Row  # Enable dict-like access
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute("PRAGMA journal_mode = WAL")
        await conn.execute("PRAGMA synchronous = NORMAL")
        await conn.execute("PRAGMA cache_size = -2000")  # 2MB cache
        await conn.execute("PRAGMA temp_store = MEMORY")
        await conn.commit()
        
        return conn
    
    @asynccontextmanager
    async def _get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Get a connection from the pool."""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get connection from pool (wait up to 30 seconds)
            conn = await asyncio.wait_for(
                self.connection_pool.get(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.warning("Connection pool timeout, creating new connection")
            conn = await self._create_connection()
        
        try:
            yield conn
        except Exception as e:
            # Log connection errors
            logger.error(
                "Database connection error",
                error=str(e),
                exc_info=True
            )
            
            # Try to rollback transaction
            try:
                await conn.rollback()
            except Exception:
                pass
            
            # Close bad connection and create new one
            try:
                await conn.close()
            except Exception:
                pass
            
            conn = await self._create_connection()
            raise
        finally:
            # Return connection to pool
            try:
                await self.connection_pool.put(conn)
            except asyncio.QueueFull:
                # Pool is full, close this connection
                await conn.close()
    
    async def execute_query(
        self,
        query: str,
        params: tuple = None
    ) -> aiosqlite.Cursor:
        """
        Execute a SQL query with optional parameters.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Cursor object with query results
        """
        async with self._get_connection() as conn:
            try:
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                
                await conn.commit()
                return cursor
                
            except Exception as e:
                await conn.rollback()
                logger.error(
                    "Query execution failed",
                    query=query[:100] + "..." if len(query) > 100 else query,
                    error=str(e),
                    exc_info=True
                )
                raise
    
    async def fetch_one(
        self,
        query: str,
        params: tuple = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row from a query.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Dictionary representing the row or None if no results
        """
        async with self._get_connection() as conn:
            try:
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                
                row = await cursor.fetchone()
                return dict(row) if row else None
                
            except Exception as e:
                logger.error(
                    "Fetch one failed",
                    query=query[:100] + "..." if len(query) > 100 else query,
                    error=str(e),
                    exc_info=True
                )
                raise
    
    async def fetch_all(
        self,
        query: str,
        params: tuple = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows from a query.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of dictionaries representing the rows
        """
        async with self._get_connection() as conn:
            try:
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows] if rows else []
                
            except Exception as e:
                logger.error(
                    "Fetch all failed",
                    query=query[:100] + "..." if len(query) > 100 else query,
                    error=str(e),
                    exc_info=True
                )
                raise
    
    async def execute_script(self, script: str) -> None:
        """
        Execute a SQL script (multiple statements).
        
        Args:
            script: SQL script string
        """
        async with self._get_connection() as conn:
            try:
                await conn.executescript(script)
                await conn.commit()
                
                logger.debug(
                    "Script executed successfully",
                    script_length=len(script)
                )
                
            except Exception as e:
                await conn.rollback()
                logger.error(
                    "Script execution failed",
                    error=str(e),
                    script_length=len(script),
                    exc_info=True
                )
                raise
    
    async def get_custom_gpt(self, custom_gpt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a Custom GPT configuration by ID.
        
        Args:
            custom_gpt_id: Custom GPT identifier
            
        Returns:
            Custom GPT configuration or None if not found
        """
        return await self.fetch_one(
            """
            SELECT id, user_id, name, description, specialization,
                   system_prompt, mcp_tools_enabled, model_preference,
                   created_at, updated_at, is_active
            FROM custom_gpts 
            WHERE id = ? AND is_active = 1
            """,
            (custom_gpt_id,)
        )
    
    async def create_message(
        self,
        message_id: str,
        thread_id: str,
        content: str,
        role: str = "user",
        attachments: List[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new message in the database.
        
        Args:
            message_id: Unique message identifier
            thread_id: Thread identifier
            content: Message content
            role: Message role (user/assistant)
            attachments: Message attachments
            
        Returns:
            True if message was created successfully
        """
        try:
            await self.execute_query(
                """
                INSERT INTO messages (
                    id, thread_id, content, role, attachments,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                """,
                (
                    message_id,
                    thread_id,
                    content,
                    role,
                    json.dumps(attachments) if attachments else None,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                )
            )
            
            logger.debug(
                "Message created",
                message_id=message_id,
                thread_id=thread_id,
                role=role
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to create message",
                message_id=message_id,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def get_thread_messages(
        self,
        thread_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent messages from a thread for context.
        
        Args:
            thread_id: Thread identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        return await self.fetch_all(
            """
            SELECT id, content, role, ai_response, attachments,
                   status, created_at
            FROM messages 
            WHERE thread_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (thread_id, limit)
        )
    
    async def log_audit_event(
        self,
        event_type: str,
        entity_id: str,
        entity_type: str,
        action: str,
        details: Dict[str, Any] = None,
        user_id: str = None
    ) -> None:
        """
        Log an audit event for compliance tracking.
        
        Args:
            event_type: Type of event (chat, compliance, etc.)
            entity_id: ID of the affected entity
            entity_type: Type of entity (message, custom_gpt, etc.)
            action: Action performed
            details: Additional event details
            user_id: User who performed the action
        """
        try:
            await self.execute_query(
                """
                INSERT INTO audit_trail (
                    event_type, entity_id, entity_type, action,
                    details, user_id, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_type,
                    entity_id,
                    entity_type,
                    action,
                    json.dumps(details) if details else None,
                    user_id,
                    datetime.utcnow().isoformat()
                )
            )
            
        except Exception as e:
            # Don't fail the main operation if audit logging fails
            logger.warning(
                "Failed to log audit event",
                event_type=event_type,
                entity_id=entity_id,
                error=str(e)
            )
    
    async def close(self) -> None:
        """Close all database connections."""
        if not self.initialized:
            return
        
        try:
            # Close all connections in pool
            while not self.connection_pool.empty():
                try:
                    conn = await asyncio.wait_for(
                        self.connection_pool.get(),
                        timeout=1.0
                    )
                    await conn.close()
                except (asyncio.TimeoutError, asyncio.QueueEmpty):
                    break
            
            self.initialized = False
            logger.info("Database service closed")
            
        except Exception as e:
            logger.error(
                "Error closing database service",
                error=str(e),
                exc_info=True
            )

    # === INFERENCE QUEUE METHODS ===
    
    async def poll_inference_queue(self, limit: int = 1) -> List[Dict[str, Any]]:
        """
        Poll for pending inference requests from the queue.
        
        Orders by priority (1=highest) and created_at for FIFO within same priority.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of pending inference requests
        """
        return await self.fetch_all(
            """
            SELECT id, request_type, message_id, custom_gpt_id, user_id,
                   request_data, priority, status, created_at, updated_at
            FROM inference_queue 
            WHERE status = 'pending'
            ORDER BY priority ASC, created_at ASC
            LIMIT ?
            """,
            (limit,)
        )
    
    async def claim_inference_request(self, request_id: str) -> bool:
        """
        Claim an inference request for processing.
        
        Args:
            request_id: Request identifier
            
        Returns:
            True if request was successfully claimed
        """
        try:
            cursor = await self.execute_query(
                """
                UPDATE inference_queue 
                SET status = 'processing', 
                    processing_started_at = ?,
                    updated_at = ?
                WHERE id = ? AND status = 'pending'
                """,
                (
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                    request_id
                )
            )
            
            success = cursor.rowcount > 0
            if success:
                logger.debug(
                    "Inference request claimed",
                    request_id=request_id
                )
            else:
                logger.warning(
                    "Failed to claim inference request - already processing or not found",
                    request_id=request_id
                )
            
            return success
            
        except Exception as e:
            logger.error(
                "Error claiming inference request",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def complete_inference_request(
        self,
        request_id: str,
        success: bool,
        response_data: Dict[str, Any],
        error_message: Optional[str] = None
    ) -> bool:
        """
        Mark an inference request as completed.
        
        Args:
            request_id: Request identifier
            success: Whether processing was successful
            response_data: Response data from inference
            error_message: Error message if failed
            
        Returns:
            True if request was successfully completed
        """
        try:
            status = "completed" if success else "failed"
            now = datetime.utcnow().isoformat()
            
            # Update the inference queue record
            await self.execute_query(
                """
                UPDATE inference_queue 
                SET status = ?,
                    completed_at = ?,
                    updated_at = ?,
                    error_message = ?
                WHERE id = ?
                """,
                (status, now, now, error_message, request_id)
            )
            
            # Store the response in response_storage table
            await self.execute_query(
                """
                INSERT INTO response_storage (
                    request_id, response_data, success, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    json.dumps(response_data) if response_data else None,
                    1 if success else 0,
                    error_message,
                    now
                )
            )
            
            logger.debug(
                "Inference request completed",
                request_id=request_id,
                success=success
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error completing inference request",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """
        Get statistics about the inference queue.
        
        Returns:
            Dictionary with queue statistics
        """
        try:
            stats = {}
            
            # Count requests by status
            status_counts = await self.fetch_all(
                """
                SELECT status, COUNT(*) as count
                FROM inference_queue
                GROUP BY status
                """
            )
            
            for row in status_counts:
                stats[f"{row['status']}_count"] = row['count']
            
            # Get total queue size
            total = await self.fetch_one(
                "SELECT COUNT(*) as total FROM inference_queue"
            )
            stats['total_requests'] = total['total'] if total else 0
            
            # Get average processing time for completed requests
            avg_time = await self.fetch_one(
                """
                SELECT AVG(
                    CAST((julianday(completed_at) - julianday(processing_started_at)) * 86400000 AS INTEGER)
                ) as avg_processing_time_ms
                FROM inference_queue
                WHERE status = 'completed' AND processing_started_at IS NOT NULL
                """
            )
            
            stats['avg_processing_time_ms'] = int(avg_time['avg_processing_time_ms']) if avg_time and avg_time['avg_processing_time_ms'] else 0
            
            return stats
            
        except Exception as e:
            logger.error(
                "Error getting queue statistics",
                error=str(e),
                exc_info=True
            )
            return {}
    
    async def cleanup_old_requests(self, days_old: int = 7) -> int:
        """
        Clean up old completed/failed requests from the queue.
        
        Args:
            days_old: Remove requests older than this many days
            
        Returns:
            Number of requests removed
        """
        try:
            cursor = await self.execute_query(
                """
                DELETE FROM inference_queue
                WHERE status IN ('completed', 'failed')
                AND created_at < datetime('now', '-{} days')
                """.format(days_old)
            )
            
            removed_count = cursor.rowcount
            
            if removed_count > 0:
                logger.info(
                    "Cleaned up old inference requests",
                    removed_count=removed_count,
                    days_old=days_old
                )
            
            return removed_count
            
        except Exception as e:
            logger.error(
                "Error cleaning up old requests",
                error=str(e),
                exc_info=True
            )
            return 0


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