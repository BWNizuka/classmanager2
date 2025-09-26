"""
Business layer service for student management.

This module contains the business logic for student operations,
including validation and orchestration of data access operations.
"""

from typing import Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from ..data.repository import StudentRepository
from ..data.models import Student


class StudentService:
    """
    Business service for student operations.
    
    This class contains business logic for student creation and validation,
    acting as an intermediary between the presentation layer and data layer.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize StudentService with database session.
        
        Args:
            db_session (Session): SQLAlchemy database session
        """
        self.repository = StudentRepository(db_session)
    
    def create_new_student(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        date_of_birth_str: Optional[str] = None,
        address: Optional[str] = None
    ) -> dict:
        """
        Create a new student with business logic validation.
        
        Args:
            student_id (str): Student's unique identifier
            first_name (str): Student's first name
            last_name (str): Student's last name
            email (str): Student's email address
            phone (Optional[str]): Student's phone number
            date_of_birth_str (Optional[str]): Date of birth in YYYY-MM-DD format
            address (Optional[str]): Student's address
            
        Returns:
            dict: Created student data with success status
            
        Raises:
            Exception: If validation fails or student creation fails
        """
        # Validate required data
        is_valid, error_msg = self.repository.validate_student_data(
            student_id, first_name, last_name, email
        )
        if not is_valid:
            raise Exception(error_msg)
        
        # Parse date of birth if provided
        date_of_birth = None
        if date_of_birth_str:
            date_of_birth = self._parse_date_of_birth(date_of_birth_str)
        
        # Additional business validations
        self._validate_age(date_of_birth)
        self._validate_phone_format(phone)
        
        # Create student through repository
        student = self.repository.create_student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            date_of_birth=date_of_birth,
            address=address
        )
        
        return {
            "success": True,
            "message": f"Student {student.full_name} created successfully",
            "student": student.to_dict()
        }
    
    def _parse_date_of_birth(self, date_str: str) -> date:
        """
        Parse date of birth string to date object.
        
        Args:
            date_str (str): Date string in YYYY-MM-DD format
            
        Returns:
            date: Parsed date object
            
        Raises:
            Exception: If date format is invalid
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise Exception("Invalid date format. Use YYYY-MM-DD format")
    
    def _validate_age(self, date_of_birth: Optional[date]) -> None:
        """
        Validate student age based on date of birth.
        
        Args:
            date_of_birth (Optional[date]): Student's date of birth
            
        Raises:
            Exception: If age is invalid
        """
        if date_of_birth is None:
            return  # Optional field, skip validation
        
        today = date.today()
        
        # Check if date is not in the future
        if date_of_birth > today:
            raise Exception("Date of birth cannot be in the future")
        
        # Calculate age
        age = today.year - date_of_birth.year
        if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
            age -= 1
        
        # Business rule: student must be at least 16 years old and at most 100 years old
        if age < 16:
            raise Exception("Student must be at least 16 years old")
        
        if age > 100:
            raise Exception("Invalid date of birth")
    
    def _validate_phone_format(self, phone: Optional[str]) -> None:
        """
        Validate phone number format.
        
        Args:
            phone (Optional[str]): Phone number to validate
            
        Raises:
            Exception: If phone format is invalid
        """
        if phone is None or not phone.strip():
            return  # Optional field, skip validation
        
        phone = phone.strip()
        
        # Basic phone validation: should contain only digits, spaces, hyphens, parentheses, and plus
        allowed_chars = set('0123456789 -()+ ')
        if not all(c in allowed_chars for c in phone):
            raise Exception("Phone number contains invalid characters")
        
        # Extract digits only for length check
        digits_only = ''.join(c for c in phone if c.isdigit())
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise Exception("Phone number must have between 10-15 digits")