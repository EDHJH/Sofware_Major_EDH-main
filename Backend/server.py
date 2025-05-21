from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__,
    template_folder='../Frontend/templates',
    static_folder='../Frontend/static')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userdatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return render_template('auth.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.password == password:  # In production, use proper password hashing
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already registered'})
    
    new_user = User(
        firstname=data['firstname'],
        lastname=data['lastname'],
        email=data['email'],
        password=data['password']  # In production, hash the password
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

@app.route('/dashboard')
def dashboard():
    return "Dashboard - Coming Soon"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)