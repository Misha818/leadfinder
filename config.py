import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration class."""
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

    # Database Config
    # Default to instance/company_finder.db if DATABASE_URL is not set
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "instance", "company_finder.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
