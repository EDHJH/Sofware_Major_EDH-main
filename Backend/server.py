from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

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
app.config["SECRET_KEY"] = "your-secret-key-here"  # Fixed secret key

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)  # Changed from firstname
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
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

# Move db.create_all() here to ensure model is defined first
with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    print("Database tables recreated successfully")  # Debug print

if __name__ == '__main__':
    app.run(debug=True)