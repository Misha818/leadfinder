from datetime import datetime
from app.models import db

class ApiUsage(db.Model):
    """ApiUsage model tracking Places API and crawler usage and estimated costs."""
    __tablename__ = 'api_usage'

    id = db.Column(db.Integer, primary_key=True)
    request_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # SKU tier category used (basic, contact, atmosphere)
    sku_tier = db.Column(db.String(30), nullable=False)

    estimated_cost_usd = db.Column(db.Float, default=0.0, nullable=False)

    # Comma-separated list of Places API fields requested (e.g., "name,formatted_address,website")
    fields_requested = db.Column(db.String(256), nullable=False)

    # Month of billing in "YYYY-MM" format for fast index lookups and monthly capping
    billing_month = db.Column(db.String(7), nullable=False, index=True)

    # Whether the request was approved (either within free tier or manually authorized)
    was_approved = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<ApiUsage {self.sku_tier} Cost: ${self.estimated_cost_usd:.4f} Month: {self.billing_month}>'
