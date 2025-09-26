# Class Management System

[![CI/CD Pipeline](https://github.com/HoaNQ98/class-management.git/actions/workflows/ci.yml/badge.svg)](https://github.com/HoaNQ98/class-management.git/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/codecov/c/github/yourusername/class-management)](https://codecov.io/gh/yourusername/class-management)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A modern, scalable Class Management System built with **FastAPI**, **Streamlit**, and supporting both **SQLite** and **MongoDB** databases. Features a clean 3-layer architecture, comprehensive testing, and Docker deployment.

## 🚀 Features

### ✨ Core Functionality
- **Student Management**: Create, view, and manage student records
- **Dual Database Support**: Switch between SQLite (development) and MongoDB (production)
- **RESTful API**: Complete CRUD operations with FastAPI
- **Interactive Frontend**: User-friendly Streamlit interface
- **Real-time Validation**: Business logic validation at multiple layers

### 🏗️ Architecture
- **3-Layer Architecture**: Data, Service (Business Logic), Router (Presentation)
- **Environment Configuration**: Comprehensive .env management
- **Database Abstraction**: Unified interface for different database types
- **Async Support**: MongoDB integration with async operations

### 🔧 Development & Deployment
- **Docker Support**: Multi-stage builds for development and production
- **Docker Compose**: Complete orchestration with MongoDB, Redis, and Nginx
- **Comprehensive Testing**: Unit tests with 80%+ coverage requirement
- **CI/CD Pipeline**: GitHub Actions with quality checks and deployment
- **Code Quality**: Black, isort, flake8, mypy, and security scanning

## 📁 Project Structure

```
class-management/
├── backend/                     # Backend application
│   ├── core/                   # Core configuration
│   │   └── config.py          # Environment settings management
│   ├── data/                   # Data layer
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── repository.py      # Repository pattern implementation
│   │   ├── database.py        # Database configuration
│   │   └── mongo_connection.py # MongoDB connection and models
│   ├── services/               # Business logic layer
│   │   └── student_service.py # Student business logic
│   ├── routers/               # API endpoints
│   │   └── student_router.py # Student API routes
│   └── main.py               # FastAPI application entry point
├── frontend/                  # Streamlit frontend
│   └── app.py                # Main Streamlit application
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py         # Test configuration
├── docker/                   # Docker configurations
├── nginx/                   # Nginx configurations
├── scripts/                 # Utility scripts
├── monitoring/              # Monitoring configurations
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
└── .env.example            # Environment template
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM for Python
- **Pydantic** - Data validation using Python type annotations
- **Motor** - Async MongoDB driver
- **Beanie** - Async MongoDB ODM based on Pydantic

### Frontend
- **Streamlit** - Framework for building data applications
- **Pandas** - Data manipulation and analysis
- **Requests** - HTTP library for API communication

### Database
- **SQLite** - Lightweight database for development
- **MongoDB** - NoSQL database for production

### Development & Operations
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and load balancer
- **Redis** - Caching and session storage
- **Pytest** - Testing framework with coverage
- **GitHub Actions** - CI/CD pipeline

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (recommended)
- MongoDB (if using MongoDB setup)

### 1. Clone Repository
```bash
git clone https://github.com/HoaNQ98/class-management.git
cd class-management
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables as needed
nano .env
```

### 3. Docker Deployment (Recommended)

#### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access applications
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

#### Production
```bash
# Copy production environment
cp .env.example .env.prod

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Enable monitoring (optional)
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

### 4. Local Development Setup

#### Backend
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment
export PYTHONPATH="${PYTHONPATH}:${PWD}"
export APP_ENV=development

# Start backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
# Start frontend (new terminal)
cd frontend
streamlit run app.py --server.port 8501
```

## 🧪 Testing

### Run All Tests
```bash
# Unit tests with coverage
pytest tests/unit/ -v --cov=backend --cov-report=html

# Integration tests
pytest tests/integration/ -v

# All tests
pytest -v --cov=backend --cov-report=html --cov-report=term-missing
```

### Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

### Code Quality
```bash
# Format code
black backend/ tests/
isort backend/ tests/

# Lint code
flake8 backend/ tests/

# Type checking
mypy backend/

# Security scan
bandit -r backend/
```

## 🌐 API Documentation

### Endpoints

#### Health Check
- `GET /` - System health check

#### Students
- `POST /api/students/` - Create new student

### Request/Response Examples

#### Create Student
```bash
curl -X POST "http://localhost:8000/api/students/" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "date_of_birth": "2000-01-15",
    "address": "123 Main St, Anytown, USA"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Student John Doe created successfully",
  "data": {
    "id": 1,
    "student_id": "STU001",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "date_of_birth": "2000-01-15",
    "address": "123 Main St, Anytown, USA",
    "enrollment_date": "2024-08-23",
    "created_at": "2024-08-23T14:30:00Z",
    "updated_at": "2024-08-23T14:30:00Z"
  }
}
```

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Application
APP_ENV=development
APP_NAME=Class Management System
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_TYPE=sqlite  # or mongodb
SQLITE_DATABASE_URL=sqlite:///./class_management.db
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=class_management

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
```

See `.env.example` for complete configuration options.

### Database Configuration

#### SQLite (Development)
```bash
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./class_management.db
```

#### MongoDB (Production)
```bash
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=class_management
```

#### MongoDB Atlas (Cloud)
```bash
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE_NAME=class_management
```

## 🚢 Deployment

### Docker Production Deployment

1. **Prepare Production Environment**
```bash
cp .env.example .env.prod
# Edit .env.prod with production values
```

2. **Deploy with Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Enable HTTPS (Production)**
```bash
# Add SSL certificates to nginx/ssl/
# Update nginx/prod.conf with SSL configuration
```

### Cloud Deployment Options

#### AWS ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
docker build -t class-management .
docker tag class-management:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/class-management:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/class-management:latest
```

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy class-management \
  --image gcr.io/PROJECT-ID/class-management \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Monitoring & Logging

### Health Checks
- Backend: `http://localhost:8000/`
- Frontend: `http://localhost:8501/_stcore/health`
- Database: Automatic health checks in Docker Compose

### Monitoring Stack (Optional)
```bash
# Enable monitoring services
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

### Logs
```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View all logs
docker-compose logs -f
```

## 🤝 Contributing

### Development Workflow

1. **Fork and Clone**
```bash
git clone https://github.com/HoaNQ98/class-management.git
cd class-management
```

2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

4. **Make Changes and Test**
```bash
# Run tests
pytest -v --cov=backend

# Check code quality
black --check backend/ tests/
flake8 backend/ tests/
mypy backend/
```

5. **Submit Pull Request**
```bash
git push origin feature/your-feature-name
# Create PR through GitHub interface
```

### Code Standards

- **Code Style**: Black formatting, isort for imports
- **Type Hints**: Full type annotations required
- **Documentation**: Comprehensive docstrings
- **Testing**: Minimum 80% test coverage
- **Security**: No secrets in code, security scanning required

## 📋 API Reference

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication (Future)
```bash
# JWT Token Authentication (planned)
Authorization: Bearer <jwt-token>
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check database service status
docker-compose ps

# Restart database service
docker-compose restart mongodb
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000
kill -9 <PID>

# Or use different ports in .env
API_PORT=8001
STREAMLIT_SERVER_PORT=8502
```

#### Import Errors
```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Or install in development mode
pip install -e .
```

### Performance Optimization

#### Database Optimization
```bash
# MongoDB indexes are created automatically
# For custom indexes, modify mongo_connection.py

# SQLite optimization
SQLITE_ECHO=false  # Disable query logging in production
```

#### Docker Optimization
```bash
# Multi-stage builds reduce image size
# Production images run as non-root user
# Health checks ensure service availability
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Development Team** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Streamlit for the intuitive frontend framework
- Docker for containerization support
- GitHub Actions for CI/CD pipeline

## 📞 Support

For support and questions:
- Create an issue: [GitHub Issues](https://github.com/yourusername/class-management/issues)
- Email: support@classmanagement.com
- Documentation: [Project Wiki](https://github.com/yourusername/class-management/wiki)

---

**Built with ❤️ using modern Python technologies**