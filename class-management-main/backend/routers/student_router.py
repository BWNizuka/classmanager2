"""
Student router for handling student-related API endpoints.

This module defines the FastAPI router for student creation operations.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..services.student_service import StudentService
from ..data.database import get_db


# Pydantic models for API requests and responses
class StudentCreateRequest(BaseModel):
    """Request model for creating a new student."""
    
    student_id: str = Field(..., min_length=3, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[str] = Field(None, description="Format: YYYY-MM-DD")
    address: Optional[str] = Field(None, max_length=200)


class ApiResponse(BaseModel):
    """Generic API response model."""
    
    success: bool
    message: str
    data: Optional[dict] = None


# Create FastAPI router
router = APIRouter(
    prefix="/api/students",
    tags=["Students"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=ApiResponse)
def create_student(
    student_data: StudentCreateRequest,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    Create a new student.
    
    Args:
        student_data (StudentCreateRequest): Student information
        db (Session): Database session dependency
        
    Returns:
        ApiResponse: Success response with created student data
        
    Raises:
        HTTPException: If student creation fails
    """
    try:
        # Initialize student service
        student_service = StudentService(db)
        
        # Create new student
        result = student_service.create_new_student(
            student_id=student_data.student_id,
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            email=student_data.email,
            phone=student_data.phone,
            date_of_birth_str=student_data.date_of_birth,
            address=student_data.address
        )
        
        return ApiResponse(
            success=True,
            message=result["message"],
            data=result["student"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create student: {str(e)}"
        )