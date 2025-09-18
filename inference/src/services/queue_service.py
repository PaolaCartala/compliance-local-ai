"""
Queue service for managing inference requests and priorities.

Handles queue operations, priority management, and request lifecycle
for the Baker Compliant AI inference system.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from inference.src.database.service import DatabaseAdapter
from inference.src.utils.logging import logger, log_queue_operation


class RequestStatus(Enum):
    """Request status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class QueueService:
    """
    Service for managing the inference request queue.
    
    Handles priority-based request processing, queue monitoring,
    and request lifecycle management with database persistence.
    """
    
    def __init__(self, database_service: DatabaseAdapter):
        self.db = database_service
        self.processing_lock = asyncio.Lock()
        self._stats_cache = {}
        self._cache_updated = datetime.utcnow()
        self._cache_ttl = timedelta(seconds=30)  # Cache stats for 30 seconds
    
    async def initialize(self) -> None:
        """Initialize the queue service."""
        logger.info("Initializing queue service")
        
        # Ensure the database is initialized
        await self.db.initialize()
        
        # Log queue service ready
        logger.info("Queue service initialized successfully")
    
    async def get_next_request(self) -> Optional[Dict[str, Any]]:
        """
        Get and claim the next request from the queue based on priority.
        
        Returns:
            Dictionary containing request data or None if queue is empty
        """
        async with self.processing_lock:
            try:
                # Get the highest priority pending request
                requests = await self.db.poll_inference_queue(limit=1)
                
                if not requests:
                    return None
                
                request = requests[0]
                request_id = request["id"]
                
                # Try to claim the request
                claimed = await self.db.claim_inference_request(request_id)
                
                if not claimed:
                    logger.warning(
                        "Failed to claim request - may have been taken by another worker",
                        request_id=request_id
                    )
                    return None
                
                # Parse JSON fields safely
                try:
                    request_data = json.loads(request["request_data"]) if request["request_data"] else {}
                except (json.JSONDecodeError, TypeError):
                    request_data = {}
                
                # Prepare the complete request object
                complete_request = {
                    "request_id": request_id,
                    "request_type": request["request_type"],
                    "message_id": request["message_id"],
                    "custom_gpt_id": request["custom_gpt_id"],
                    "user_id": request["user_id"],
                    "priority": request["priority"],
                    "created_at": request["created_at"],
                    **request_data  # Unpack the request_data JSON
                }
                
                log_queue_operation(
                    operation="claim_request",
                    request_id=request_id,
                    priority=request["priority"],
                    queue_size=await self._get_queue_size()
                )
                
                return complete_request
                
            except Exception as e:
                logger.error(
                    "Error getting next request from queue",
                    error=str(e),
                    exc_info=True
                )
                return None
    
    async def complete_request(
        self,
        request_id: str,
        success: bool,
        response_data: Dict[str, Any],
        error_message: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> bool:
        """
        Mark a request as completed and store the response.
        
        Args:
            request_id: Request identifier
            success: Whether processing was successful
            response_data: Response data from inference
            error_message: Error message if failed
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            True if request was successfully completed
        """
        try:
            success_completed = await self.db.complete_inference_request(
                request_id=request_id,
                success=success,
                response_data=response_data,
                error_message=error_message
            )
            
            if success_completed:
                log_queue_operation(
                    operation="complete_request",
                    request_id=request_id,
                    priority=0,  # Priority not relevant for completed requests
                    queue_size=await self._get_queue_size(),
                    processing_time_ms=processing_time_ms
                )
            
            return success_completed
            
        except Exception as e:
            logger.error(
                "Error completing request",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def get_queue_statistics(self) -> Dict[str, Any]:
        """
        Get current queue statistics with caching.
        
        Returns:
            Dictionary with queue statistics
        """
        now = datetime.utcnow()
        
        # Check if cache is still valid
        if (now - self._cache_updated) < self._cache_ttl and self._stats_cache:
            return self._stats_cache
        
        try:
            # Get fresh statistics from database
            stats = await self.db.get_queue_stats()
            
            # Add additional computed statistics
            stats.update({
                "cache_updated": now.isoformat(),
                "queue_health": self._calculate_queue_health(stats)
            })
            
            # Update cache
            self._stats_cache = stats
            self._cache_updated = now
            
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
        Clean up old completed/failed requests.
        
        Args:
            days_old: Remove requests older than this many days
            
        Returns:
            Number of requests removed
        """
        try:
            removed_count = await self.db.cleanup_old_requests(days_old)
            
            if removed_count > 0:
                logger.info(
                    "Queue cleanup completed",
                    removed_count=removed_count,
                    days_old=days_old
                )
            
            return removed_count
            
        except Exception as e:
            logger.error(
                "Error during queue cleanup",
                error=str(e),
                exc_info=True
            )
            return 0
    
    async def get_user_priority(self, user_id: str) -> int:
        """
        Get priority for a user based on their role.
        
        Args:
            user_id: User identifier
            
        Returns:
            Priority value (1=highest, 10=lowest)
        """
        try:
            user = await self.db.fetch_one(
                "SELECT role FROM users WHERE id = ?",
                (user_id,)
            )
            
            if not user:
                return 5  # Default priority for unknown users
            
            # Map roles to priorities
            role_priorities = {
                "executive": 1,
                "senior_advisor": 2,
                "advisor": 3,
                "junior_advisor": 4,
                "staff": 5,
                "intern": 6
            }
            
            return role_priorities.get(user.get("role", "staff"), 5)
            
        except Exception as e:
            logger.error(
                "Error getting user priority",
                user_id=user_id,
                error=str(e)
            )
            return 5  # Default priority on error
    
    def _calculate_queue_health(self, stats: Dict[str, Any]) -> str:
        """
        Calculate queue health status based on statistics.
        
        Args:
            stats: Queue statistics
            
        Returns:
            Health status string
        """
        try:
            pending = stats.get("pending_count", 0)
            processing = stats.get("processing_count", 0)
            avg_time = stats.get("avg_processing_time_ms", 0)
            
            # Health criteria
            if pending > 50:
                return "critical"
            elif pending > 20 or avg_time > 30000:  # 30 seconds
                return "warning"
            elif processing > 0 or pending > 0:
                return "active"
            else:
                return "idle"
                
        except Exception:
            return "unknown"
    
    async def _get_queue_size(self) -> int:
        """Get current queue size (pending + processing)."""
        try:
            result = await self.db.fetch_one(
                """
                SELECT COUNT(*) as size 
                FROM inference_queue 
                WHERE status IN ('pending', 'processing')
                """
            )
            return result["size"] if result else 0
        except Exception:
            return 0
    
    async def get_queue_size(self) -> int:
        """Public method to get current queue size."""
        return await self._get_queue_size()