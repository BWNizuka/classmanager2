"""
Unit tests for service layer.

Tests for StudentService business logic including validation,
data processing, and orchestration of repository operations.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch

from backend.services.student_service import StudentService
from backend.data.models import Student


class TestStudentService:
    """Test cases for StudentService."""

    def test_create_new_student_success(self, db_session):
        """Test successful student creation through service."""
        service = StudentService(db_session)
        
        result = service.create_new_student(
            student_id="SVC001",
            first_name="Service",
            last_name="Test",
            email="service@example.com",
            phone="+1-555-0111",
            date_of_birth_str="2000-06-15",
            address="111 Service St, Test City, TC 11111"
        )
        
        assert result["success"] is True
        assert "Service Test created successfully" in result["message"]
        assert "student" in result
        
        student_data = result["student"]
        assert student_data["student_id"] == "SVC001"
        assert student_data["first_name"] == "Service"
        assert student_data["last_name"] == "Test"
        assert student_data["full_name"] == "Service Test"
        assert student_data["email"] == "service@example.com"
        assert student_data["phone"] == "+1-555-0111"
        assert student_data["date_of_birth"] == "2000-06-15"
        assert student_data["address"] == "111 Service St, Test City, TC 11111"

    def test_create_new_student_minimal_data(self, db_session):
        """Test creating student with only required fields."""
        service = StudentService(db_session)
        
        result = service.create_new_student(
            student_id="SVC002",
            first_name="Minimal",
            last_name="Service",
            email="minimal.service@example.com"
        )
        
        assert result["success"] is True
        student_data = result["student"]
        assert student_data["phone"] is None
        assert student_data["date_of_birth"] is None
        assert student_data["address"] is None

    def test_create_new_student_invalid_data(self, db_session):
        """Test service validation with invalid data."""
        service = StudentService(db_session)
        
        with pytest.raises(Exception) as exc_info:
            service.create_new_student(
                student_id="",  # Invalid
                first_name="Invalid",
                last_name="Service",
                email="invalid@example.com"
            )
        
        assert "Student ID is required" in str(exc_info.value)

    @pytest.mark.parametrize("date_str,expected_error", [
        ("invalid-date", "Invalid date format"),
        ("2000-13-01", "Invalid date format"),  # Invalid month
        ("2000-02-30", "Invalid date format"),  # Invalid day
        ("00-01-01", "Invalid date format"),    # Invalid year format
        ("2000/01/01", "Invalid date format"),  # Wrong separator
    ])
    def test_parse_date_of_birth_invalid(self, db_session, date_str, expected_error):
        """Test date parsing with invalid date strings."""
        service = StudentService(db_session)
        
        with pytest.raises(Exception) as exc_info:
            service.create_new_student(
                student_id="DATE001",
                first_name="Date",
                last_name="Test",
                email="date@example.com",
                date_of_birth_str=date_str
            )
        
        assert expected_error in str(exc_info.value)

    def test_parse_date_of_birth_valid(self, db_session):
        """Test date parsing with valid date string."""
        service = StudentService(db_session)
        
        result = service.create_new_student(
            student_id="VALIDDATE001",
            first_name="Valid",
            last_name="Date",
            email="validdate@example.com",
            date_of_birth_str="1995-12-25"
        )
        
        assert result["success"] is True
        assert result["student"]["date_of_birth"] == "1995-12-25"

    @pytest.mark.parametrize("birth_date_str,expected_error", [
        ("2050-01-01", "Date of birth cannot be in the future"),  # Future date
        ("2010-01-01", "Student must be at least 16 years old"),  # Too young (assuming current year is 2024)
        ("1900-01-01", "Invalid date of birth"),  # Too old
    ])
    def test_validate_age_invalid(self, db_session, birth_date_str, expected_error):
        """Test age validation with invalid ages."""
        service = StudentService(db_session)
        
        with pytest.raises(Exception) as exc_info:
            service.create_new_student(
                student_id="AGE001",
                first_name="Age",
                last_name="Test",
                email="age@example.com",
                date_of_birth_str=birth_date_str
            )
        
        assert expected_error in str(exc_info.value)

    def test_validate_age_valid(self, db_session):
        """Test age validation with valid age."""
        service = StudentService(db_session)
        
        # Calculate a date that makes the person exactly 20 years old
        twenty_years_ago = date.today().replace(year=date.today().year - 20)
        date_str = twenty_years_ago.strftime("%Y-%m-%d")
        
        result = service.create_new_student(
            student_id="VALIDAGE001",
            first_name="Valid",
            last_name="Age",
            email="validage@example.com",
            date_of_birth_str=date_str
        )
        
        assert result["success"] is True

    def test_validate_age_none_allowed(self, db_session):
        """Test that None date of birth is allowed."""
        service = StudentService(db_session)
        
        result = service.create_new_student(
            student_id="NOAGE001",
            first_name="No",
            last_name="Age",
            email="noage@example.com",
            date_of_birth_str=None
        )
        
        assert result["success"] is True
        assert result["student"]["date_of_birth"] is None

    @pytest.mark.parametrize("phone,expected_error", [
        ("123-456-789a", "Phone number contains invalid characters"),  # Contains letter
        ("123@456#7890", "Phone number contains invalid characters"),  # Invalid chars
        ("123456789", "Phone number must have between 10-15 digits"),  # Too few digits
        ("1234567890123456", "Phone number must have between 10-15 digits"),  # Too many digits
    ])
    def test_validate_phone_format_invalid(self, db_session, phone, expected_error):
        """Test phone validation with invalid formats."""
        service = StudentService(db_session)
        
        with pytest.raises(Exception) as exc_info:
            service.create_new_student(
                student_id="PHONE001",
                first_name="Phone",
                last_name="Test",
                email="phone@example.com",
                phone=phone
            )
        
        assert expected_error in str(exc_info.value)

    @pytest.mark.parametrize("phone", [
        "+1-555-123-4567",
        "(555) 123-4567",
        "555.123.4567",
        "15551234567",
        "+44 20 7946 0958",  # UK format
        None,  # None should be allowed
        "",    # Empty string should be allowed
        "   ", # Whitespace only should be allowed
    ])
    def test_validate_phone_format_valid(self, db_session, phone):
        """Test phone validation with valid formats."""
        service = StudentService(db_session)
        
        result = service.create_new_student(
            student_id=f"VALIDPHONE{hash(str(phone)) % 1000}",
            first_name="Valid",
            last_name="Phone",
            email=f"validphone{hash(str(phone)) % 1000}@example.com",
            phone=phone
        )
        
        assert result["success"] is True

    def test_repository_error_propagation(self, db_session):
        """Test that repository errors are properly propagated."""
        service = StudentService(db_session)
        
        # Create first student
        service.create_new_student(
            student_id="DUPLICATE",
            first_name="First",
            last_name="Student",
            email="first@example.com"
        )
        
        # Try to create duplicate - should propagate repository error
        with pytest.raises(Exception) as exc_info:
            service.create_new_student(
                student_id="DUPLICATE",
                first_name="Second",
                last_name="Student",
                email="second@example.com"
            )
        
        assert "already exists" in str(exc_info.value)

    def test_service_uses_repository_correctly(self, db_session):
        """Test that service uses repository methods correctly."""
        service = StudentService(db_session)
        
        # Mock the repository to verify method calls
        with patch.object(service.repository, 'validate_student_data') as mock_validate:
            with patch.object(service.repository, 'create_student') as mock_create:
                
                mock_validate.return_value = (True, "")
                mock_student = Mock()
                mock_student.to_dict.return_value = {"student_id": "TEST"}
                mock_student.full_name = "Test Student"
                mock_create.return_value = mock_student
                
                service.create_new_student(
                    student_id="TEST001",
                    first_name="Test",
                    last_name="Student",
                    email="test@example.com"
                )
                
                # Verify repository methods were called
                mock_validate.assert_called_once()
                mock_create.assert_called_once()

    def test_create_student_with_empty_optional_strings(self, db_session):
        """Test handling of empty strings for optional fields."""
        service = StudentService(db_session)
        
        result = service.create_new_student(
            student_id="EMPTY001",
            first_name="Empty",
            last_name="Optional",
            email="empty@example.com",
            phone="",
            date_of_birth_str="",
            address=""
        )
        
        assert result["success"] is True
        student_data = result["student"]
        assert student_data["phone"] is None
        assert student_data["date_of_birth"] is None
        assert student_data["address"] is None

    def test_business_logic_orchestration(self, db_session):
        """Test that business logic is properly orchestrated."""
        service = StudentService(db_session)
        
        # Test the full flow with all validations
        result = service.create_new_student(
            student_id="ORCHESTRATION001",
            first_name="Business",
            last_name="Logic",
            email="business.logic@example.com",
            phone="+1-555-0199",
            date_of_birth_str="1990-03-15",
            address="199 Business Ave, Logic City, LC 19900"
        )
        
        # Verify all business rules were applied
        assert result["success"] is True
        assert "Business Logic created successfully" in result["message"]
        
        student_data = result["student"]
        assert student_data["email"] == "business.logic@example.com"  # Email case handled
        assert student_data["enrollment_date"] is not None  # Enrollment date set
        assert student_data["created_at"] is not None  # Timestamps set
        assert student_data["updated_at"] is not None