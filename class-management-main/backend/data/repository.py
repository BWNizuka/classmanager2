"""
Repository for Student data access operations.

This module provides the StudentRepository class for creating new students
in the database using the Repository design pattern.
"""

from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .models import Student


class StudentRepository:
    """
    Repository class for Student creation operations.
    
    Handles database operations for creating new students with proper
    validation and error handling.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize StudentRepository with database session.
        
        Args:
            db_session (Session): SQLAlchemy database session
        """
        self.db = db_session
    
    def create_student(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        address: Optional[str] = None
    ) -> Student:
        """
        Create new student with validation.
        
        Args:
            student_id (str): Student's unique identifier
            first_name (str): Student's first name
            last_name (str): Student's last name
            email (str): Student's email address
            phone (Optional[str]): Student's phone number
            date_of_birth (Optional[date]): Student's date of birth
            address (Optional[str]): Student's address
            
        Returns:
            Student: Created student instance
            
        Raises:
            Exception: If student creation fails or unique constraints are violated
        """
        try:
            # Create new student instance with cleaned data
            student = Student(
                student_id=student_id.strip(),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                email=email.lower().strip(),
                phone=phone.strip() if phone else None,
                date_of_birth=date_of_birth,
                address=address.strip() if address else None,
                enrollment_date=date.today()
            )
            
            # Add to session and commit
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
            
            return student
            
        except IntegrityError as e:
            self.db.rollback()
            # Handle unique constraint violations
            if "student_id" in str(e):
                raise Exception(f"Student with ID '{student_id}' already exists")
            elif "email" in str(e):
                raise Exception(f"Student with email '{email}' already exists")
            else:
                raise Exception(f"Integrity error creating student: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error creating student: {str(e)}")
    
    def validate_student_data(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        email: str
    ) -> tuple[bool, str]:
        """
        Validate required student data before creation.
        
        Args:
            student_id (str): Student's unique identifier
            first_name (str): Student's first name
            last_name (str): Student's last name
            email (str): Student's email address
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check required fields
        if not student_id or not student_id.strip():
            return False, "Student ID is required"
        
        if not first_name or not first_name.strip():
            return False, "First name is required"
        
        if not last_name or not last_name.strip():
            return False, "Last name is required"
        
        if not email or not email.strip():
            return False, "Email is required"
        
        # Validate student ID format
        student_id = student_id.strip()
        if len(student_id) < 3 or len(student_id) > 20:
            return False, "Student ID must be between 3-20 characters"
        
        # Basic email validation
        email = email.strip()
        if "@" not in email or "." not in email:
            return False, "Invalid email format"
        
        return True, ""