"""
MongoDB connection and configuration for Class Management System.

This module provides MongoDB connection management, document models,
and repository implementations for the student management system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import MongoClient
from beanie import Document, init_beanie
from pydantic import Field
import asyncio
from ..core.config import settings


class StudentDocument(Document):
    """
    MongoDB document model for Student.
    
    Uses Beanie ODM for async MongoDB operations with Pydantic validation.
    """
    
    student_id: str = Field(..., description="Unique student identifier")
    first_name: str = Field(..., description="Student's first name")
    last_name: str = Field(..., description="Student's last name")
    email: str = Field(..., description="Student's email address")
    phone: Optional[str] = Field(None, description="Student's phone number")
    date_of_birth: Optional[date] = Field(None, description="Student's date of birth")
    address: Optional[str] = Field(None, description="Student's address")
    enrollment_date: date = Field(default_factory=date.today, description="Enrollment date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @property
    def full_name(self) -> str:
        """Get student's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        doc_dict = self.dict()
        doc_dict['id'] = str(self.id)
        doc_dict['full_name'] = self.full_name
        
        # Convert date objects to ISO format strings
        if self.date_of_birth:
            doc_dict['date_of_birth'] = self.date_of_birth.isoformat()
        if self.enrollment_date:
            doc_dict['enrollment_date'] = self.enrollment_date.isoformat()
        if self.created_at:
            doc_dict['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            doc_dict['updated_at'] = self.updated_at.isoformat()
        
        return doc_dict
    
    class Settings:
        """Beanie document settings."""
        name = "students"  # Collection name
        
        # Indexes for better query performance
        indexes = [
            "student_id",
            "email",
            [("first_name", 1), ("last_name", 1)],
            "enrollment_date"
        ]


class MongoConnection:
    """
    MongoDB connection manager.
    
    Handles connection lifecycle, database initialization,
    and provides access to database collections.
    """
    
    def __init__(self):
        """Initialize MongoDB connection manager."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.is_connected: bool = False
    
    async def connect(self) -> None:
        """
        Establish connection to MongoDB.
        
        Creates async client, connects to database, and initializes Beanie ODM.
        
        Raises:
            Exception: If connection fails
        """
        try:
            # Create async MongoDB client
            self.client = AsyncIOMotorClient(
                settings.mongodb_connection_string,
                minPoolSize=settings.mongodb_min_connections,
                maxPoolSize=settings.mongodb_max_connections,
                maxIdleTimeMS=settings.mongodb_max_idle_time_ms
            )
            
            # Get database reference
            self.database = self.client[settings.mongodb_database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Initialize Beanie ODM with document models
            await init_beanie(
                database=self.database,
                document_models=[StudentDocument]
            )
            
            self.is_connected = True
            print(f"✅ Connected to MongoDB: {settings.mongodb_database_name}")
            
        except Exception as e:
            self.is_connected = False
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.is_connected = False
            print("📤 Disconnected from MongoDB")
    
    async def ping(self) -> bool:
        """
        Test MongoDB connection.
        
        Returns:
            bool: True if connection is alive, False otherwise
        """
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
        except Exception:
            pass
        return False
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        Get MongoDB collection reference.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            AsyncIOMotorCollection: Collection reference
            
        Raises:
            Exception: If not connected to database
        """
        if not self.database:
            raise Exception("Not connected to MongoDB database")
        
        return self.database[collection_name]
    
    async def create_indexes(self) -> None:
        """Create database indexes for better query performance."""
        if not self.database:
            raise Exception("Not connected to MongoDB database")
        
        students_collection = self.get_collection("students")
        
        # Create indexes for students collection
        await students_collection.create_index("student_id", unique=True)
        await students_collection.create_index("email", unique=True)
        await students_collection.create_index([("first_name", 1), ("last_name", 1)])
        await students_collection.create_index("enrollment_date")
        
        print("✅ MongoDB indexes created")


class MongoStudentRepository:
    """
    MongoDB repository for Student operations.
    
    Provides async database operations for student management using Beanie ODM.
    """
    
    async def create_student(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        address: Optional[str] = None
    ) -> StudentDocument:
        """
        Create new student document.
        
        Args:
            student_id (str): Student's unique identifier
            first_name (str): Student's first name
            last_name (str): Student's last name
            email (str): Student's email address
            phone (Optional[str]): Student's phone number
            date_of_birth (Optional[date]): Student's date of birth
            address (Optional[str]): Student's address
            
        Returns:
            StudentDocument: Created student document
            
        Raises:
            Exception: If creation fails or unique constraints are violated
        """
        try:
            # Check if student_id already exists
            existing_student = await StudentDocument.find_one(
                StudentDocument.student_id == student_id
            )
            if existing_student:
                raise Exception(f"Student with ID '{student_id}' already exists")
            
            # Check if email already exists
            existing_email = await StudentDocument.find_one(
                StudentDocument.email == email.lower().strip()
            )
            if existing_email:
                raise Exception(f"Student with email '{email}' already exists")
            
            # Create new student document
            student = StudentDocument(
                student_id=student_id.strip(),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                email=email.lower().strip(),
                phone=phone.strip() if phone else None,
                date_of_birth=date_of_birth,
                address=address.strip() if address else None,
                enrollment_date=date.today(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to database
            await student.save()
            
            return student
            
        except Exception as e:
            raise Exception(f"Failed to create student: {str(e)}")
    
    async def get_by_student_id(self, student_id: str) -> Optional[StudentDocument]:
        """Get student by student ID."""
        return await StudentDocument.find_one(StudentDocument.student_id == student_id)
    
    async def get_by_email(self, email: str) -> Optional[StudentDocument]:
        """Get student by email."""
        return await StudentDocument.find_one(StudentDocument.email == email.lower().strip())
    
    async def get_all_students(self, limit: int = 100, skip: int = 0) -> List[StudentDocument]:
        """Get all students with pagination."""
        return await StudentDocument.find().skip(skip).limit(limit).to_list()
    
    async def count_students(self) -> int:
        """Get total count of students."""
        return await StudentDocument.count()


# Global MongoDB connection instance
mongo_connection = MongoConnection()


async def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
        
    Raises:
        Exception: If not connected to MongoDB
    """
    if not mongo_connection.is_connected:
        await mongo_connection.connect()
    
    if not mongo_connection.database:
        raise Exception("MongoDB database not available")
    
    return mongo_connection.database


async def init_mongodb() -> None:
    """Initialize MongoDB connection and create indexes."""
    await mongo_connection.connect()
    await mongo_connection.create_indexes()


async def close_mongodb() -> None:
    """Close MongoDB connection."""
    await mongo_connection.disconnect()