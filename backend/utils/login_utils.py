import datetime
from dotenv import load_dotenv
import os
from flask_mail import Mail, Message
import jwt
import secrets
from datetime import datetime, timedelta
from base64 import urlsafe_b64encode

load_dotenv()
APP_URL = os.getenv("APP_URL")
SENDER_EMAIL = os.getenv("MAIL_DEFAULT_SENDER")

def validate_email(email):
    """Basic email format validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Ensure password meets security requirements"""
    password_message = ""
    if len(password) < 8:
        return "Your password is not long enough."
    # Check for at least one uppercase, lowercase, number, and special character
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    cond_and_msg = [
        [has_upper, "An uppercase character"],
        [has_lower, "A lowercase character"],
        [has_digit, "A digit"],
        [has_special, "A special character"]
    ]

    for cond, msg in cond_and_msg:
        if not cond:
            if len(password_message) == 0:
                password_message = f"Your password is missing the following: {msg}"
            else:
                password_message = password_message + (", " + msg.lower())
    return password_message




def send_verification_email(email, token, mail):
    verification_url = f"{APP_URL}verify-email?token={token}"

    msg = Message("Verify Your Email",
                  sender=SENDER_EMAIL,
                  recipients=[email])
    msg.body = f"Please click the following link to verify your email: {verification_url}"

    mail.send(msg)

def generate_access_token(user_id,app):
    """Generate a JWT token for the user"""
    return jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.utcnow() + datetime.timedelta(hours=24)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

if __name__ == "__main__":
    print(validate_password("nnnathan"))
    print(validate_password("Nnnathan"))
    print(validate_password("Nnn4than"))
    print(validate_password("Nnn4than!"))