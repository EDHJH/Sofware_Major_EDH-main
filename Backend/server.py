from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps  # Add this import
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import re
import secrets
import datetime

# Update instance path
instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app = Flask(__name__,
    template_folder='../Frontend/templates',
    static_folder='../Frontend/static',
    instance_path=instance_path)

# Update the database path to be in the instance folder
db_path = os.path.join(instance_path, 'userdatabase.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', secrets.token_hex(32))

db = SQLAlchemy(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

class User(db.Model):
    __tablename__ = 'user'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)  # Changed from firstname
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')
        
        # Try to find user by email or username
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    except Exception as e:
        print(f"Login error: {str(e)}")  # Add logging
        return jsonify({'success': False, 'message': str(e)}), 500

def validate_password(password):
    if len(password) < 10:
        return False, "Password must be at least 10 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?_\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print("Received registration data:", data)  # Debug print
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'success': False, 'message': message})
            
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')  # Changed from sha256
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return jsonify({'success': True})
    except Exception as e:
        print(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

def login_required(f):
    @wraps(f)  # Add this decorator
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/build-editor')
@login_required
def build_editor():
    return render_template('build-editor.html')

@app.route('/ai-chatbot')
@login_required
def ai_chatbot():
    return render_template('ai-chatbot.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    if request.method == 'GET':
        user = User.query.get(session['user_id'])
        return jsonify({
            'username': user.username,
            'email': user.email
        })
    else:
        try:
            data = request.get_json()
            user = User.query.get(session['user_id'])
            if 'username' in data:
                user.username = data['username']
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def request_password_reset():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
            db.session.commit()
            # TODO: Send email with reset link
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Email not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Error handling middleware
@app.errorhandler(Exception)
def handle_error(error):
    code = 500
    if hasattr(error, 'code'):
        code = error.code
    return jsonify({'success': False, 'message': str(error)}), code

# Move db.create_all() into a function to ensure proper context
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")

if __name__ == '__main__':
    init_db()  # Initialize database before running the app
    app.run(debug=True)

# 1. first rename branch to feature/header-auth-etc. 
# 2. merge this branch onto main
# 3. git switch "branch name"
# 4. git pull origin main

# option 1: delete the branches outdated (not suggested). Create v2/feature/ui-improvements as an example to distinguish
# option 2: keep the branches, but git pull origin main