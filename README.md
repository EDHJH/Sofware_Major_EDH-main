# StatSouls - Ultimate Builder Platform

A comprehensive web application for Elden Ring players to create, share, and optimize character builds. Features user authentication, build editor, AI chatbot integration, and extensive wiki resources.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Security & Development](#security--development)
- [Git Workflow](#git-workflow)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## 🎯 Project Overview

StatSouls is a full-stack web application built with Flask (backend) and vanilla JavaScript (frontend) that provides Elden Ring players with tools to:
- Create and manage character builds
- Get AI-powered recommendations
- Access comprehensive game wiki information
- Share builds with the community

## ✨ Features

### 🔐 Authentication System
- Secure user registration and login
- Password strength requirements (10+ chars, uppercase, lowercase, numbers, special chars)
- Session management with CSRF protection
- Rate limiting to prevent brute force attacks

### 🏗️ Build Editor
- Interactive character build creation
- Stat allocation and optimization
- Equipment selection and management
- Build sharing and export functionality

### 🤖 AI Chatbot
- Intelligent build recommendations
- Game strategy assistance
- Interactive Q&A system

### 📚 Wiki Integration
- Direct links to Fextralife wiki
- Categorized game information (Weapons, Armor, Spells, etc.)
- Quick reference tools

### 🎨 Modern UI/UX
- Responsive design for all devices
- Dark theme with Elden Ring aesthetics
- Smooth animations and parallax effects
- Intuitive navigation

## 📁 Project Structure

```
Sofware_Major_main_Edward/
├── Backend/
│   └── server.py                 # Flask application with security fixes
├── Frontend/
│   ├── static/
│   │   ├── assets/              # Images, videos, icons
│   │   ├── css/                 # Stylesheets (auth, header, home)
│   │   └── js/                  # JavaScript (authentication logic)
│   └── templates/               # HTML templates
│       ├── auth.html            # Login/registration page
│       ├── home.html            # Dashboard
│       ├── build-editor.html    # Build creation tool
│       ├── ai-chatbot.html      # AI assistant
│       └── about.html           # About page
├── tests/                       # Comprehensive test suite
│   ├── test_app.py              # Main application tests
│   ├── test_startup.py          # Basic functionality tests
│   └── README.md                # Testing documentation
├── instance/
│   └── userdatabase.db          # SQLite database
└── README.md                    # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Dependencies
```bash
pip install flask flask-sqlalchemy flask-wtf werkzeug pytest requests
```

### Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd Sofware_Major_main_Edward

# Install dependencies
python3 -m pip install flask flask-sqlalchemy flask-wtf werkzeug pytest requests

# Set environment variables (recommended for production)
export SECRET_KEY="your-super-secret-key-here"
export FLASK_DEBUG="false"  # Set to "true" for development only
export RESET_DB="false"     # Set to "true" to reset database on startup
```

### Running the Application
```bash
# From the Backend directory
cd Backend
python3 server.py

# Or from project root
python3 Backend/server.py
```

The application will be available at `http://127.0.0.1:5000`

## 🔒 Security & Development

### Security Features
- **Environment-based configuration**: Secret keys and debug settings via environment variables
- **Input validation**: Comprehensive validation for all user inputs
- **CSRF protection**: Cross-site request forgery protection enabled
- **Rate limiting**: Prevents brute force attacks (5 attempts per 15 minutes)
- **Password hashing**: Secure password storage using PBKDF2-SHA256
- **SQL injection prevention**: Parameterized queries and ORM usage
- **XSS protection**: Input sanitization and safe error display
- **Session security**: Secure session management

### Development Practices
- **Logging**: Structured logging for debugging and monitoring
- **Error handling**: Graceful error handling with user-friendly messages
- **Database safety**: Conditional database operations, no automatic drops
- **Code organization**: Modular structure with clear separation of concerns

## 🌿 Git Workflow

The repository follows a feature-branch workflow:

### Main Branches
- **`main`**: Production-ready code with latest stable features
- **`debug/development`**: Development branch for testing and debugging

### Feature Branches
- **`feature/server-setup`**: Initial server configuration
- **`feature/authentication`**: User authentication system
- **`feature/home-page`**: Landing page and dashboard
- **`feature/header-navigation`**: Navigation and routing
- **`feature/ui-improvements`**: UI/UX enhancements

### Branch Management
```bash
# Switch to development branch
git checkout debug/development

# Create new feature branch
git checkout -b feature/new-feature

# Merge feature to development
git checkout debug/development
git merge feature/new-feature

# Deploy to main when ready
git checkout main
git merge debug/development
```

## 🧪 Testing

### Test Suite Overview
- **21 comprehensive tests** covering all major functionality
- **100% pass rate** with security vulnerability verification
- **Multiple test categories**: Security, authentication, validation, error handling

### Running Tests
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test categories
python3 -m pytest tests/test_app.py::TestSecurityFixes -v
python3 -m pytest tests/test_app.py::TestAuthentication -v

# Run with coverage (if pytest-cov installed)
python3 -m pytest tests/ --cov=Backend
```

### Test Coverage
- ✅ Security vulnerability fixes
- ✅ Authentication flows (login/register/logout)
- ✅ Input validation (email, password, username)
- ✅ Rate limiting functionality
- ✅ Error handling and edge cases
- ✅ Database operations and models
- ✅ CSRF protection verification

## 📡 API Documentation

### Authentication Endpoints

#### POST `/api/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "string (3-50 chars, alphanumeric + underscore)",
  "email": "string (valid email format)",
  "password": "string (10+ chars with requirements)"
}
```

**Response:**
```json
{
  "success": true|false,
  "message": "string (error message if failed)"
}
```

#### POST `/api/login`
Authenticate user and create session.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true|false,
  "message": "string (error message if failed)"
}
```

#### GET `/api/logout`
End user session.

**Response:**
```json
{
  "success": true
}
```

### Protected Routes
All routes require authentication (redirect to login if not authenticated):
- `/dashboard` - User dashboard
- `/build-editor` - Build creation tool
- `/ai-chatbot` - AI assistant
- `/about` - About page

### Rate Limiting
- **Login attempts**: 5 per 15 minutes per IP
- **Registration attempts**: 5 per 15 minutes per IP
- **Response**: `429 Too Many Requests` when limit exceeded

## 🛠️ Development

### Code Quality Standards
- **Input validation**: All user inputs validated and sanitized
- **Error handling**: Comprehensive error handling with logging
- **Security**: Following OWASP security guidelines
- **Testing**: All new features must include tests
- **Documentation**: Code comments and API documentation required

### Adding New Features
1. Create feature branch from `debug/development`
2. Implement feature with tests
3. Run full test suite: `python3 -m pytest tests/`
4. Update documentation if needed
5. Create pull request to `debug/development`

### Database Schema

#### User Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)  # Hashed
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Write tests** for your changes
4. **Ensure all tests pass** (`python3 -m pytest tests/`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Code Review Checklist
- [ ] All tests pass
- [ ] Security considerations addressed
- [ ] Input validation implemented
- [ ] Error handling included
- [ ] Documentation updated
- [ ] No hardcoded secrets or debug code

## 📝 Version History

- **v2.0.0** - Security hardening and comprehensive testing (Current)
  - Fixed 17 critical security vulnerabilities
  - Added comprehensive test suite (21 tests)
  - Implemented CSRF protection and rate limiting
  - Enhanced input validation and error handling

- **v1.0.0** - Initial release
  - Basic authentication system
  - Core UI components
  - Database setup
  - Feature branch structure

## 📄 License

This project is part of a Year 12 Software Development major work.

## 🆘 Support

For issues, questions, or contributions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include steps to reproduce for bugs
4. Provide environment details (OS, Python version, etc.)

---

**Built with ❤️ for the Elden Ring community**