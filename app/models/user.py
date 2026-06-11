from datetime import datetime
from app.models import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for authentication and owner tracking."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies given password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
