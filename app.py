from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
import secrets
from time import sleep
from flask import Flask, request, render_template, redirect, session, jsonify
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_mail import Mail
import os
from flask_cors import CORS, cross_origin
import logging

from functools import wraps

from backend.gpt_messaging.gpt import get_gpt_results
from backend.utils.text_extraction import extract_interview_notes, extract_job_description, extract_resume_info
from backend.utils.login_utils import send_verification_email, send_verification_email_sendgrid, validate_email, validate_password

load_dotenv()
app = Flask(__name__)

CORS(app)

"""
logging.basicConfig(
    filename='auth.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
"""

UPLOAD_FOLDER =  os.getenv("UPLOAD_FOLDER")
pg_username = os.getenv("POSTGRES_USERNAME")
pg_password = os.getenv("POSTGRES_PASSWORD")
pg_db = os.getenv("POSTGRES_DB")
pg_port = os.getenv("POSTGRES_PORT")
DEV_MODE = True
postgres_connection_string = f"postgresql://{pg_username}:{pg_password}@localhost:{pg_port}/{pg_db}"


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT"))
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = postgres_connection_string
if DEV_MODE:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

mail = Mail(app)
db = SQLAlchemy(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app
)
class Base(DeclarativeBase):
    pass
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

class GptAnalysis(db.Model):
    __tablename__ = "gptanalysis"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("appuser.id"), nullable=False)
    
    # Text fields that could be long
    satisfied_requirements = db.Column(db.JSON, nullable=True)
    unsatisfied_requirements = db.Column(db.JSON, nullable=True)
    interview_fit = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    areas_of_improvement = db.Column(db.Text, nullable=True)
    conclusion_oneline = db.Column(db.String(255), nullable=True)
    overall_conclusion = db.Column(db.Text, nullable=True)
    
    # Count fields
    strengths_count = db.Column(db.Integer, default=0)
    areas_of_improvement_count = db.Column(db.Integer, default=0)
    satisfied_requirements_count = db.Column(db.Integer, default=0)
    unsatisfied_requirements_count = db.Column(db.Integer, default=0)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.now())
with app.app_context():
    db.create_all()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/index')
def landing():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/response')
def response():
    return render_template('response.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/records')
def records():
    return render_template('records.html')

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
            if current_user.token_expiry < datetime.now():
                raise Exception('Token expired')
                
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated

def generate_access_token(user_id):
    """Generate a JWT token for the user"""
    return jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(hours=24)
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
    

    user = User.query.filter_by(email=email).first()
    if user and user.email_verified and not data.get("test"):
        logging.info(f"Failed registration attempt for email: {data.get('email')} due to email already in use")
        return jsonify({'error': 'This email is already in use. Please try again.'}), 401

    password_message = validate_password(password)
    if password_message != "":
        return jsonify({'error': password_message}), 401
    
    token = generate_verification_token()
    
    user = User(email=data['email'])
    user.set_password(data['password'])
    token = generate_verification_token()
    user.verification_token = token
    user.token_expiry = datetime.now() + timedelta(hours=24)
    try:
        if not data["test"]:
            db.session.add(user)
            db.session.commit()
        send_verification_email_sendgrid(email, token)
        
        logging.info(f"Sent login token to: {data.get('email')}")
        return jsonify({'message': 'Please check your email to verify your account'}), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': 'An error occurred during registration'}), 500

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password")):
        if not user:
            logging.warning(f"Failed login attempt for email: {data.get('email')} due to invalid email")
        else:
            logging.warning(f"Failed login attempt for email: {data.get('email')} due to invalid password")
        return jsonify({"error": "Invalid email or password."}), 401
    
    if not user.email_verified:
        return jsonify({"error": "Please verify your email."}), 401
    
    access_token = generate_access_token(user.id)
    user.token_expiry = datetime.now() + timedelta(hours=24)
    logging.info(f"Sucecssful login attempt for email: {data.get('email')}")
    return jsonify({"access_token": access_token, "user_id":user.id}), 200

@app.route("/verify-email", methods=["POST"])
def verify_email():
    token = request.args.get("token")
    user = User.query.filter_by(verification_token=token).first()
    
    if not user or user.token_expiry > datetime.now():
        if not user:
            return jsonify({"error": "Verification failed, invalid token"}), 401
        else:
            return jsonify({"error": "Verification failed, token expired"}), 401
    
    user.email_verified = True
    user.verification_token = None
    user.token_expiry = None
    db.session.commit()
    
    return ({"Success"}), 200


@app.route('/upload', methods=['POST'])
## TODO make this actually work@require_auth
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
    employment_history, educational_history, skills, certifications = extract_resume_info(saved_files["resume"])

    return jsonify({
        "requirements": requirements,
        "responsibilities": responsibilities,
        "employment_history": employment_history,
        "educational_history": educational_history,
        "skills": skills,
        "certifications": certifications,
        "strengths": strengths,
        "areas_of_improvement": areas_of_improvement,
        "job_fit": job_fit
    }), 200
    

@app.route('/analyze', methods=['POST'])
#@require_auth
def analyze_response():
    token = request.headers.get('Authorization')
    data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    current_user_id = data['user_id']
    try:
        data = request.get_json()
        employment_history = data["employment_history"]
        educational_history = data["educational_history"]
        certifications = data["certifications"]
        skills = data["skills"]
        strengths = data["strengths"]
        areas_of_improvement = data["areas_of_improvement"]
        job_fit = data["job_fit"]
        requirements = data["requirements"]
        responsibilities = data["responsibilities"]

        gpt_results = get_gpt_results((employment_history,educational_history,certifications,skills), (strengths, areas_of_improvement, job_fit), requirements, responsibilities)
        analysis = GptAnalysis(
            user_id=current_user_id,
            satisfied_requirements=gpt_results.get('satisfied_requirements', 'None'),
            unsatisfied_requirements=gpt_results.get('unsatisfied_requirements', 'None'),
            interview_fit=gpt_results.get('interview_fit', ''),
            strengths=gpt_results.get('strengths', ''),
            areas_of_improvement=gpt_results.get('areas_of_improvement', ''),
            conclusion_oneline=gpt_results.get('conclusion_oneline', ''),
            overall_conclusion=gpt_results.get('overall_conclusion', ''),
            strengths_count=gpt_results.get('strengths_count', 0),
            areas_of_improvement_count=gpt_results.get('areas_of_improvement_count', 0),
            satisfied_requirements_count=gpt_results.get('satisfied_requirements_count', 0),
            unsatisfied_requirements_count=gpt_results.get('unsatisfied_requirements_count', 0),
            created_at=datetime.now()
        )

        db.session.add(analysis)
        db.session.commit()
        return jsonify(gpt_results), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error":"An error occurred during processing"}), 401

@app.route('/get_records', methods=["GET"])
def get_records():
    token = request.headers.get('Authorization')
    data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    current_user_id = data['user_id']
    current_user = User.query.filter_by(id=current_user_id).first()

    if not current_user:
        return {"error": "User not found"}, 404
    past_analyses = GptAnalysis.query.filter_by(user_id = current_user_id).all()

    return jsonify(past_analyses), 200

if __name__ == '__main__':
    app.run(debug=True)

