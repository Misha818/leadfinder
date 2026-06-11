from datetime import datetime
from app.models import db

class Project(db.Model):
    """Project model to organize lead searches and target businesses."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    searches = db.relationship('Search', backref='project', lazy=True, cascade='all, delete-orphan')
    businesses = db.relationship('Business', backref='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.name}>'
