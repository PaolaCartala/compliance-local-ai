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
                SELECT * FROM inference_queue 
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
    
    async def complete_inference_request(self, request_id: str, success: bool, result_data: Any = None, error_message: str = None) -> bool:
        """Complete an inference request."""
        try:
            async with self._get_connection() as conn:
                if success:
                    await conn.execute("""
                        UPDATE inference_queue 
                        SET status = 'completed', 
                            completed_at = ?,
                            processing_time_ms = ?
                        WHERE id = ?
                    """, (datetime.utcnow().isoformat(), 1000, request_id))  # Default 1000ms
                else:
                    await conn.execute("""
                        UPDATE inference_queue 
                        SET status = 'failed', 
                            completed_at = ?,
                            error = ?
                        WHERE id = ?
                    """, (datetime.utcnow().isoformat(), error_message, request_id))
                
                await conn.commit()
                return True
                
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