import os
import logging
from flask import Flask
from config import Config
from app.models import db

def create_app(config_class=Config):
    """Application factory for Company Finder."""
    # Configure production-ready server logs
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    logger = logging.getLogger('company_finder')
    logger.info("Starting Company Finder application factory setup...")

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLAlchemy database connection
    db.init_app(app)
    logger.info("SQLAlchemy database connection pool established.")

    # Ensure local database directory folder exists for SQLite local instance path
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to establish SQLite instance directory path: {str(e)}")

    # Register Blueprint Controllers
    from app.routes.main import main_bp
    from app.routes.search import search_bp
    from app.routes.business import business_bp
    from app.routes.project import project_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(business_bp)
    app.register_blueprint(project_bp)
    logger.info("SaaS Blueprints registered cleanly in application context.")

    return app
