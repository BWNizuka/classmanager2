"""
Configuration management for the Class Management System.

This module loads and validates environment variables using Pydantic settings,
providing centralized configuration management for the application.
"""

import os
from typing import List, Optional
from pathlib import Path
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic BaseSettings to automatically load and validate
    environment variables with type conversion and default values.
    """
    
    # =============================================================================
    # APPLICATION CONFIGURATION
    # =============================================================================
    
    app_env: str = "development"
    app_name: str = "Class Management System"
    app_version: str = "1.0.0"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ]
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret_key: str = "dev-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    
    # Primary database type
    database_type: str = "sqlite"  # sqlite or mongodb
    
    # SQLite Configuration
    sqlite_database_url: str = "sqlite:///./class_management.db"
    sqlite_echo: bool = False
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database_name: str = "class_management"
    mongodb_min_connections: int = 10
    mongodb_max_connections: int = 100
    mongodb_max_idle_time_ms: int = 30000
    mongodb_username: Optional[str] = None
    mongodb_password: Optional[str] = None
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: Optional[str] = None
    
    # =============================================================================
    # EXTERNAL SERVICES
    # =============================================================================
    
    # Email Configuration
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_from_address: str = "noreply@classmanagement.com"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    
    # =============================================================================
    # FRONTEND CONFIGURATION
    # =============================================================================
    
    streamlit_server_port: int = 8501
    streamlit_server_address: str = "localhost"
    backend_api_url: str = "http://localhost:8000"
    
    # =============================================================================
    # DEVELOPMENT/TESTING
    # =============================================================================
    
    test_database_url: str = "sqlite:///./test_class_management.db"
    enable_docs: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    enable_reload: bool = True
    enable_debug_toolbar: bool = False
    
    # =============================================================================
    # VALIDATORS
    # =============================================================================
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('database_type')
    def validate_database_type(cls, v):
        """Validate database type is supported."""
        allowed_types = ['sqlite', 'mongodb']
        if v.lower() not in allowed_types:
            raise ValueError(f'Database type must be one of: {allowed_types}')
        return v.lower()
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {allowed_levels}')
        return v.upper()
    
    @validator('mongodb_url')
    def validate_mongodb_url(cls, v):
        """Validate MongoDB URL format."""
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError('MongoDB URL must start with mongodb:// or mongodb+srv://')
        return v
    
    # =============================================================================
    # COMPUTED PROPERTIES
    # =============================================================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == 'development'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == 'production'
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.app_env.lower() == 'testing'
    
    @property
    def database_url(self) -> str:
        """Get the appropriate database URL based on database type."""
        if self.database_type == 'sqlite':
            return self.sqlite_database_url
        elif self.database_type == 'mongodb':
            return self.mongodb_url
        else:
            raise ValueError(f'Unsupported database type: {self.database_type}')
    
    @property
    def mongodb_connection_string(self) -> str:
        """Get MongoDB connection string with authentication if provided."""
        if self.mongodb_username and self.mongodb_password:
            # Replace mongodb:// with credentials
            if self.mongodb_url.startswith('mongodb://'):
                return self.mongodb_url.replace(
                    'mongodb://',
                    f'mongodb://{self.mongodb_username}:{self.mongodb_password}@'
                )
            elif self.mongodb_url.startswith('mongodb+srv://'):
                return self.mongodb_url.replace(
                    'mongodb+srv://',
                    f'mongodb+srv://{self.mongodb_username}:{self.mongodb_password}@'
                )
        return self.mongodb_url
    
    # =============================================================================
    # METHODS
    # =============================================================================
    
    def create_log_directory(self) -> None:
        """Create log directory if log file path is specified."""
        if self.log_file_path:
            log_dir = Path(self.log_file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_database_config(self) -> dict:
        """Get database configuration based on selected database type."""
        if self.database_type == 'sqlite':
            return {
                'type': 'sqlite',
                'url': self.sqlite_database_url,
                'echo': self.sqlite_echo
            }
        elif self.database_type == 'mongodb':
            return {
                'type': 'mongodb',
                'url': self.mongodb_connection_string,
                'database_name': self.mongodb_database_name,
                'min_connections': self.mongodb_min_connections,
                'max_connections': self.mongodb_max_connections,
                'max_idle_time_ms': self.mongodb_max_idle_time_ms
            }
        else:
            raise ValueError(f'Unsupported database type: {self.database_type}')
    
    class Config:
        """Pydantic configuration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Map environment variable names to field names
        fields = {
            'cors_origins': 'CORS_ORIGINS',
            'secret_key': 'SECRET_KEY',
            'jwt_secret_key': 'JWT_SECRET_KEY',
            'jwt_algorithm': 'JWT_ALGORITHM',
            'jwt_access_token_expire_minutes': 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES'
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings instance.
    
    Returns:
        Settings: Application settings loaded from environment variables
    """
    return settings


def load_settings(env_file: Optional[str] = None) -> Settings:
    """
    Load settings from specified environment file.
    
    Args:
        env_file (Optional[str]): Path to environment file
        
    Returns:
        Settings: Loaded application settings
    """
    if env_file:
        return Settings(_env_file=env_file)
    return Settings()


# Initialize logging directory on import
settings.create_log_directory()