"""
Health check router for monitoring API service status.
"""

import asyncio
from datetime import datetime
from fastapi import APIRouter
from api.src.models.schemas import HealthCheck, ServiceHealthDetail, ServiceStatus, APIResponse
from api.src.services.health_service import health_service
from api.src.utils.config import get_settings
from api.src.utils.logging import logger

router = APIRouter()

@router.get("/", response_model=HealthCheck)
async def comprehensive_health_check() -> HealthCheck:
    """
    Comprehensive health check endpoint that verifies all system components.
    
    Checks database, Ollama AI service, message queue, file storage, and MCP services.
    Returns detailed status for each component plus overall system status.
    """
    settings = get_settings()
    
    # Run all health checks concurrently for better performance
    database_task = health_service.check_database_health()
    ollama_task = health_service.check_ollama_health()
    queue_task = health_service.check_queue_health()
    storage_task = health_service.check_file_storage_health()
    mcp_task = health_service.check_mcp_services_health()
    
    # Wait for all checks to complete
    database_health, ollama_health, queue_health, storage_health, mcp_services_health = await asyncio.gather(
        database_task, ollama_task, queue_task, storage_task, mcp_task,
        return_exceptions=True
    )
    
    # Handle any exceptions in health checks
    if isinstance(database_health, Exception):
        logger.error("Database health check exception", error=str(database_health))
        database_health = ServiceHealthDetail(
            status=ServiceStatus.UNHEALTHY,
            message=f"Health check failed: {str(database_health)}"
        )
    
    if isinstance(ollama_health, Exception):
        logger.error("Ollama health check exception", error=str(ollama_health))
        ollama_health = ServiceHealthDetail(
            status=ServiceStatus.UNHEALTHY,
            message=f"Health check failed: {str(ollama_health)}"
        )
    
    if isinstance(queue_health, Exception):
        logger.error("Queue health check exception", error=str(queue_health))
        queue_health = ServiceHealthDetail(
            status=ServiceStatus.UNHEALTHY,
            message=f"Health check failed: {str(queue_health)}"
        )
    
    if isinstance(storage_health, Exception):
        logger.error("Storage health check exception", error=str(storage_health))
        storage_health = ServiceHealthDetail(
            status=ServiceStatus.UNHEALTHY,
            message=f"Health check failed: {str(storage_health)}"
        )
    
    if isinstance(mcp_services_health, Exception):
        logger.error("MCP services health check exception", error=str(mcp_services_health))
        mcp_services_health = {}
    
    # Determine overall system status
    service_statuses = {
        "database": database_health.status,
        "ollama": ollama_health.status,
        "queue": queue_health.status,
        "file_storage": storage_health.status
    }
    
    overall_status = health_service.determine_overall_status(service_statuses)
    
    # Get system metrics
    system_metrics = health_service.get_system_metrics()
    
    # Get queue depth for legacy compatibility
    queue_depth = queue_health.details.get("total_queue_depth", 0) if queue_health.details else 0
    
    return HealthCheck(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.api_version,
        database=database_health,
        ollama=ollama_health,
        queue=queue_health,
        file_storage=storage_health,
        mcp_services=mcp_services_health,
        queue_depth=queue_depth,
        memory_usage_percent=system_metrics.get("memory_usage_percent"),
        # Legacy fields for backwards compatibility
        database_status=database_health.status.value,
        ollama_status=ollama_health.status.value,
        gpu_utilization=None  # Could be added later with nvidia-ml-py
    )


@router.get("/database", response_model=APIResponse[ServiceHealthDetail])
async def database_health_check():
    """Check database service health specifically."""
    try:
        health_detail = await health_service.check_database_health()
        return APIResponse(
            success=health_detail.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED],
            data=health_detail,
            message=health_detail.message
        )
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return APIResponse(
            success=False,
            data=ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"Database health check failed: {str(e)}"
            ),
            message="Health check failed"
        )


@router.get("/ollama", response_model=APIResponse[ServiceHealthDetail])
async def ollama_health_check():
    """Check Ollama AI service health specifically."""
    try:
        health_detail = await health_service.check_ollama_health()
        return APIResponse(
            success=health_detail.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED],
            data=health_detail,
            message=health_detail.message
        )
    except Exception as e:
        logger.error("Ollama health check failed", error=str(e))
        return APIResponse(
            success=False,
            data=ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"Ollama health check failed: {str(e)}"
            ),
            message="Health check failed"
        )


@router.get("/queue", response_model=APIResponse[ServiceHealthDetail])
async def queue_health_check():
    """Check message queue health specifically."""
    try:
        health_detail = await health_service.check_queue_health()
        return APIResponse(
            success=health_detail.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED],
            data=health_detail,
            message=health_detail.message
        )
    except Exception as e:
        logger.error("Queue health check failed", error=str(e))
        return APIResponse(
            success=False,
            data=ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"Queue health check failed: {str(e)}"
            ),
            message="Health check failed"
        )


@router.get("/storage", response_model=APIResponse[ServiceHealthDetail])
async def storage_health_check():
    """Check file storage health specifically."""
    try:
        health_detail = await health_service.check_file_storage_health()
        return APIResponse(
            success=health_detail.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED],
            data=health_detail,
            message=health_detail.message
        )
    except Exception as e:
        logger.error("Storage health check failed", error=str(e))
        return APIResponse(
            success=False,
            data=ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"Storage health check failed: {str(e)}"
            ),
            message="Health check failed"
        )


@router.get("/mcp", response_model=APIResponse[dict])
async def mcp_services_health_check():
    """Check all MCP services health specifically."""
    try:
        mcp_health = await health_service.check_mcp_services_health()
        
        # Determine if all MCP services are healthy
        all_healthy = all(
            service.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED, ServiceStatus.NOT_CONFIGURED]
            for service in mcp_health.values()
        )
        
        return APIResponse(
            success=all_healthy,
            data=mcp_health,
            message="MCP services health check completed"
        )
    except Exception as e:
        logger.error("MCP services health check failed", error=str(e))
        return APIResponse(
            success=False,
            data={},
            message=f"MCP services health check failed: {str(e)}"
        )
