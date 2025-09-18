"""
Baker Compliant AI - GPU Resource Manager

Manages GPU resource allocation for Ollama models to prevent contention and
ensure optimal performance for the Baker Compliant AI system.
"""

import asyncio
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from ..utils.config import InferenceSettings
from ..utils.logging import logger, log_performance_metric, log_error_with_context


class GPUResourceManager:
    """
    Manages GPU resource allocation using semaphores to prevent model contention.
    
    Uses asyncio.Semaphore(1) to ensure only one inference runs at a time on GPU,
    preventing out-of-memory errors and ensuring optimal performance.
    """
    
    def __init__(self, settings: InferenceSettings):
        """Initialize GPU resource manager."""
        self.settings = settings
        
        # Single GPU semaphore - only one model can use GPU at a time
        self._gpu_semaphore = asyncio.Semaphore(1)
        
        # Resource tracking
        self._resource_acquired_at: Optional[datetime] = None
        self._current_holder: Optional[str] = None
        self._total_acquisitions = 0
        self._total_wait_time_ms = 0
        
        logger.info(
            "GPU Resource Manager initialized",
            gpu_timeout_seconds=settings.service.gpu_timeout_seconds,
            max_concurrent_gpu_requests=1
        )
    
    async def initialize(self) -> None:
        """Initialize the GPU resource manager."""
        logger.info("GPU Resource Manager initialization complete")
    
    async def acquire_resource(self, timeout: Optional[int] = None, request_id: Optional[str] = None) -> bool:
        """
        Acquire GPU resource with optional timeout.
        
        Args:
            timeout: Maximum seconds to wait for resource (defaults to config value)
            request_id: Optional request ID for tracking
            
        Returns:
            True if resource acquired, False if timeout
        """
        if timeout is None:
            timeout = self.settings.service.gpu_timeout_seconds
        
        start_time = datetime.utcnow()
        request_id = request_id or f"req_{start_time.timestamp()}"
        
        logger.debug(
            "Attempting to acquire GPU resource",
            request_id=request_id,
            timeout_seconds=timeout
        )
        
        try:
            # Try to acquire with timeout
            acquired = await asyncio.wait_for(
                self._gpu_semaphore.acquire(),
                timeout=timeout
            )
            
            if acquired:
                # Track acquisition
                self._resource_acquired_at = datetime.utcnow()
                self._current_holder = request_id
                self._total_acquisitions += 1
                
                wait_time_ms = int((self._resource_acquired_at - start_time).total_seconds() * 1000)
                self._total_wait_time_ms += wait_time_ms
                
                # Log performance metrics
                log_performance_metric(
                    operation="gpu_resource_acquired",
                    duration_ms=wait_time_ms,
                    metadata={
                        "request_id": request_id,
                        "timeout_seconds": timeout,
                        "total_acquisitions": self._total_acquisitions,
                        "average_wait_time_ms": self._total_wait_time_ms // max(1, self._total_acquisitions)
                    }
                )
                
                logger.info(
                    "GPU resource acquired",
                    request_id=request_id,
                    wait_time_ms=wait_time_ms,
                    total_acquisitions=self._total_acquisitions
                )
                
                return True
            
        except asyncio.TimeoutError:
            wait_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            log_error_with_context(
                error_type="gpu_resource_timeout",
                error_message=f"GPU resource acquisition timeout after {timeout}s",
                context={
                    "request_id": request_id,
                    "timeout_seconds": timeout,
                    "wait_time_ms": wait_time_ms,
                    "current_holder": self._current_holder,
                    "acquired_at": self._resource_acquired_at.isoformat() if self._resource_acquired_at else None
                }
            )
            
            logger.warning(
                "GPU resource acquisition timeout",
                request_id=request_id,
                timeout_seconds=timeout,
                wait_time_ms=wait_time_ms,
                current_holder=self._current_holder
            )
            
            return False
        
        except Exception as e:
            log_error_with_context(
                error_type="gpu_resource_acquisition_error",
                error_message=str(e),
                context={
                    "request_id": request_id,
                    "timeout_seconds": timeout
                }
            )
            
            logger.error(
                "GPU resource acquisition error",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            
            return False
    
    async def release_resource(self, request_id: Optional[str] = None) -> None:
        """
        Release GPU resource.
        
        Args:
            request_id: Optional request ID for tracking
        """
        if self._resource_acquired_at is None:
            logger.warning("Attempting to release GPU resource that was not acquired")
            return
        
        request_id = request_id or self._current_holder
        
        # Calculate usage time
        usage_time_ms = int((datetime.utcnow() - self._resource_acquired_at).total_seconds() * 1000)
        
        # Log performance metrics
        log_performance_metric(
            operation="gpu_resource_released",
            duration_ms=usage_time_ms,
            metadata={
                "request_id": request_id,
                "usage_time_ms": usage_time_ms,
                "total_acquisitions": self._total_acquisitions
            }
        )
        
        logger.info(
            "GPU resource released",
            request_id=request_id,
            usage_time_ms=usage_time_ms
        )
        
        # Reset tracking
        self._resource_acquired_at = None
        self._current_holder = None
        
        # Release semaphore
        self._gpu_semaphore.release()
    
    async def is_available(self) -> bool:
        """Check if GPU resource is currently available."""
        return self._gpu_semaphore.locked() == False
    
    async def get_stats(self) -> dict:
        """Get GPU resource usage statistics."""
        stats = {
            "total_acquisitions": self._total_acquisitions,
            "average_wait_time_ms": self._total_wait_time_ms // max(1, self._total_acquisitions),
            "currently_acquired": self._resource_acquired_at is not None,
            "current_holder": self._current_holder,
            "resource_available": await self.is_available()
        }
        
        if self._resource_acquired_at:
            stats["current_usage_time_ms"] = int(
                (datetime.utcnow() - self._resource_acquired_at).total_seconds() * 1000
            )
        
        return stats
    
    @asynccontextmanager
    async def acquire_context(self, timeout: Optional[int] = None, request_id: Optional[str] = None):
        """
        Context manager for GPU resource acquisition.
        
        Usage:
            async with gpu_manager.acquire_context(timeout=30, request_id="req1") as acquired:
                if acquired:
                    # Use GPU resource
                    result = await some_gpu_operation()
        """
        acquired = await self.acquire_resource(timeout=timeout, request_id=request_id)
        try:
            yield acquired
        finally:
            if acquired:
                await self.release_resource(request_id=request_id)
    
    async def cleanup(self) -> None:
        """Cleanup GPU resource manager."""
        if self._resource_acquired_at:
            logger.warning(
                "GPU resource manager cleanup - resource was still acquired",
                current_holder=self._current_holder,
                usage_time_ms=int((datetime.utcnow() - self._resource_acquired_at).total_seconds() * 1000)
            )
            await self.release_resource()
        
        # Log final stats
        final_stats = await self.get_stats()
        logger.info("GPU Resource Manager cleanup complete", final_stats=final_stats)