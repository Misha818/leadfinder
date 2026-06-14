from flask_sqlalchemy import SQLAlchemy

# Initialize db instance
db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.project import Project
from app.models.search import Search
from app.models.business import Business, BusinessScore
from app.models.outreach import ContactHistory, Note
from app.models.billing import ApiUsage
