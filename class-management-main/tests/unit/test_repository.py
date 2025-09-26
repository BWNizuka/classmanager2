"""
Unit tests for repository layer.

Tests for StudentRepository class functionality including
CRUD operations and data validation.
"""

import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError

from backend.data.repository import StudentRepository
from backend.data.models import Student


class TestStudentRepository:
    """Test cases for StudentRepository."""

    def test_create_student_success(self, db_session):
        """Test successful student creation."""
        repository = StudentRepository(db_session)
        
        student = repository.create_student(
            student_id="REPO001",
            first_name="Repository",
            last_name="Test",
            email="repo.test@example.com",
            phone="+1-555-0789",
            date_of_birth=date(2000, 1, 1),
            address="789 Repo St, Test City, TC 12345"
        )
        
        assert student.id is not None
        assert student.student_id == "REPO001"
        assert student.first_name == "Repository"
        assert student.last_name == "Test"
        assert student.email == "repo.test@example.com"
        assert student.phone == "+1-555-0789"
        assert student.date_of_birth == date(2000, 1, 1)
        assert student.address == "789 Repo St, Test City, TC 12345"
        assert student.enrollment_date == date.today()

    def test_create_student_with_minimal_data(self, db_session):
        """Test creating student with only required fields."""
        repository = StudentRepository(db_session)
        
        student = repository.create_student(
            student_id="REPO002",
            first_name="Minimal",
            last_name="Data",
            email="minimal@example.com"
        )
        
        assert student.student_id == "REPO002"
        assert student.first_name == "Minimal"
        assert student.last_name == "Data"
        assert student.email == "minimal@example.com"
        assert student.phone is None
        assert student.date_of_birth is None
        assert student.address is None

    def test_create_student_duplicate_student_id(self, db_session):
        """Test that creating student with duplicate student_id raises exception."""
        repository = StudentRepository(db_session)
        
        # Create first student
        repository.create_student(
            student_id="DUPLICATE",
            first_name="First",
            last_name="Student",
            email="first@example.com"
        )
        
        # Attempt to create second student with same student_id
        with pytest.raises(Exception) as exc_info:
            repository.create_student(
                student_id="DUPLICATE",
                first_name="Second",
                last_name="Student",
                email="second@example.com"
            )
        
        assert "already exists" in str(exc_info.value)

    def test_create_student_duplicate_email(self, db_session):
        """Test that creating student with duplicate email raises exception."""
        repository = StudentRepository(db_session)
        
        # Create first student
        repository.create_student(
            student_id="EMAIL001",
            first_name="First",
            last_name="Student",
            email="duplicate@example.com"
        )
        
        # Attempt to create second student with same email
        with pytest.raises(Exception) as exc_info:
            repository.create_student(
                student_id="EMAIL002",
                first_name="Second",
                last_name="Student",
                email="duplicate@example.com"
            )
        
        assert "already exists" in str(exc_info.value)

    def test_validate_student_data_valid(self, db_session):
        """Test validation with valid student data."""
        repository = StudentRepository(db_session)
        
        is_valid, error_msg = repository.validate_student_data(
            student_id="VALID001",
            first_name="Valid",
            last_name="Student",
            email="valid@example.com"
        )
        
        assert is_valid is True
        assert error_msg == ""

    @pytest.mark.parametrize("student_id,first_name,last_name,email,expected_error", [
        ("", "Valid", "Student", "valid@example.com", "Student ID is required"),
        ("   ", "Valid", "Student", "valid@example.com", "Student ID is required"),
        ("VALID001", "", "Student", "valid@example.com", "First name is required"),
        ("VALID001", "   ", "Student", "valid@example.com", "First name is required"),
        ("VALID001", "Valid", "", "valid@example.com", "Last name is required"),
        ("VALID001", "Valid", "   ", "valid@example.com", "Last name is required"),
        ("VALID001", "Valid", "Student", "", "Email is required"),
        ("VALID001", "Valid", "Student", "   ", "Email is required"),
        ("AB", "Valid", "Student", "valid@example.com", "Student ID must be between 3-20 characters"),
        ("A" * 21, "Valid", "Student", "valid@example.com", "Student ID must be between 3-20 characters"),
        ("VALID001", "Valid", "Student", "invalid-email", "Invalid email format"),
        ("VALID001", "Valid", "Student", "no-at-sign", "Invalid email format"),
    ])
    def test_validate_student_data_invalid(self, db_session, student_id, first_name, last_name, email, expected_error):
        """Test validation with invalid student data."""
        repository = StudentRepository(db_session)
        
        is_valid, error_msg = repository.validate_student_data(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        assert is_valid is False
        assert expected_error in error_msg

    def test_create_student_strips_whitespace(self, db_session):
        """Test that student creation strips whitespace from input."""
        repository = StudentRepository(db_session)
        
        student = repository.create_student(
            student_id="  WHITESPACE001  ",
            first_name="  John  ",
            last_name="  Doe  ",
            email="  JOHN.DOE@EXAMPLE.COM  ",
            phone="  +1-555-0123  ",
            address="  123 Main St  "
        )
        
        assert student.student_id == "WHITESPACE001"
        assert student.first_name == "John"
        assert student.last_name == "Doe"
        assert student.email == "john.doe@example.com"  # Should be lowercase
        assert student.phone == "+1-555-0123"
        assert student.address == "123 Main St"

    def test_create_student_email_case_insensitive(self, db_session):
        """Test that email is stored in lowercase."""
        repository = StudentRepository(db_session)
        
        student = repository.create_student(
            student_id="CASE001",
            first_name="Case",
            last_name="Test",
            email="CASE.TEST@EXAMPLE.COM"
        )
        
        assert student.email == "case.test@example.com"

    def test_create_student_handles_none_optional_fields(self, db_session):
        """Test that None values for optional fields are handled correctly."""
        repository = StudentRepository(db_session)
        
        student = repository.create_student(
            student_id="NONE001",
            first_name="None",
            last_name="Test",
            email="none@example.com",
            phone=None,
            date_of_birth=None,
            address=None
        )
        
        assert student.phone is None
        assert student.date_of_birth is None
        assert student.address is None

    def test_create_student_handles_empty_string_optional_fields(self, db_session):
        """Test that empty strings for optional fields are converted to None."""
        repository = StudentRepository(db_session)
        
        student = repository.create_student(
            student_id="EMPTY001",
            first_name="Empty",
            last_name="Test",
            email="empty@example.com",
            phone="",
            address="   "  # Whitespace only
        )
        
        assert student.phone is None
        assert student.address is None

    def test_create_student_database_error_handling(self, db_session, monkeypatch):
        """Test that database errors are properly handled and re-raised."""
        repository = StudentRepository(db_session)
        
        # Mock db_session.add to raise an exception
        def mock_add(obj):
            raise Exception("Database connection failed")
        
        monkeypatch.setattr(db_session, "add", mock_add)
        
        with pytest.raises(Exception) as exc_info:
            repository.create_student(
                student_id="ERROR001",
                first_name="Error",
                last_name="Test",
                email="error@example.com"
            )
        
        assert "Database error creating student" in str(exc_info.value)

    def test_create_student_sets_enrollment_date(self, db_session, mock_datetime):
        """Test that enrollment_date is set to current date."""
        repository = StudentRepository(db_session)
        
        student = repository.create_student(
            student_id="DATE001",
            first_name="Date",
            last_name="Test",
            email="date@example.com"
        )
        
        assert student.enrollment_date == mock_datetime["date"]

    def test_repository_session_management(self, db_session):
        """Test that repository uses the provided session correctly."""
        repository = StudentRepository(db_session)
        
        # Verify the repository uses the provided session
        assert repository.db is db_session
        
        # Create a student to test session usage
        student = repository.create_student(
            student_id="SESSION001",
            first_name="Session",
            last_name="Test",
            email="session@example.com"
        )
        
        # Verify the student was created in the session
        session_student = db_session.query(Student).filter_by(student_id="SESSION001").first()
        assert session_student is not None
        assert session_student.id == student.id