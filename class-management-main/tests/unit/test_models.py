"""
Unit tests for data models.

Tests for Student model functionality including validation,
properties, and database operations.
"""

import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from backend.data.models import Student


class TestStudentModel:
    """Test cases for Student model."""

    def test_create_student_with_required_fields(self, db_session):
        """Test creating a student with only required fields."""
        student = Student(
            student_id="TEST001",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            enrollment_date=date.today()
        )
        
        db_session.add(student)
        db_session.commit()
        
        assert student.id is not None
        assert student.student_id == "TEST001"
        assert student.first_name == "John"
        assert student.last_name == "Doe"
        assert student.email == "john.doe@example.com"
        assert student.enrollment_date == date.today()
        assert student.created_at is not None
        assert student.updated_at is not None

    def test_create_student_with_all_fields(self, db_session):
        """Test creating a student with all fields."""
        test_date = date(2000, 1, 1)
        
        student = Student(
            student_id="TEST002",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="+1-555-0123",
            date_of_birth=test_date,
            address="123 Main St, Anytown, USA",
            enrollment_date=date.today()
        )
        
        db_session.add(student)
        db_session.commit()
        
        assert student.phone == "+1-555-0123"
        assert student.date_of_birth == test_date
        assert student.address == "123 Main St, Anytown, USA"

    def test_student_full_name_property(self, db_session):
        """Test full_name property returns correct concatenated name."""
        student = Student(
            student_id="TEST003",
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            enrollment_date=date.today()
        )
        
        assert student.full_name == "Alice Johnson"

    def test_student_to_dict_method(self, db_session):
        """Test to_dict method returns correct dictionary representation."""
        test_date = date(2000, 5, 15)
        
        student = Student(
            student_id="TEST004",
            first_name="Bob",
            last_name="Wilson",
            email="bob.wilson@example.com",
            phone="+1-555-0456",
            date_of_birth=test_date,
            address="456 Oak Ave, Somewhere, USA",
            enrollment_date=date.today()
        )
        
        db_session.add(student)
        db_session.commit()
        
        student_dict = student.to_dict()
        
        assert student_dict["student_id"] == "TEST004"
        assert student_dict["first_name"] == "Bob"
        assert student_dict["last_name"] == "Wilson"
        assert student_dict["full_name"] == "Bob Wilson"
        assert student_dict["email"] == "bob.wilson@example.com"
        assert student_dict["phone"] == "+1-555-0456"
        assert student_dict["date_of_birth"] == test_date.isoformat()
        assert student_dict["address"] == "456 Oak Ave, Somewhere, USA"
        assert "created_at" in student_dict
        assert "updated_at" in student_dict

    def test_student_string_representation(self, db_session):
        """Test __repr__ method returns correct string representation."""
        student = Student(
            student_id="TEST005",
            first_name="Charlie",
            last_name="Brown",
            email="charlie.brown@example.com",
            enrollment_date=date.today()
        )
        
        db_session.add(student)
        db_session.commit()
        
        repr_str = repr(student)
        expected_pattern = f"<Student(id={student.id}, student_id='TEST005', name='Charlie Brown', email='charlie.brown@example.com')>"
        
        assert repr_str == expected_pattern

    def test_unique_student_id_constraint(self, db_session):
        """Test that student_id must be unique."""
        student1 = Student(
            student_id="DUPLICATE001",
            first_name="First",
            last_name="Student",
            email="first@example.com",
            enrollment_date=date.today()
        )
        
        student2 = Student(
            student_id="DUPLICATE001",  # Same student_id
            first_name="Second",
            last_name="Student",
            email="second@example.com",
            enrollment_date=date.today()
        )
        
        db_session.add(student1)
        db_session.commit()
        
        db_session.add(student2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_unique_email_constraint(self, db_session):
        """Test that email must be unique."""
        student1 = Student(
            student_id="EMAIL001",
            first_name="First",
            last_name="Student",
            email="duplicate@example.com",
            enrollment_date=date.today()
        )
        
        student2 = Student(
            student_id="EMAIL002",
            first_name="Second",
            last_name="Student",
            email="duplicate@example.com",  # Same email
            enrollment_date=date.today()
        )
        
        db_session.add(student1)
        db_session.commit()
        
        db_session.add(student2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_default_enrollment_date(self, db_session):
        """Test that enrollment_date defaults to today."""
        student = Student(
            student_id="DEFAULT001",
            first_name="Default",
            last_name="Student",
            email="default@example.com"
        )
        
        db_session.add(student)
        db_session.commit()
        
        assert student.enrollment_date == date.today()

    def test_automatic_timestamps(self, db_session):
        """Test that created_at and updated_at are set automatically."""
        student = Student(
            student_id="TIMESTAMP001",
            first_name="Timestamp",
            last_name="Student",
            email="timestamp@example.com",
            enrollment_date=date.today()
        )
        
        db_session.add(student)
        db_session.commit()
        
        assert student.created_at is not None
        assert student.updated_at is not None
        assert isinstance(student.created_at, datetime)
        assert isinstance(student.updated_at, datetime)

    @pytest.mark.parametrize("field,value", [
        ("student_id", ""),
        ("first_name", ""),
        ("last_name", ""),
        ("email", ""),
    ])
    def test_required_fields_validation(self, db_session, field, value):
        """Test that required fields cannot be empty."""
        student_data = {
            "student_id": "REQ001",
            "first_name": "Required",
            "last_name": "Student",
            "email": "required@example.com",
            "enrollment_date": date.today()
        }
        
        # Set the field to invalid value
        student_data[field] = value
        
        student = Student(**student_data)
        db_session.add(student)
        
        with pytest.raises((IntegrityError, ValueError)):
            db_session.commit()

    def test_optional_fields_can_be_none(self, db_session):
        """Test that optional fields can be None or empty."""
        student = Student(
            student_id="OPTIONAL001",
            first_name="Optional",
            last_name="Student",
            email="optional@example.com",
            phone=None,
            date_of_birth=None,
            address=None,
            enrollment_date=date.today()
        )
        
        db_session.add(student)
        db_session.commit()
        
        assert student.phone is None
        assert student.date_of_birth is None
        assert student.address is None

    def test_field_length_constraints(self, db_session):
        """Test field length constraints."""
        # Test maximum lengths (these should not raise errors)
        student = Student(
            student_id="A" * 20,  # Max 20 characters
            first_name="B" * 50,  # Max 50 characters
            last_name="C" * 50,   # Max 50 characters
            email="d" * 90 + "@example.com",  # Max 100 characters total
            phone="+" + "1" * 19,  # Max 20 characters
            address="E" * 200,     # Max 200 characters
            enrollment_date=date.today()
        )
        
        db_session.add(student)
        db_session.commit()
        
        assert len(student.student_id) == 20
        assert len(student.first_name) == 50
        assert len(student.last_name) == 50