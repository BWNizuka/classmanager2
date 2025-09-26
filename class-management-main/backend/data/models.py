"""
Data layer models for Class Management System.

This module defines the database models using SQLAlchemy ORM for SQLite database.
Includes Student model for managing student information.
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# SQLAlchemy base class for model definitions
Base = declarative_base()


class Student(Base):
    """
    Student model representing a student in the class management system.
    
    Attributes:
        id (int): Primary key, auto-incrementing student ID
        student_id (str): Unique student identifier/code (required, max 20 characters)
        first_name (str): Student's first name (required, max 50 characters)
        last_name (str): Student's last name (required, max 50 characters)
        email (str): Student's email address (required, unique, max 100 characters)
        phone (str): Student's phone number (optional, max 20 characters)
        date_of_birth (date): Student's date of birth (optional)
        address (str): Student's address (optional, max 200 characters)
        enrollment_date (date): Date when student was enrolled (auto-generated)
        created_at (datetime): Timestamp when record was created (auto-generated)
        updated_at (datetime): Timestamp when record was last updated (auto-updated)
    """
    
    __tablename__ = "students"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Required student information
    student_id = Column(String(20), nullable=False, unique=True, index=True)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    
    # Optional student information
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String(200), nullable=True)
    
    # Enrollment information
    enrollment_date = Column(Date, nullable=False, default=date.today)
    
    # Timestamps for audit trail
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now()
    )
    
    def __repr__(self) -> str:
        """
        String representation of Student model.
        
        Returns:
            str: Human-readable representation of the Student instance
        """
        return (
            f"<Student(id={self.id}, student_id='{self.student_id}', "
            f"name='{self.first_name} {self.last_name}', email='{self.email}')>"
        )
    
    @property
    def full_name(self) -> str:
        """
        Get student's full name.
        
        Returns:
            str: Concatenated first and last name
        """
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """
        Convert Student model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the Student instance
        """
        return {
            "id": self.id,
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "address": self.address,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


def get_database_url(db_path: str = "class_management.db") -> str:
    """
    Generate SQLite database URL.
    
    Args:
        db_path (str): Path to SQLite database file
        
    Returns:
        str: SQLAlchemy database URL for SQLite
    """
    return f"sqlite:///{db_path}"


def create_database_engine(database_url: str, echo: bool = False):
    """
    Create SQLAlchemy database engine.
    
    Args:
        database_url (str): Database connection URL
        echo (bool): Enable SQL query logging
        
    Returns:
        Engine: SQLAlchemy engine instance
    """
    return create_engine(
        database_url,
        echo=echo,
        # SQLite-specific configurations
        connect_args={"check_same_thread": False}  # Allow multi-threading
    )


def create_session_factory(engine):
    """
    Create SQLAlchemy session factory.
    
    Args:
        engine: SQLAlchemy engine instance
        
    Returns:
        sessionmaker: Session factory for creating database sessions
    """
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )


def create_tables(engine) -> None:
    """
    Create all database tables defined in models.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(bind=engine)