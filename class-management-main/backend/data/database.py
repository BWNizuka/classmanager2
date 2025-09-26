"""
Database configuration and session management.

This module handles database setup for both SQLite and MongoDB,
providing a unified interface for database operations based on configuration.
"""

from typing import Union, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import Base, get_database_url, create_database_engine, create_session_factory
from .mongo_connection import get_mongo_db, init_mongodb, close_mongodb, mongo_connection
from ..core.config import settings


# SQLite Configuration
def get_sqlite_config():
    """Get SQLite database configuration."""
    DATABASE_URL = settings.sqlite_database_url
    engine = create_database_engine(DATABASE_URL, echo=settings.sqlite_echo)
    SessionLocal = create_session_factory(engine)
    return engine, SessionLocal


# Initialize SQLite components
sqlite_engine, SQLiteSessionLocal = get_sqlite_config()


def init_sqlite_database() -> None:
    """
    Initialize SQLite database by creating all tables.
    
    This function creates all database tables defined in the models
    if they don't already exist.
    """
    Base.metadata.create_all(bind=sqlite_engine)


def get_sqlite_db() -> Session:
    """
    SQLite database session dependency for FastAPI.
    
    Creates a new database session for each request and ensures
    it's properly closed after the request is completed.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SQLiteSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_mongodb_db() -> AsyncIOMotorDatabase:
    """
    MongoDB database dependency for FastAPI.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    return await get_mongo_db()


def get_db() -> Union[Session, AsyncIOMotorDatabase]:
    """
    Universal database dependency that returns the appropriate database session
    based on the configured database type.
    
    Returns:
        Union[Session, AsyncIOMotorDatabase]: Database session/connection
    """
    if settings.database_type == 'sqlite':
        return get_sqlite_db()
    elif settings.database_type == 'mongodb':
        # Note: For MongoDB, this would need to be an async dependency
        # This is a simplified version for compatibility
        raise NotImplementedError(
            "MongoDB requires async dependencies. Use get_mongodb_db() directly in async routes."
        )
    else:
        raise ValueError(f"Unsupported database type: {settings.database_type}")


async def init_database() -> None:
    """
    Initialize database based on configured database type.
    
    Creates tables/collections and indexes as needed.
    """
    if settings.database_type == 'sqlite':
        init_sqlite_database()
        print(f"✅ SQLite database initialized: {settings.sqlite_database_url}")
    
    elif settings.database_type == 'mongodb':
        await init_mongodb()
        print(f"✅ MongoDB database initialized: {settings.mongodb_database_name}")
    
    else:
        raise ValueError(f"Unsupported database type: {settings.database_type}")


async def close_database() -> None:
    """
    Close database connections based on configured database type.
    """
    if settings.database_type == 'mongodb':
        await close_mongodb()
        print("📤 Database connections closed")


class DatabaseManager:
    """
    Database manager that provides a unified interface for different database types.
    
    This class abstracts the differences between SQLite and MongoDB operations.
    """
    
    def __init__(self):
        """Initialize database manager."""
        self.db_type = settings.database_type
    
    async def initialize(self) -> None:
        """Initialize the configured database."""
        await init_database()
    
    async def close(self) -> None:
        """Close database connections."""
        await close_database()
    
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.db_type == 'sqlite'
    
    def is_mongodb(self) -> bool:
        """Check if using MongoDB database."""
        return self.db_type == 'mongodb'
    
    def get_session_dependency(self):
        """
        Get the appropriate database session dependency.
        
        Returns:
            Callable: Database session dependency function
        """
        if self.is_sqlite():
            return get_sqlite_db
        elif self.is_mongodb():
            return get_mongodb_db
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


# Global database manager instance
db_manager = DatabaseManager()