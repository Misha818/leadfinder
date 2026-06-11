from datetime import datetime
from app.models import db

class Business(db.Model):
    """Business model representing a lead within a project."""
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    search_id = db.Column(db.Integer, db.ForeignKey('searches.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    website_url = db.Column(db.String(256), nullable=True)
    google_maps_url = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(30), default='lead', nullable=False)  # lead, contacted, meeting_booked, closed_won, closed_lost

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    # One-to-One relationship with BusinessScore
    score = db.relationship('BusinessScore', backref='business', uselist=False, cascade='all, delete-orphan')

    # One-to-Many relationships
    contact_history = db.relationship('ContactHistory', backref='business', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='business', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Business {self.name}>'


class BusinessScore(db.Model):
    """BusinessScore model storing detailed website audit metrics and opportunity score."""
    __tablename__ = 'business_scores'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id', ondelete='CASCADE'), unique=True, nullable=False)

    # The calculated 0-100 score (higher means more opportunity/need for a website)
    score = db.Column(db.Integer, default=0, nullable=False)
    opportunity_level = db.Column(db.String(30), nullable=True)  # Very High, High, Medium, Low
    explanation = db.Column(db.Text, nullable=True)
    sales_angle = db.Column(db.Text, nullable=True)

    # Scoring checkpoint indicators
    has_website = db.Column(db.Boolean, default=False, nullable=False)
    is_responsive = db.Column(db.Boolean, default=False, nullable=False)
    has_ssl = db.Column(db.Boolean, default=False, nullable=False)
    load_time_seconds = db.Column(db.Float, nullable=True)
    seo_title_present = db.Column(db.Boolean, default=False, nullable=False)
    social_links_count = db.Column(db.Integer, default=0, nullable=False)

    last_scanned_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<BusinessScore {self.score} (Level: {self.opportunity_level})>'
