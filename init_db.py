import os
from app import create_app
from app.models import db

def initialize_database():
    """Initializes SQLite database and tables based on SQLAlchemy models."""
    app = create_app()

    print("=" * 50)
    print("Initializing Company Finder Local Database...")
    print("=" * 50)

    with app.app_context():
        # Ensure the instance directory exists for SQLite
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, 'company_finder.db')
        print(f"Database location: {db_path}")

        print("Creating all tables defined in models...")
        db.create_all()
        print("Database tables created successfully!")
        print("=" * 50)

if __name__ == '__main__':
    initialize_database()
