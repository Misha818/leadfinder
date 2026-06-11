from datetime import datetime
import json
from app.models import db

class Search(db.Model):
    """Search model storing queries, locations, filters, and state metadata."""
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    query = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, in_progress, completed, failed
    results_count = db.Column(db.Integer, default=0, nullable=False)

    # Nickname or custom label for the search transaction
    label = db.Column(db.String(100), nullable=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    # Store filters applied as JSON string
    _filters = db.Column('filters', db.Text, nullable=True, default='{}')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    businesses = db.relationship('Business', backref='search', lazy=True)

    @property
    def filters(self):
        """Getter for the JSON filters."""
        if self._filters:
            try:
                return json.loads(self._filters)
            except ValueError:
                return {}
        return {}

    @filters.setter
    def filters(self, val):
        """Setter to serialize python dict to JSON string."""
        if val is None:
            self._filters = '{}'
        else:
            self._filters = json.dumps(val)

    def __repr__(self):
        return f'<Search {self.label or self.query} in {self.location}>'
    body = ""
