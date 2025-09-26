"""
FastAPI backend application for Class Management System.

This module provides a REST API with CORS support for managing students
with 3-layer architecture and SQLite database.
"""

from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import database initialization
from .data.database import init_database

# Import routers
from .routers.student_router import router as student_router


# Initialize FastAPI application with metadata
app = FastAPI(
    title="Class Management System",
    description="A REST API for managing students with 3-layer architecture",
    version="1.0.0"
)

# Configure CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(student_router)


@app.on_event("startup")
def startup_event():
    """
    Initialize database on application startup.
    
    Creates database tables if they don't exist.
    """
    init_database()


@app.get("/", tags=["Health"])
def read_root() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: Status message confirming backend is running
    """
    return {"message": "Class Management System Backend is running!"}


if __name__ == "__main__":
    # Run the application with uvicorn server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )