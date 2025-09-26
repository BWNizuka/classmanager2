"""
Streamlit frontend application for Class Management System.

This module provides a web interface for creating new students
through the FastAPI backend with 3-layer architecture.
"""

from typing import Optional
import streamlit as st
import requests
from datetime import date


# Configuration constants
BACKEND_URL: str = "http://localhost:8000"
REQUEST_TIMEOUT: int = 10  # seconds


def configure_page() -> None:
    """Configure Streamlit page settings and styling."""
    st.set_page_config(
        page_title="Class Management System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def test_backend_connection() -> None:
    """
    Test connectivity to the backend API and display results.
    
    Makes a GET request to the backend health endpoint and shows
    connection status to the user.
    """
    try:
        # Attempt to connect to backend health endpoint
        response = requests.get(f"{BACKEND_URL}/", timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            message = response.json().get('message', 'Unknown response')
            st.success(f"✅ Backend connected: {message}")
        else:
            st.error(f"❌ Backend error: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure it's running on port 8000.")
    except requests.exceptions.Timeout:
        st.error("❌ Connection timeout. Backend may be slow or unresponsive.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")


def create_student(
    student_id: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    address: Optional[str] = None
) -> None:
    """
    Create a new student through the backend API.
    
    Args:
        student_id (str): Student's unique identifier
        first_name (str): Student's first name
        last_name (str): Student's last name
        email (str): Student's email address
        phone (Optional[str]): Student's phone number
        date_of_birth (Optional[str]): Date of birth in YYYY-MM-DD format
        address (Optional[str]): Student's address
    """
    # Validate required fields
    if not all([student_id.strip(), first_name.strip(), last_name.strip(), email.strip()]):
        st.warning("Please fill in all required fields (Student ID, First Name, Last Name, Email).")
        return
    
    # Prepare payload for API submission
    payload = {
        "student_id": student_id.strip(),
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip()
    }
    
    # Add optional fields if provided
    if phone and phone.strip():
        payload["phone"] = phone.strip()
    if date_of_birth and date_of_birth.strip():
        payload["date_of_birth"] = date_of_birth.strip()
    if address and address.strip():
        payload["address"] = address.strip()
    
    try:
        # Submit student data to backend
        response = requests.post(
            f"{BACKEND_URL}/api/students/",
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ {result['message']}")
            
            # Display created student information
            with st.expander("View Created Student Details", expanded=True):
                student_data = result.get('data', {})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Student ID:** {student_data.get('student_id', 'N/A')}")
                    st.write(f"**Full Name:** {student_data.get('full_name', 'N/A')}")
                    st.write(f"**Email:** {student_data.get('email', 'N/A')}")
                
                with col2:
                    st.write(f"**Phone:** {student_data.get('phone', 'N/A')}")
                    st.write(f"**Date of Birth:** {student_data.get('date_of_birth', 'N/A')}")
                    st.write(f"**Enrollment Date:** {student_data.get('enrollment_date', 'N/A')}")
                
                if student_data.get('address'):
                    st.write(f"**Address:** {student_data.get('address', 'N/A')}")
                
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_message = error_data.get('detail', f'HTTP {response.status_code}')
            st.error(f"❌ Failed to create student: {error_message}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure it's running on port 8000.")
    except requests.exceptions.Timeout:
        st.error("❌ Request timeout. Backend may be slow or unresponsive.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def render_student_creation_form() -> None:
    """
    Render the student creation form.
    
    Creates a Streamlit form for users to input student information
    and submit it to the backend API.
    """
    with st.form("student_form"):
        st.subheader("Create New Student")
        
        # Required fields
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input(
                "Student ID *",
                placeholder="e.g., STU001, 2024001",
                help="Unique identifier for the student (3-20 characters)"
            )
            
            first_name = st.text_input(
                "First Name *",
                placeholder="Enter student's first name",
                help="Required field"
            )
        
        with col2:
            email = st.text_input(
                "Email Address *",
                placeholder="student@example.com",
                help="Student's email address (required)"
            )
            
            last_name = st.text_input(
                "Last Name *",
                placeholder="Enter student's last name",
                help="Required field"
            )
        
        # Optional fields
        st.subheader("Additional Information (Optional)")
        
        col3, col4 = st.columns(2)
        
        with col3:
            phone = st.text_input(
                "Phone Number",
                placeholder="e.g., +1-234-567-8900",
                help="Student's phone number (optional)"
            )
            
            date_of_birth = st.date_input(
                "Date of Birth",
                value=None,
                help="Student's date of birth (optional)"
            )
        
        with col4:
            address = st.text_area(
                "Address",
                placeholder="Enter student's address",
                height=100,
                help="Student's home address (optional)"
            )
        
        # Form submission
        if st.form_submit_button("Create Student", type="primary"):
            # Convert date to string if provided
            dob_str = None
            if date_of_birth:
                dob_str = date_of_birth.strftime("%Y-%m-%d")
            
            create_student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                date_of_birth=dob_str,
                address=address
            )


def main() -> None:
    """
    Main application function that orchestrates the Streamlit interface.
    
    Sets up the page configuration and renders all UI components
    in the correct order.
    """
    # Configure page settings
    configure_page()
    
    # Main application title
    st.title("🎓 Class Management System")
    st.markdown("### Student Registration Portal")
    st.markdown("---")
    
    # Backend connection testing section
    st.header("🔗 System Status")
    st.write("Check the connection to the backend system.")
    
    if st.button("Test System Connection", type="secondary"):
        test_backend_connection()
    
    st.markdown("---")
    
    # Student creation section
    st.header("👤 Create New Student")
    st.write("Fill in the student information below to register a new student.")
    render_student_creation_form()
    
    # Sidebar with additional information
    with st.sidebar:
        st.header("ℹ️ System Information")
        st.write(f"**Backend URL:** {BACKEND_URL}")
        st.write(f"**Request Timeout:** {REQUEST_TIMEOUT}s")
        
        st.header("📋 Student ID Guidelines")
        st.write("""
        - Must be 3-20 characters long
        - Can contain letters, numbers, hyphens, underscores
        - Must be unique for each student
        - Examples: STU001, 2024-CS-001, STUDENT_123
        """)
        
        st.header("📚 Available Features")
        st.write("✅ Create new students")
        st.write("🔄 More features coming soon...")


if __name__ == "__main__":
    main()