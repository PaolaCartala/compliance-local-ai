"""
Database service for Baker Compliant AI.

Manages SQLAlchemy setup, session management, and database operations
following the async pattern required for FastAPI.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from api.src.utils.config import get_settings
from api.src.utils.logging import logger


# Base class for all database models
Base = declarative_base()


class DatabaseService:
    """
    Database service for managing SQLAlchemy async connections.
    
    Handles database initialization, connection management, and session lifecycle.
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
        
        # Get absolute database path using settings method
        db_path = self.settings.get_database_path()
        async_database_url = f"sqlite+aiosqlite:///{db_path}"
        
        # Create async engine
        self.engine = create_async_engine(
            async_database_url,
            echo=self.settings.database_echo and self.settings.is_development,
            future=True,
        )
        
        # Create session maker
        self.async_session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        # Create tables (in production, use Alembic migrations)
        if self.settings.is_development:
            await self._create_tables()
        
        self._initialized = True
        logger.info(
            "Database service initialized",
            database_path=str(db_path),
            echo=self.settings.database_echo
        )
    
    async def _create_tables(self) -> None:
        """Create database tables for development."""
        try:
            # First, try to execute the schema.sql file if it exists
            import os
            schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database", "schema.sql")
            
            if os.path.exists(schema_path):
                await self._execute_sql_file(schema_path)
                logger.info("Database tables created from schema.sql")
            else:
                # Fallback to SQLAlchemy metadata creation
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created from SQLAlchemy metadata")
                
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e), exc_info=True)
            raise
    
    async def _execute_sql_file(self, file_path: str) -> None:
        """Execute SQL statements from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Use SQLite's executescript for complex SQL with triggers
            # This bypasses SQLAlchemy for schema creation
            import aiosqlite
            
            # Get absolute database path
            db_path = self.settings.get_database_path()
            
            async with aiosqlite.connect(db_path) as conn:
                await conn.executescript(sql_content)
                await conn.commit()
            
            logger.info("SQL file executed successfully using aiosqlite", file_path=file_path)
            
        except Exception as e:
            logger.error(
                "Failed to execute SQL file",
                file_path=file_path,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session as an async context manager.
        
        Yields:
            AsyncSession: Database session
        """
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            bool: True if database is accessible, False otherwise
        """
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False


# Global database service instance
_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get the global database service instance."""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session for FastAPI.
    
    Yields:
        AsyncSession: Database session for the request
    """
    db_service = get_database_service()
    async with db_service.get_session() as session:
        yield session


# Utility functions for direct database operations
async def migrate_database() -> None:
    """
    Run database migrations.
    
    In production, this should use Alembic. For development,
    we can use this to apply schema changes.
    """
    settings = get_settings()
    db_service = get_database_service()
    
    if settings.is_development:
        # Apply the enhanced inference queue schema
        try:
            queue_schema_path = settings.get_database_path().parent.parent / "frontend" / "database" / "enhanced_inference_queue.sql"
            if queue_schema_path.exists():
                await db_service._execute_sql_file(str(queue_schema_path))
                logger.info("Applied enhanced inference queue schema")
        except Exception as e:
            logger.warning("Could not apply queue schema", error=str(e))
    
    logger.info("Database migration completed")


# Background task for database maintenance
async def database_maintenance_task() -> None:
    """
    Background task for database maintenance.
    
    Handles cleanup of old records based on retention policies.
    """
    settings = get_settings()
    db_service = get_database_service()
    
    while True:
        try:
            async with db_service.get_session() as session:
                # Clean up old audit logs (older than retention period)
                retention_days = settings.audit_log_retention_days
                cleanup_date = f"datetime('now', '-{retention_days} days')"
                
                # Example cleanup query (adjust based on actual schema)
                await session.execute(text(f"""
                    DELETE FROM audit_trail_event_logs 
                    WHERE created_at < {cleanup_date}
                """))
                
                logger.info("Database maintenance completed", retention_days=retention_days)
        
        except Exception as e:
            logger.error("Database maintenance failed", error=str(e), exc_info=True)
        
        # Run maintenance daily
        await asyncio.sleep(86400)  # 24 hours