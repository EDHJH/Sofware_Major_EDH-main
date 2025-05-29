#!/usr/bin/env python3
"""
Simple startup test to verify the application can run
"""

import sys
import os
import tempfile

# Add the Backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Backend'))

def test_app_startup():
    """Test that the app can start without errors"""
    try:
        from server import app, db, init_db
        
        # Configure for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            # Initialize database
            init_db()
            
            # Test that we can create a user
            from server import User
            user = User(
                username='testuser',
                email='test@example.com',
                password='hashed_password'
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            found_user = User.query.filter_by(email='test@example.com').first()
            assert found_user is not None
            assert found_user.username == 'testuser'
            
            print("✓ App startup test passed")
            return True
            
    except Exception as e:
        print(f"✗ App startup test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_app_startup()
    sys.exit(0 if success else 1)