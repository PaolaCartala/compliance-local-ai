"""
Baker Compliant AI - Main Inference Service

Coordinates the inference pipeline by polling the queue, routing to appropriate agents,
and managing GPU resources for optimal performance.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from ..utils.config import InferenceSettings
from ..utils.logging import logger, log_error_with_context, log_compliance_audit, log_performance_metric, log_retry_attempt
from ..database.service import DatabaseAdapter
from ..services.queue_service import QueueService
from ..agents.chat_agent import ChatAgent
from ..services.gpu_manager import GPUResourceManager


class InferenceService:
    """
    Main inference service that coordinates the pipeline.
    
    Manages request processing, agent routing, and GPU resource allocation
    with comprehensive logging and error handling for SEC compliance.
    """
    
    def __init__(self, settings: InferenceSettings):
        """Initialize the inference service with configuration."""
        self.settings = settings
        self.config = settings  # Alias for backward compatibility
        self.running = False
        self.start_time: Optional[datetime] = None
        
        # Initialize services
        self.db_service = DatabaseAdapter()
        self.queue_service = QueueService(self.db_service)
        self.gpu_manager = GPUResourceManager(settings)
        
        # Initialize agents
        self.chat_agent = ChatAgent()
        self.settings = settings  # Store for later use in initialize
        
        # Performance tracking
        self.stats = {
            "requests_processed": 0,
            "requests_successful": 0,
            "total_processing_time_ms": 0,
            "average_processing_time_ms": 0
        }
        
        logger.info(
            "Inference service initialized",
            gpu_timeout_seconds=settings.service.gpu_timeout_seconds,
            poll_interval_seconds=settings.service.poll_interval_seconds,
            max_queue_retries=settings.service.max_queue_retries
        )
    
    async def initialize(self) -> None:
        """Initialize all service components."""
        logger.info("Initializing inference service components")
        
        # Initialize database service
        await self.db_service.initialize()
        
        # Initialize queue service
        await self.queue_service.initialize()
        
        # Initialize GPU manager
        await self.gpu_manager.initialize()
        
        # Initialize chat agent
        await self.chat_agent.initialize(
            base_url=self.settings.ollama.base_url,
            chat_model=self.settings.ollama.chat_model,
            vision_model=self.settings.ollama.vision_model
        )
        
        logger.info("All inference service components initialized successfully")
    
    async def start(self) -> None:
        """Start the main inference service loop."""
        if self.running:
            logger.warning("Inference service is already running")
            return
        
        self.running = True
        self.start_time = datetime.utcnow()
        
        logger.info("Starting inference service main loop")
        
        # Log compliance audit for service start
        log_compliance_audit(
            action="inference_service_start",
            user_id="system",
            request_id="inference_service_startup",
            compliance_status="COMPLIANT",
            details={
                "start_time": self.start_time.isoformat(),
                "configuration": {
                    "gpu_timeout_seconds": self.settings.service.gpu_timeout_seconds,
                    "poll_interval_seconds": self.settings.service.poll_interval_seconds,
                    "max_queue_retries": self.settings.service.max_queue_retries
                }
            }
        )
        
        # Main service loop with circuit breaker pattern
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while self.running:
                try:
                    # Process inference requests
                    await self._process_inference_request()
                    
                    # Reset error counter on successful cycle
                    consecutive_errors = 0
                    
                    # Log health check periodically
                    if self.stats["requests_processed"] % 100 == 0:
                        await self._log_health_metrics()
                        
                except Exception as e:
                    consecutive_errors += 1
                    error_delay = min(consecutive_errors * 2, 30)  # Exponential backoff, max 30s
                    
                    # Log with enhanced error context
                    log_error_with_context(
                        error_type="main_loop_cycle",
                        error_message=str(e),
                        context={
                            "consecutive_errors": consecutive_errors,
                            "max_consecutive_errors": max_consecutive_errors,
                            "retry_delay_seconds": error_delay,
                            "service_uptime_seconds": int((datetime.utcnow() - self.start_time).total_seconds())
                        }
                    )
                    
                    # If too many consecutive errors, stop the service
                    if consecutive_errors >= max_consecutive_errors:
                        log_error_with_context(
                            error_type="service_failure",
                            error_message="Too many consecutive errors, stopping service",
                            context={
                                "consecutive_errors": consecutive_errors,
                                "max_allowed": max_consecutive_errors,
                                "service_uptime_seconds": int((datetime.utcnow() - self.start_time).total_seconds())
                            }
                        )
                        self.running = False
                        break
                    
                    # Log retry attempt with enhanced context
                    log_retry_attempt(
                        operation="main_loop_cycle",
                        attempt_number=consecutive_errors,
                        max_attempts=max_consecutive_errors,
                        error_reason=str(e),
                        request_id=f"service_main_loop_{consecutive_errors}"
                    )
                    
                    # Wait before retrying with exponential backoff
                    await asyncio.sleep(error_delay)
                
                await asyncio.sleep(self.config.service.poll_interval_seconds)
                
        except asyncio.CancelledError:
            logger.info("Inference service cancelled")
            raise
        except Exception as e:
            logger.critical("Inference service main loop failed catastrophically", error=str(e), exc_info=True)
            raise
        finally:
            self.running = False
            logger.info("Inference service main loop stopped")
    
    async def stop(self) -> None:
        """Stop the inference service gracefully."""
        logger.info("Stopping inference service")
        
        # Log compliance audit for service stop
        if self.start_time:
            uptime_seconds = int((datetime.utcnow() - self.start_time).total_seconds())
            log_compliance_audit(
                action="inference_service_stop",
                user_id="system",
                request_id="inference_service_shutdown",
                compliance_status="COMPLIANT",
                details={
                    "stop_time": datetime.utcnow().isoformat(),
                    "uptime_seconds": uptime_seconds,
                    "final_stats": self.stats.copy()
                }
            )
        
        self.running = False
        
        # Cleanup resources
        if hasattr(self, 'gpu_manager'):
            await self.gpu_manager.cleanup()
        
        logger.info("Inference service stopped successfully")
    
    async def _process_inference_request(self) -> None:
        """Process a single inference request from the queue."""
        try:
            # Get next request from queue
            request = await self.queue_service.get_next_request()
            
            if not request:
                # No requests to process
                logger.debug("No requests in queue")
                return
            
            # Debug logging to see what's in the request
            logger.debug("Request received", request_keys=list(request.keys()) if request else "None", request_content=request)
            
            request_id = request["request_id"]
            request_type = request["request_type"]
            retry_count = request.get("retry_count", 0)
            max_retries = self.settings.service.max_queue_retries
            
            logger.info(
                "Processing inference request",
                request_id=request_id,
                request_type=request_type,
                priority=request["priority"],
                retry_count=retry_count,
                max_retries=max_retries
            )
            
            # Log compliance audit for request start
            log_compliance_audit(
                action="inference_request_start",
                user_id=request["user_id"],
                request_id=request_id,
                compliance_status="COMPLIANT",
                details={
                    "request_type": request_type,
                    "priority": request["priority"],
                    "retry_count": retry_count
                }
            )
            
            start_time = datetime.utcnow()
            
            # Process the request with retries
            result = None
            for attempt in range(max_retries + 1):
                try:
                    cycle_start = datetime.utcnow()
                    
                    # Route request to appropriate agent based on type
                    if request_type in ["chat", "analysis", "compliance_check"]:
                        result = await self._process_chat_request(request)
                    else:
                        result = {
                            "success": False,
                            "error": f"Unknown request type: {request_type}",
                            "processing_time_ms": 0
                        }
                    
                    # If successful, break out of retry loop
                    if result.get("success"):
                        break
                        
                except Exception as e:
                    is_last_attempt = attempt == max_retries
                    
                    logger.error(
                        "Request processing attempt failed",
                        request_id=request_id,
                        attempt=attempt + 1,
                        max_attempts=max_retries + 1,
                        error=str(e),
                        is_last_attempt=is_last_attempt,
                        exc_info=not is_last_attempt  # Only log full traceback on last attempt
                    )
                    
                    if is_last_attempt:
                        # Final failure - create error result
                        processing_time_ms = int((datetime.utcnow() - cycle_start).total_seconds() * 1000)
                        result = {
                            "success": False,
                            "error": f"Failed after {max_retries + 1} attempts: {str(e)}",
                            "processing_time_ms": processing_time_ms,
                            "retry_exhausted": True
                        }
                        break
                    else:
                        # Wait before retry
                        retry_delay = min(2 ** attempt, 10)  # Exponential backoff, max 10s
                        await asyncio.sleep(retry_delay)
            
            # Calculate total processing time
            total_processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log performance metrics
            log_performance_metric(
                metric_type="inference_request_complete",
                value=total_processing_time_ms,
                unit="ms",
                request_id=request_id,
                context={
                    "request_type": request_type,
                    "success": result.get("success", False),
                    "retry_count": retry_count,
                    "priority": request["priority"]
                }
            )
            
            # Update result with total processing time
            if "processing_time_ms" not in result:
                result["processing_time_ms"] = total_processing_time_ms
            
            # Complete the request in the queue
            await self.queue_service.complete_request(
                request_id,
                success=result.get("success", False),
                response_data=result.get("data", {}),
                error_message=result.get("error")
            )
            
            # Log compliance audit for request completion
            log_compliance_audit(
                action="inference_request_complete",
                user_id=request["user_id"],
                request_id=request_id,
                compliance_status="COMPLIANT" if result.get("success", False) else "NON_COMPLIANT",
                details={
                    "request_type": request_type,
                    "priority": request["priority"],
                    "success": result.get("success", False),
                    "processing_time_ms": total_processing_time_ms,
                    "retry_count": retry_count
                }
            )
            
            # Update stats
            self._update_stats(result.get("processing_time_ms", 0), result.get("success", False))
            
            # Log completion
            if result.get("success"):
                logger.info(
                    "Request completed successfully",
                    request_id=request_id,
                    processing_time_ms=result.get("processing_time_ms", 0)
                )
            else:
                logger.error(
                    "Request failed after all retries",
                    request_id=request_id,
                    error=result.get("error", "Unknown error"),
                    processing_time_ms=result.get("processing_time_ms", 0)
                )
                
        except Exception as e:
            logger.error("Error in _process_inference_request", error=str(e), exc_info=True)
    
    async def _process_chat_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat/analysis request using the chat agent."""
        request_id = request["request_id"]
        
        try:
            # Extract request data with error handling
            if "input_data" not in request:
                logger.error("Missing input_data field in request", request_id=request_id, request_keys=list(request.keys()))
                return {
                    "success": False,
                    "error": "Missing input_data field in request",
                    "processing_time_ms": 0
                }
            
            if not request["input_data"]:
                logger.error("Empty input_data field in request", request_id=request_id)
                return {
                    "success": False,
                    "error": "Empty input_data field in request", 
                    "processing_time_ms": 0
                }
            
            try:
                request_data = json.loads(request["input_data"])
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON in input_data", request_id=request_id, error=str(e), input_data=request["input_data"])
                return {
                    "success": False,
                    "error": f"Invalid JSON in input_data: {str(e)}",
                    "processing_time_ms": 0
                }
            
            # Get GPU resource for processing
            async with self._gpu_resource() as gpu_acquired:
                if not gpu_acquired:
                    return {
                        "success": False,
                        "error": "GPU resource timeout - system overloaded",
                        "processing_time_ms": 0
                    }
                
                # Process with chat agent
                start_time = datetime.utcnow()
                
                # Extract required fields from request_data
                message_id = request_data.get("message_id", request["message_id"])
                custom_gpt_id = request_data.get("custom_gpt_id", request.get("custom_gpt_id"))
                user_message = request_data.get("user_message", "")
                context_messages = request_data.get("context_messages", [])
                attachments = request_data.get("attachments", [])
                
                # For now, create a minimal custom_gpt config - this should come from DB in the future
                custom_gpt = {
                    "id": custom_gpt_id,
                    "user_id": request["user_id"],  # Include user_id from request
                    "specialization": "general",
                    "compliance_level": "sec_compliant"
                }
                
                # Generate a thread_id if not present
                thread_id = request_data.get("thread_id", f"thread_{message_id}")
                
                result = await self.chat_agent.process_chat(
                    message_id=message_id,
                    thread_id=thread_id,
                    custom_gpt=custom_gpt,
                    user_message=user_message,
                    context_messages=context_messages,
                    attachments=attachments
                )
                
                processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                result["processing_time_ms"] = processing_time_ms
                
                # Create thread if it doesn't exist before creating assistant message
                if result.get("success", False) and result.get("content"):
                    # Ensure user exists first
                    user_created = await self.db_service.create_user_if_not_exists(
                        user_id=request["user_id"],
                        email=f"{request['user_id']}@bakergroup.com",
                        display_name=f"Auto User {request['user_id'][:8]}"
                    )
                    
                    if not user_created:
                        logger.warning(
                            "Failed to create/verify user",
                            request_id=request_id,
                            user_id=request["user_id"]
                        )
                    
                    # Ensure custom GPT exists
                    custom_gpt_created = await self.db_service.create_custom_gpt_if_not_exists(
                        custom_gpt_id=custom_gpt_id,
                        name=f"Auto-generated {custom_gpt.get('specialization', 'General')} GPT",
                        description=f"Automatically generated Custom GPT for {custom_gpt.get('specialization', 'general')} tasks",
                        system_prompt=f"You are a helpful {custom_gpt.get('specialization', 'general')} assistant.",
                        specialization=custom_gpt.get('specialization', 'general'),
                        user_id=request["user_id"]
                    )
                    
                    if not custom_gpt_created:
                        logger.warning(
                            "Failed to create/verify custom GPT",
                            request_id=request_id,
                            custom_gpt_id=custom_gpt_id
                        )
                    
                    # Ensure thread exists before creating message
                    thread_created = await self.db_service.create_thread_if_not_exists(
                        thread_id=thread_id,
                        title=f"Chat with {custom_gpt.get('specialization', 'AI Assistant')}",
                        custom_gpt_id=custom_gpt_id,
                        user_id=request["user_id"],
                        client_id=None  # Can be extracted from request if needed
                    )
                    
                    if not thread_created:
                        logger.warning(
                            "Failed to create/verify thread",
                            request_id=request_id,
                            thread_id=thread_id
                        )
                        # Continue anyway - the thread might exist but we couldn't verify it
                    
                    # Create assistant message in database if chat processing was successful
                    try:
                        assistant_message_id = await self.db_service.create_assistant_message(
                            thread_id=thread_id,
                            content=result["content"],
                            custom_gpt_id=custom_gpt_id,
                            user_id=request["user_id"],
                            confidence_score=result.get("confidence_score"),
                            model_used=result.get("model_used"),
                            processing_time_ms=processing_time_ms,
                            compliance_flags=result.get("compliance_flags", []),
                            sec_compliant=result.get("sec_compliant", True),
                            human_review_required=result.get("human_review_required", False)
                        )
                        
                        if assistant_message_id:
                            logger.info(
                                "Assistant message created successfully",
                                request_id=request_id,
                                thread_id=thread_id,
                                assistant_message_id=assistant_message_id,
                                processing_time_ms=processing_time_ms
                            )
                            result["assistant_message_id"] = assistant_message_id
                        else:
                            logger.warning(
                                "Failed to create assistant message",
                                request_id=request_id,
                                thread_id=thread_id
                            )
                    except Exception as e:
                        logger.error(
                            "Error creating assistant message",
                            request_id=request_id,
                            thread_id=thread_id,
                            error=str(e),
                            exc_info=True
                        )
                        # Don't fail the entire request if message creation fails
                
                return result
                
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid request data format: {str(e)}",
                "processing_time_ms": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Chat processing failed: {str(e)}",
                "processing_time_ms": 0
            }
    
    @asynccontextmanager
    async def _gpu_resource(self):
        """Context manager for GPU resource acquisition."""
        acquired = False
        try:
            # Try to acquire GPU resource with timeout
            acquired = await self.gpu_manager.acquire_resource(
                timeout=self.settings.service.gpu_timeout_seconds
            )
            yield acquired
        finally:
            if acquired:
                await self.gpu_manager.release_resource()
    
    def _update_stats(self, processing_time_ms: int, success: bool) -> None:
        """Update performance statistics."""
        self.stats["requests_processed"] += 1
        if success:
            self.stats["requests_successful"] += 1
        
        self.stats["total_processing_time_ms"] += processing_time_ms
        
        if self.stats["requests_processed"] > 0:
            self.stats["average_processing_time_ms"] = (
                self.stats["total_processing_time_ms"] // self.stats["requests_processed"]
            )
    
    async def _log_health_metrics(self) -> None:
        """Log service health and performance metrics."""
        if not self.start_time:
            return
        
        uptime_seconds = int((datetime.utcnow() - self.start_time).total_seconds())
        success_rate = 0.0
        
        if self.stats["requests_processed"] > 0:
            success_rate = self.stats["requests_successful"] / self.stats["requests_processed"]
        
        log_performance_metric(
            metric_type="service_health_check",
            value=uptime_seconds * 1000,
            unit="ms",
            context={
                "uptime_seconds": uptime_seconds,
                "requests_processed": self.stats["requests_processed"],
                "requests_successful": self.stats["requests_successful"],
                "success_rate": success_rate,
                "average_processing_time_ms": self.stats["average_processing_time_ms"],
                "gpu_available": await self.gpu_manager.is_available()
            }
        )
        
        logger.info(
            "Service health metrics",
            uptime_seconds=uptime_seconds,
            requests_processed=self.stats["requests_processed"],
            success_rate=success_rate,
            average_processing_time_ms=self.stats["average_processing_time_ms"]
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current service statistics."""
        stats = self.stats.copy()
        
        if self.start_time:
            stats["uptime_seconds"] = int((datetime.utcnow() - self.start_time).total_seconds())
        
        return stats


async def run_inference_service() -> None:
    """
    Main entry point for running the inference service.
    
    Initializes configuration, creates the service instance, and runs the main loop
    with proper error handling and cleanup.
    """
    settings = InferenceSettings()
    service = InferenceService(settings)
    
    try:
        logger.info("Starting Baker Compliant AI Inference Service")
        
        # Initialize all components
        await service.initialize()
        
        # Start the main service loop
        await service.start()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping service")
    except Exception as e:
        logger.critical("Inference service startup failed", error=str(e), exc_info=True)
        raise
    finally:
        # Ensure cleanup
        try:
            await service.stop()
        except Exception as e:
            logger.error("Error during service cleanup", error=str(e), exc_info=True)
        
        logger.info("Baker Compliant AI Inference Service shutdown complete")


if __name__ == "__main__":
    asyncio.run(run_inference_service())