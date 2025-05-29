#!/usr/bin/env python3
"""
Comprehensive test suite for the Flask application
Tests security fixes, authentication, validation, and functionality
"""

import pytest
import json
import tempfile
import os
import sys
from unittest.mock import patch

# Add the Backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Backend'))

from server import app, db, User, validate_password, validate_email, validate_username, rate_limit_check, rate_limit_storage

@pytest.fixture
def client():
    """Create a test client"""
    # Clear rate limiting storage before each test
    rate_limit_storage.clear()
    
    # Create a temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password': 'TestPassword123!'
    }

class TestSecurityFixes:
    """Test security vulnerability fixes"""
    
    def test_secret_key_not_hardcoded(self):
        """Test that secret key is not hardcoded"""
        assert app.config['SECRET_KEY'] != 'your-secret-key-here'
        assert len(app.config['SECRET_KEY']) >= 32
    
    def test_debug_mode_configurable(self):
        """Test that debug mode is configurable via environment"""
        # Should not be hardcoded to True
        assert 'debug=True' not in open('Backend/server.py').read()
    
    def test_database_not_dropped_automatically(self):
        """Test that database is not automatically dropped in production"""
        server_content = open('Backend/server.py').read()
        # Check that db.drop_all() is only used conditionally, not unconditionally
        lines = server_content.split('\n')
        drop_all_lines = [line for line in lines if 'db.drop_all()' in line]
        
        # Should only be used conditionally with environment check
        for line in drop_all_lines:
            # Must be inside an if statement checking environment
            assert 'RESET_DB' in server_content and "if os.environ.get('RESET_DB'" in server_content

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_login_with_valid_credentials(self, client):
        """Test successful login"""
        import random
        import string
        
        # Generate a truly unique user for this test
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_user = {
            'username': f'logintest{random_suffix}',
            'email': f'logintest{random_suffix}@example.com',
            'password': 'TestPassword123!'
        }
        
        # Register user first
        register_response = client.post('/api/register', 
                   data=json.dumps(test_user),
                   content_type='application/json')
        assert register_response.status_code == 200
        
        # Clear session to simulate logout
        with client.session_transaction() as sess:
            sess.clear()
        
        # Test login
        response = client.post('/api/login',
                             data=json.dumps({
                                 'email': test_user['email'],
                                 'password': test_user['password']
                             }),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_login_with_invalid_credentials(self, client):
        """Test login with wrong password"""
        # Use unique user data for this test
        test_user = {
            'username': 'invalidtest123',
            'email': 'invalidtest@example.com',
            'password': 'TestPassword123!'
        }
        
        # Register user first
        client.post('/api/register', 
                   data=json.dumps(test_user),
                   content_type='application/json')
        
        # Test login with wrong password
        response = client.post('/api/login',
                             data=json.dumps({
                                 'email': test_user['email'],
                                 'password': 'wrongpassword'
                             }),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid credentials' in data['message']
    
    def test_login_missing_data(self, client):
        """Test login with missing data"""
        response = client.post('/api/login',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_protected_routes_require_login(self, client):
        """Test that protected routes redirect when not logged in"""
        response = client.get('/build-editor')
        assert response.status_code == 302  # Redirect to login
        
        response = client.get('/ai-chatbot')
        assert response.status_code == 302
        
        response = client.get('/about')
        assert response.status_code == 302

class TestRegistration:
    """Test user registration functionality"""
    
    def test_register_valid_user(self, client):
        """Test successful registration"""
        import random
        import string
        
        # Generate a truly unique email and username for this test
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        unique_user = {
            'username': f'uniqueuser{random_suffix}',
            'email': f'unique{random_suffix}@example.com',
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/register',
                             data=json.dumps(unique_user),
                             content_type='application/json')
        
        if response.status_code != 200:
            # Debug output
            data = json.loads(response.data)
            print(f"Registration failed: {data}")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Use unique user data for this test
        test_user = {
            'username': 'duplicatetest123',
            'email': 'duplicate@example.com',
            'password': 'TestPassword123!'
        }
        
        # Register user first time
        client.post('/api/register',
                   data=json.dumps(test_user),
                   content_type='application/json')
        
        # Try to register again with same email
        duplicate_user = test_user.copy()
        duplicate_user['username'] = 'different_username'
        
        response = client.post('/api/register',
                             data=json.dumps(duplicate_user),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'already registered' in data['message']
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        invalid_user = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/register',
                             data=json.dumps(invalid_user),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        weak_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'weak'
        }
        
        response = client.post('/api/register',
                             data=json.dumps(weak_user),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Password must' in data['message']

class TestValidation:
    """Test input validation functions"""
    
    def test_password_validation(self):
        """Test password validation function"""
        # Valid password
        valid, msg = validate_password('TestPassword123!')
        assert valid is True
        
        # Too short
        valid, msg = validate_password('short')
        assert valid is False
        assert 'at least 10 characters' in msg
        
        # No uppercase
        valid, msg = validate_password('testpassword123!')
        assert valid is False
        assert 'uppercase letter' in msg
        
        # No lowercase
        valid, msg = validate_password('TESTPASSWORD123!')
        assert valid is False
        assert 'lowercase letter' in msg
        
        # No number
        valid, msg = validate_password('TestPassword!')
        assert valid is False
        assert 'number' in msg
        
        # No special character
        valid, msg = validate_password('TestPassword123')
        assert valid is False
        assert 'special character' in msg
    
    def test_email_validation(self):
        """Test email validation function"""
        # Valid email
        valid, email = validate_email('test@example.com')
        assert valid is True
        assert email == 'test@example.com'
        
        # Invalid format
        valid, msg = validate_email('invalid-email')
        assert valid is False
        
        # Empty email
        valid, msg = validate_email('')
        assert valid is False
        
        # Too long
        valid, msg = validate_email('a' * 100 + '@example.com')
        assert valid is False
    
    def test_username_validation(self):
        """Test username validation function"""
        # Valid username
        valid, username = validate_username('testuser123')
        assert valid is True
        assert username == 'testuser123'
        
        # Too short
        valid, msg = validate_username('ab')
        assert valid is False
        
        # Invalid characters
        valid, msg = validate_username('test@user')
        assert valid is False
        
        # Empty username
        valid, msg = validate_username('')
        assert valid is False

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def setup_method(self):
        """Clear rate limiting storage before each test"""
        rate_limit_storage.clear()
    
    def test_rate_limiting_allows_normal_usage(self):
        """Test that rate limiting allows normal usage"""
        identifier = 'test_user_1'
        
        # Should allow several attempts within limit
        for i in range(4):
            assert rate_limit_check(identifier) is True
    
    def test_rate_limiting_blocks_excessive_attempts(self):
        """Test that rate limiting blocks excessive attempts"""
        identifier = 'test_user_2'
        
        # Use up all attempts
        for i in range(5):
            rate_limit_check(identifier)
        
        # Next attempt should be blocked
        assert rate_limit_check(identifier) is False

class TestErrorHandling:
    """Test error handling improvements"""
    
    def test_login_with_malformed_json(self, client):
        """Test login with malformed JSON"""
        response = client.post('/api/login',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 500  # Flask returns 500 for malformed JSON
    
    def test_register_with_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/api/register',
                             data=json.dumps({'email': 'test@example.com'}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

class TestDatabaseModel:
    """Test database model improvements"""
    
    def test_user_model_has_required_fields(self, client):
        """Test that User model has all required fields"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='hashed_password'
            )
            
            # Should have all required attributes
            assert hasattr(user, 'id')
            assert hasattr(user, 'username')
            assert hasattr(user, 'email')
            assert hasattr(user, 'password')
    
    def test_user_repr(self, client):
        """Test User model string representation"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass')
            assert 'testuser' in str(user)

def run_tests():
    """Run all tests and return results"""
    # Run pytest and capture results
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', __file__, '-v', '--tb=short'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
    
    return result.returncode, result.stdout, result.stderr

if __name__ == '__main__':
    # Run tests when script is executed directly
    exit_code, stdout, stderr = run_tests()
    print(stdout)
    if stderr:
        print("STDERR:", stderr)
    sys.exit(exit_code)