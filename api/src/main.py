"""
Main FastAPI application for Baker Compliant AI API Service.

This is the Backend-for-Frontend (BFF) service that handles HTTP requests,
validates input, manages authentication, and enqueues jobs to SQLite.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from api.src.routers import chat, threads, custom_gpts, health
from api.src.services.database import get_database_service
from api.src.utils.config import get_settings
from api.src.utils.logging import logger, audit_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    
    # Initialize database
    db_service = get_database_service()
    await db_service.initialize()
    logger.info("Database initialized")
    
    # Store database service in app state
    app.state.db_service = db_service
    
    logger.info(
        "Baker Compliant AI API Service started",
        version=settings.api_version,
        environment=settings.environment.value,
        debug=settings.debug
    )
    
    yield
    
    # Cleanup
    await db_service.close()
    logger.info("Baker Compliant AI API Service stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="SEC-compliant AI chat API for financial advisory services",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan
    )
    
    # Middleware
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            allow_headers=["*"],
        )
    
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure with actual domains in production
        )
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler for unhandled errors."""
        logger.error(
            "Unhandled exception occurred",
            error=str(exc),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "errors": ["An unexpected error occurred"]
            }
        )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
    app.include_router(threads.router, prefix="/api/v1/threads", tags=["Threads"])
    app.include_router(custom_gpts.router, prefix="/api/v1/custom-gpts", tags=["Custom GPTs"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": "Baker Compliant AI API",
            "version": settings.api_version,
            "status": "operational",
            "docs_url": "/docs" if settings.is_development else None
        }
    
    return app


# Create app instance
app = create_app()