from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
import secrets
from time import sleep
from flask import Flask, request, render_template, redirect, session, jsonify
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_mail import Mail
import os
from flask_cors import CORS, cross_origin

import wraps


from backend.gpt_messaging.gpt import get_gpt_results
from text_extraction import extract_interview_notes, extract_job_description, extract_resume_info
from utils.login_utils import send_verification_email, validate_email, validate_password

load_dotenv()
app = Flask(__name__)

CORS(app)

UPLOAD_FOLDER =  os.getenv("UPLOAD_FOLDER")
pg_username = os.getenv("POSTGRES_USERNAME")
pg_password = os.getenv("POSTGRES_PASSWORD")
pg_db = os.getenv("POSTGRES_DB")
pg_port = os.getenv("POSTGRES_PORT")
postgres_connection_string = f"postgresql://{pg_username}:{pg_password}@localhost:{pg_port}/{pg_db}"


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT"))
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = postgres_connection_string


mail = Mail(app)
db = SQLAlchemy(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app
)

class User(UserMixin, db.Model):
    __tablename__ = "appuser"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
with app.app_context():
    db.create_all()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_verification_token(length=32):
    random_bytes = secrets.token_bytes(length)
    token = urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    
    return token

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
                
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                raise Exception('User not found')
                
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated

def generate_access_token(user_id):
    """Generate a JWT token for the user"""
    return jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

@app.route('/hello', methods=["GET"])
def hello_world():
    return jsonify({'message': 'hello, world!'}), 200

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({'error': 'Please properly fill out all of the forms before submission.'}), 401

    if not validate_email(email):
        return jsonify({'error': 'Invalid email. Please try again.'}), 401

    password_message = validate_password(password)
    if password_message != "":
        return jsonify({'error': password_message}), 401
    
    token = generate_verification_token()
    #TODO this doesnt actually work
    
    user = User(email=data['email'])
    user.set_password(data['password'])
    token = generate_verification_token()
    user.verification_token = token
    user.token_expiry = datetime.now() + timedelta(hours=24)
    try:
        db.session.add(user)
        db.session.commit()
        #send_verification_email(email, token, mail)
        return jsonify({'message': 'Please check your email to verify your account'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred during registration'}), 500

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password")):
        return jsonify({"error": "Invalid email or password."}), 401
    
    if not user.email_verified:
        return jsonify({"error": "Please verify your email."}), 401
    
    access_token = generate_access_token(user.id)
    return jsonify({"access_token": access_token}), 200

@app.route("/verify-email")
def verify_email(token):
    #TODO fill this in
    pass

@app.route('/upload', methods=['POST'])
@require_auth
def upload_files():
    required_files = ['job_description', 'resume', 'interview_notes']
    missing_files = [file for file in required_files if file not in request.files]
    
    if missing_files:
        return jsonify({'error': f'Missing files: {", ".join(missing_files)}'}), 400

    saved_files = {}
    for file_key in required_files:
        file = request.files[file_key]
        if file.filename == '':
            return jsonify({'error': f'File for {file_key} is empty.'}), 400
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': f'{file_key} must be a PDF file.'}), 400

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        saved_files[file_key] = file_path

    strengths, areas_of_improvement, job_fit = extract_interview_notes(saved_files["interview_notes"])
    requirements, responsibilities = extract_job_description(saved_files["job_description"]) 
    resume_info = extract_resume_info(saved_files["resume"])
    """
    return jsonify({
        "satisfied_requirements": "b",
        "unsatisfied_requirements": "c",
        "interview_fit": "d",
        "strengths": "e",
        "areas_of_improvement": "f",
        "overall_conclusion": "g",
        "strengths_count": "1",
        "areas_of_improvement_count": "2",
        "satisfied_requirements_count": "3",
        "unsatisfied_requirements_count": "4"

    }), 200
    """
    gpt_results = get_gpt_results(resume_info, (strengths, areas_of_improvement, job_fit), requirements, responsibilities)
    return jsonify(gpt_results), 200

if __name__ == '__main__':
    app.run(debug=True)

