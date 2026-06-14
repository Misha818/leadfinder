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

    # Google Places API configurations
    GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', '').strip()
    DATA_PROVIDER = os.environ.get('DATA_PROVIDER', 'mock').strip().lower()

    # Google Cloud Platform Billing configurations
    GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '').strip()
    GOOGLE_BILLING_ACCOUNT_ID = os.environ.get('GOOGLE_BILLING_ACCOUNT_ID', '').strip()

    @classmethod
    def validate(cls):
        """Raises a ValueError at startup if google provider is set but key is missing."""
        if cls.DATA_PROVIDER == 'google' and not cls.GOOGLE_PLACES_API_KEY:
            raise ValueError(
                "CRITICAL STARTUP ERROR: DATA_PROVIDER is configured to 'google' in your .env, "
                "but GOOGLE_PLACES_API_KEY is empty or missing. "
                "Add a valid GOOGLE_PLACES_API_KEY inside your .env file."
            )
