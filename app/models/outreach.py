from datetime import datetime
from app.models import db

class ContactHistory(db.Model):
    """ContactHistory model tracking outreach interactions with a lead."""
    __tablename__ = 'contact_history'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False)
    contact_type = db.Column(db.String(30), nullable=False)  # email, call, in_person, linkedin, etc.
    outcome = db.Column(db.String(100), nullable=True)
    contacted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ContactHistory {self.contact_type} (Biz ID: {self.business_id})>'


class Note(db.Model):
    """Note model to store general textual descriptions and notes about a lead."""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Note (Biz ID: {self.business_id})>'
