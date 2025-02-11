class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        # Werkzeug's generate_password_hash uses pbkdf2:sha256 by default
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)