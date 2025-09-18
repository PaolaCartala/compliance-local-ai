"""
Health check service for monitoring all system components.

This service provides comprehensive health monitoring for all Baker Compliant AI
system components including database, AI models, queue system, file storage,
and external MCP services.
"""

import asyncio
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models.schemas import ServiceStatus, ServiceHealthDetail
from api.src.services.database_adapter import db_adapter
from api.src.utils.config import get_settings
from api.src.utils.logging import logger


class HealthService:
    """Comprehensive health monitoring service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logger
    
    async def check_database_health(self) -> ServiceHealthDetail:
        """Check database service health."""
        start_time = time.time()
        
        try:
            health_data = await db_adapter.health_check()
            response_time = (time.time() - start_time) * 1000
            
            if health_data["status"] == "healthy":
                return ServiceHealthDetail(
                    status=ServiceStatus.HEALTHY,
                    message="Database connection successful",
                    response_time_ms=response_time,
                    details={
                        "tables": health_data.get("tables", 0),
                        "database_path": health_data.get("database_path"),
                        "connection": health_data.get("connection")
                    }
                )
            else:
                return ServiceHealthDetail(
                    status=ServiceStatus.UNHEALTHY,
                    message=f"Database error: {health_data.get('error', 'Unknown error')}",
                    response_time_ms=response_time,
                    details=health_data
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error("Database health check failed", error=str(e))
            return ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)}
            )
    
    async def check_ollama_health(self) -> ServiceHealthDetail:
        """Check Ollama AI service health."""
        start_time = time.time()
        
        try:
            # Use Python's http client instead of external commands for better reliability
            import urllib.request
            import urllib.error
            
            try:
                with urllib.request.urlopen(
                    f"{self.settings.ollama_base_url}/api/tags", 
                    timeout=10
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        models = data.get("models", [])
                        
                        # Check if required models are available
                        model_names = [model.get("name", "") for model in models]
                        chat_model_available = any(self.settings.ollama_chat_model in name for name in model_names)
                        vision_model_available = any(self.settings.ollama_vision_model in name for name in model_names)
                        
                        if chat_model_available and vision_model_available:
                            status = ServiceStatus.HEALTHY
                            message = "Ollama service running with required models"
                        elif chat_model_available or vision_model_available:
                            status = ServiceStatus.DEGRADED
                            message = "Ollama service running but missing some required models"
                        else:
                            status = ServiceStatus.DEGRADED
                            message = "Ollama service running but required models not found"
                        
                        return ServiceHealthDetail(
                            status=status,
                            message=message,
                            response_time_ms=response_time,
                            details={
                                "models_count": len(models),
                                "chat_model_available": chat_model_available,
                                "vision_model_available": vision_model_available,
                                "required_chat_model": self.settings.ollama_chat_model,
                                "required_vision_model": self.settings.ollama_vision_model,
                                "available_models": model_names[:5]  # Limit for brevity
                            }
                        )
                    else:
                        return ServiceHealthDetail(
                            status=ServiceStatus.UNHEALTHY,
                            message=f"Ollama service returned status {response.status}",
                            response_time_ms=response_time,
                            details={"status_code": response.status}
                        )
            
            except urllib.error.URLError as e:
                response_time = (time.time() - start_time) * 1000
                return ServiceHealthDetail(
                    status=ServiceStatus.UNHEALTHY,
                    message=f"Ollama service connection failed: {str(e)}",
                    response_time_ms=response_time,
                    details={"error": str(e)}
                )
            except json.JSONDecodeError as e:
                response_time = (time.time() - start_time) * 1000
                return ServiceHealthDetail(
                    status=ServiceStatus.DEGRADED,
                    message="Ollama service responding but invalid JSON",
                    response_time_ms=response_time,
                    details={"json_error": str(e)}
                )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error("Ollama health check failed", error=str(e))
            return ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"Ollama service error: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)}
            )
    
    async def check_queue_health(self) -> ServiceHealthDetail:
        """Check message queue health."""
        start_time = time.time()
        
        try:
            async with db_adapter.get_session() as session:
                # Check queue depth
                queue_depth_result = await session.execute(
                    text("SELECT COUNT(*) FROM inference_queue WHERE status = 'pending'")
                )
                pending_count = queue_depth_result.scalar() or 0
                
                # Check processing count
                processing_result = await session.execute(
                    text("SELECT COUNT(*) FROM inference_queue WHERE status = 'processing'")
                )
                processing_count = processing_result.scalar() or 0
                
                # Check failed count in last hour
                failed_result = await session.execute(
                    text("""
                        SELECT COUNT(*) FROM inference_queue 
                        WHERE status = 'failed' 
                        AND created_at > datetime('now', '-1 hour')
                    """)
                )
                failed_count = failed_result.scalar() or 0
                
                response_time = (time.time() - start_time) * 1000
                
                # Determine status based on queue metrics
                if failed_count > 10:
                    status = ServiceStatus.UNHEALTHY
                    message = f"High failure rate: {failed_count} failed jobs in last hour"
                elif pending_count > 100:
                    status = ServiceStatus.DEGRADED
                    message = f"High queue depth: {pending_count} pending jobs"
                else:
                    status = ServiceStatus.HEALTHY
                    message = "Queue operating normally"
                
                return ServiceHealthDetail(
                    status=status,
                    message=message,
                    response_time_ms=response_time,
                    details={
                        "pending_jobs": pending_count,
                        "processing_jobs": processing_count,
                        "failed_jobs_last_hour": failed_count,
                        "total_queue_depth": pending_count + processing_count
                    }
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error("Queue health check failed", error=str(e))
            return ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"Queue check failed: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)}
            )
    
    async def check_file_storage_health(self) -> ServiceHealthDetail:
        """Check file storage health."""
        start_time = time.time()
        
        try:
            storage_path = self.settings.get_file_storage_path()
            
            # Check if storage directory exists and is writable
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)
            
            # Test write permission
            test_file = storage_path / ".health_check"
            test_file.write_text("health_check")
            test_file.unlink()
            
            response_time = (time.time() - start_time) * 1000
            
            # Try to get disk usage if psutil is available
            try:
                import psutil
                disk_usage = psutil.disk_usage(str(storage_path))
                free_space_gb = disk_usage.free / (1024**3)
                usage_percent = (disk_usage.used / disk_usage.total) * 100
                
                # Determine status based on available space
                if free_space_gb < 1:  # Less than 1GB free
                    status = ServiceStatus.UNHEALTHY
                    message = f"Critical: Only {free_space_gb:.2f}GB free space remaining"
                elif free_space_gb < 5:  # Less than 5GB free
                    status = ServiceStatus.DEGRADED
                    message = f"Warning: Only {free_space_gb:.2f}GB free space remaining"
                else:
                    status = ServiceStatus.HEALTHY
                    message = "File storage operating normally"
                
                return ServiceHealthDetail(
                    status=status,
                    message=message,
                    response_time_ms=response_time,
                    details={
                        "storage_path": str(storage_path),
                        "free_space_gb": round(free_space_gb, 2),
                        "total_space_gb": round(disk_usage.total / (1024**3), 2),
                        "usage_percent": round(usage_percent, 2),
                        "writable": True
                    }
                )
            except ImportError:
                # Fallback when psutil is not available
                return ServiceHealthDetail(
                    status=ServiceStatus.HEALTHY,
                    message="File storage accessible (disk metrics unavailable)",
                    response_time_ms=response_time,
                    details={
                        "storage_path": str(storage_path),
                        "writable": True,
                        "note": "psutil not available for disk usage metrics"
                    }
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error("File storage health check failed", error=str(e))
            return ServiceHealthDetail(
                status=ServiceStatus.UNHEALTHY,
                message=f"File storage check failed: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)}
            )
    
    async def check_mcp_services_health(self) -> Dict[str, ServiceHealthDetail]:
        """Check MCP services health."""
        mcp_services = {}
        
        # MCP services configuration (these would typically come from config)
        mcp_endpoints = {
            "redtail-crm": "http://localhost:8001",
            "albridge-portfolio": "http://localhost:8002",
            "black-diamond": "http://localhost:8003"
        }
        
        for service_name, endpoint in mcp_endpoints.items():
            start_time = time.time()
            
            try:
                import urllib.request
                import urllib.error
                
                health_url = f"{endpoint}/health" if not endpoint.endswith('/') else f"{endpoint}health"
                
                try:
                    with urllib.request.urlopen(health_url, timeout=5) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            mcp_services[service_name] = ServiceHealthDetail(
                                status=ServiceStatus.HEALTHY,
                                message=f"{service_name} MCP service is running",
                                response_time_ms=response_time,
                                details={"endpoint": endpoint}
                            )
                        else:
                            mcp_services[service_name] = ServiceHealthDetail(
                                status=ServiceStatus.DEGRADED,
                                message=f"{service_name} returned status {response.status}",
                                response_time_ms=response_time,
                                details={"endpoint": endpoint, "status_code": response.status}
                            )
                except urllib.error.URLError as e:
                    response_time = (time.time() - start_time) * 1000
                    mcp_services[service_name] = ServiceHealthDetail(
                        status=ServiceStatus.NOT_CONFIGURED,
                        message=f"{service_name} not available: {str(e)}",
                        response_time_ms=response_time,
                        details={"endpoint": endpoint, "error": str(e)}
                    )
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                mcp_services[service_name] = ServiceHealthDetail(
                    status=ServiceStatus.NOT_CONFIGURED,
                    message=f"{service_name} not available: {str(e)}",
                    response_time_ms=response_time,
                    details={"endpoint": endpoint, "error": str(e)}
                )
        
        return mcp_services
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            # Try to import psutil, fall back to basic metrics if not available
            try:
                import psutil
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # CPU usage (quick snapshot)
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                return {
                    "memory_usage_percent": round(memory_percent, 2),
                    "cpu_usage_percent": round(cpu_percent, 2),
                    "available_memory_gb": round(memory.available / (1024**3), 2),
                    "total_memory_gb": round(memory.total / (1024**3), 2)
                }
            except ImportError:
                # Fallback for when psutil is not available
                self.logger.warning("psutil not available, using basic system metrics")
                return {
                    "memory_usage_percent": None,
                    "cpu_usage_percent": None,
                    "available_memory_gb": None,
                    "total_memory_gb": None,
                    "note": "psutil not available for detailed metrics"
                }
        except Exception as e:
            self.logger.error("Failed to get system metrics", error=str(e))
            return {"error": str(e)}
    
    def determine_overall_status(self, service_statuses: Dict[str, ServiceStatus]) -> ServiceStatus:
        """Determine overall system status based on individual service statuses."""
        status_priority = {
            ServiceStatus.UNHEALTHY: 0,
            ServiceStatus.DEGRADED: 1,
            ServiceStatus.HEALTHY: 2,
            ServiceStatus.NOT_CONFIGURED: 3
        }
        
        # Get the worst status among core services (ignore NOT_CONFIGURED for MCP services)
        core_services = ["database", "ollama", "queue", "file_storage"]
        core_statuses = [service_statuses.get(service, ServiceStatus.UNHEALTHY) for service in core_services]
        
        if ServiceStatus.UNHEALTHY in core_statuses:
            return ServiceStatus.UNHEALTHY
        elif ServiceStatus.DEGRADED in core_statuses:
            return ServiceStatus.DEGRADED
        else:
            return ServiceStatus.HEALTHY


# Global health service instance
health_service = HealthService()