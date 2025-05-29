from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import re
import secrets
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# Update instance path
instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app = Flask(__name__,
    template_folder='../Frontend/templates',
    static_folder='../Frontend/static',
    instance_path=instance_path)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userdatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['WTF_CSRF_TIME_LIMIT'] = None

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting storage
rate_limit_storage = defaultdict(list)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/api/login', methods=['POST'])
def login():
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    
    # Rate limiting
    if not rate_limit_check(f"login_{client_ip}"):
        logger.warning(f"Rate limit exceeded for login from {client_ip}")
        return jsonify({'success': False, 'message': 'Too many login attempts. Please try again later.'}), 429
    
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
            
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Input validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
            
        if '@' not in email or len(email) > 100:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            logger.info(f"Successful login for user {user.username} from {client_ip}")
            return jsonify({'success': True})
        
        logger.warning(f"Failed login attempt for email {email} from {client_ip}")
        return jsonify({'success': False, 'message': 'Invalid credentials'})
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

def validate_password(password):
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    if len(password) < 10:
        return False, "Password must be at least 10 characters long"
    if len(password) > 128:
        return False, "Password must be less than 128 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?_\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def validate_email(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False, "Email is required"
    email = email.strip().lower()
    if len(email) > 100:
        return False, "Email must be less than 100 characters"
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return False, "Invalid email format"
    return True, email

def validate_username(username):
    """Validate username"""
    if not username or not isinstance(username, str):
        return False, "Username is required"
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters long"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, username

@app.route('/api/register', methods=['POST'])
def register():
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    
    # Rate limiting
    if not rate_limit_check(f"register_{client_ip}"):
        logger.warning(f"Rate limit exceeded for registration from {client_ip}")
        return jsonify({'success': False, 'message': 'Too many registration attempts. Please try again later.'}), 429
    
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
        # Validate email
        email_valid, email_or_message = validate_email(data.get('email'))
        if not email_valid:
            return jsonify({'success': False, 'message': email_or_message}), 400
        email = email_or_message
        
        # Validate username
        username_valid, username_or_message = validate_username(data.get('username'))
        if not username_valid:
            return jsonify({'success': False, 'message': username_or_message}), 400
        username = username_or_message
        
        # Validate password
        password_valid, password_message = validate_password(data.get('password'))
        if not password_valid:
            return jsonify({'success': False, 'message': password_message}), 400
        
        # Check for existing user
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'}), 409
            
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already taken'}), 409
        
        # Create new user
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        
        logger.info(f"New user registered: {username} from {client_ip}")
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred during registration'}), 500

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
@login_required
def dashboard():
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

def init_db():
    """Initialize database tables if they don't exist"""
    with app.app_context():
        # Check if we're in development and should reset DB
        if os.environ.get('RESET_DB', 'False').lower() == 'true':
            db.drop_all()
            logger.info("Database tables dropped for development")
        
        db.create_all()
        logger.info("Database tables initialized successfully")

def rate_limit_check(identifier, max_attempts=5, window_minutes=15):
    """Simple rate limiting implementation"""
    now = datetime.now(timezone.utc)
    attempts = rate_limit_storage[identifier]
    
    # Remove old attempts outside the window
    cutoff = now - timedelta(minutes=window_minutes)
    rate_limit_storage[identifier] = [attempt for attempt in attempts if attempt > cutoff]
    
    if len(rate_limit_storage[identifier]) >= max_attempts:
        return False
    
    rate_limit_storage[identifier].append(now)
    return True

if __name__ == '__main__':
    init_db()
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)