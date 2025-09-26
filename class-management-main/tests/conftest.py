"""
Pytest configuration and fixtures for Class Management System tests.

This module provides shared fixtures and configuration for unit and integration tests.
"""

import os
import asyncio
from typing import Generator, AsyncGenerator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from motor.motor_asyncio import AsyncIOMotorClient

# Import application components
from backend.main import app
from backend.core.config import Settings, get_settings
from backend.data.models import Base
from backend.data.database import get_db, get_sqlite_db


# Test settings
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings configuration."""
    return Settings(
        app_env="testing",
        database_type="sqlite",
        sqlite_database_url="sqlite:///./test_class_management.db",
        sqlite_echo=False,
        mongodb_url="mongodb://localhost:27017",
        mongodb_database_name="test_class_management",
        jwt_secret_key="test-secret-key",
        secret_key="test-app-secret-key"
    )


# Database fixtures
@pytest.fixture(scope="session")
def test_engine(test_settings: Settings):
    """Create test database engine."""
    engine = create_engine(
        test_settings.sqlite_database_url,
        connect_args={"check_same_thread": False},
        echo=test_settings.sqlite_echo
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup: Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Remove test database file
    db_file = test_settings.sqlite_database_url.replace("sqlite:///", "")
    if os.path.exists(db_file):
        os.remove(db_file)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session, test_settings: Settings) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    
    def override_get_db():
        """Override database dependency for testing."""
        try:
            yield db_session
        finally:
            pass
    
    def override_get_settings():
        """Override settings dependency for testing."""
        return test_settings
    
    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_sqlite_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()


# MongoDB fixtures (for MongoDB tests)
@pytest.fixture(scope="session")
async def mongodb_client(test_settings: Settings) -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create test MongoDB client."""
    client = AsyncIOMotorClient(test_settings.mongodb_url)
    
    try:
        # Test connection
        await client.admin.command('ping')
        yield client
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")
    finally:
        client.close()


@pytest.fixture(scope="function")
async def mongodb_database(mongodb_client: AsyncIOMotorClient, test_settings: Settings):
    """Create test MongoDB database."""
    database = mongodb_client[test_settings.mongodb_database_name]
    
    yield database
    
    # Cleanup: Drop test database
    await mongodb_client.drop_database(test_settings.mongodb_database_name)


# Sample data fixtures
@pytest.fixture
def sample_student_data() -> dict:
    """Provide sample student data for tests."""
    return {
        "student_id": "TEST001",
        "first_name": "Test",
        "last_name": "Student",
        "email": "test.student@example.com",
        "phone": "+1-555-0123",
        "date_of_birth": "2000-01-01",
        "address": "123 Test St, Test City, TC 12345"
    }


@pytest.fixture
def sample_student_data_invalid() -> dict:
    """Provide invalid student data for negative tests."""
    return {
        "student_id": "",  # Invalid: empty
        "first_name": "",  # Invalid: empty
        "last_name": "Student",
        "email": "invalid-email",  # Invalid: not an email
        "phone": "+1-555-0123",
        "date_of_birth": "invalid-date",  # Invalid: not a date
        "address": "123 Test St, Test City, TC 12345"
    }


# Async event loop fixture
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Authentication fixtures (for future use)
@pytest.fixture
def auth_headers() -> dict:
    """Provide authentication headers for API tests."""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


# Mock fixtures
@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime for consistent testing."""
    import datetime
    from unittest.mock import Mock
    
    mock_now = datetime.datetime(2024, 1, 1, 12, 0, 0)
    mock_date = datetime.date(2024, 1, 1)
    
    datetime_mock = Mock(wraps=datetime.datetime)
    datetime_mock.utcnow.return_value = mock_now
    datetime_mock.now.return_value = mock_now
    
    date_mock = Mock(wraps=datetime.date)
    date_mock.today.return_value = mock_date
    
    monkeypatch.setattr("datetime.datetime", datetime_mock)
    monkeypatch.setattr("datetime.date", date_mock)
    
    return {"datetime": mock_now, "date": mock_date}


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.end_time - self.start_time
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Database cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_database(db_session: Session):
    """Automatically cleanup database after each test."""
    yield
    
    # Rollback any uncommitted transactions
    db_session.rollback()
    
    # Clean up all data
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "db: Database tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "mock: Tests with mocking")