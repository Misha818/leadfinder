# System Architecture - Company Finder

## Technology Stack
- **Backend:** Python/Flask (with Flask-SQLAlchemy)
- **Database:** SQLite (SQLAlchemy ORM for ease of migration and database abstraction)
- **Frontend:** Vanilla JavaScript (no heavy frameworks like React, to keep it fast, simple, and light)
- **Styling:** Bootstrap 5 (with clean, responsive components)
- **Authentication:** Flask-Login or custom session-based secure authentication

## Folder Structure
We will adopt a modular and production-ready folder structure:
```
leadfinder/
│
├── claude_memory/          # Persistent development memory
│   ├── 1_PROJECT_GOALS.md
│   ├── 2_ARCHITECTURE.md
│   └── 3_ACTIVE_STATE.md
│
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── routes/             # Blueprints for views and APIs
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── api.py
│   ├── models/             # SQLAlchemy Database Models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── business.py
│   │   └── outreach.py
│   ├── services/           # Business logic (Scrapers, Scoring API, Exports)
│   │   ├── __init__.py
│   │   ├── search_service.py
│   │   └── scoring_service.py
│   ├── templates/          # HTML templates (Jinja2)
│   └── static/             # JS, CSS, assets
│       ├── css/
│       └── js/
│
├── requirements.txt        # Python package dependencies
├── .env                    # Environment variables (git-ignored)
├── run.py                  # Entry point script
└── instance/               # Local SQLite database directory
```

## Database Schema Requirements
We will define the following models:

1. **User**
   - `id` (PK)
   - `username` (Unique, string)
   - `email` (Unique, string)
   - `password_hash` (String, secure)
   - `created_at` (DateTime)

2. **Project**
   - `id` (PK)
   - `user_id` (FK -> User.id)
   - `name` (String)
   - `description` (Text)
   - `created_at` (DateTime)

3. **Search**
   - `id` (PK)
   - `project_id` (FK -> Project.id)
   - `query` (String, e.g., "plumber")
   - `location` (String, e.g., "Denver, CO")
   - `status` (String: pending, in_progress, completed, failed)
   - `results_count` (Integer)
   - `created_at` (DateTime)

4. **Business**
   - `id` (PK)
   - `project_id` (FK -> Project.id)
   - `search_id` (FK -> Search.id, Nullable)
   - `name` (String)
   - `address` (String)
   - `phone` (String)
   - `email` (String)
   - `website_url` (String, Nullable)
   - `google_maps_url` (String, Nullable)
   - `status` (String: lead, contacted, meeting_booked, closed_won, closed_lost)
   - `created_at` (DateTime)

5. **BusinessScore** (Website Opportunity Score metadata)
   - `id` (PK)
   - `business_id` (FK -> Business.id, Unique)
   - `score` (Integer, 0-100)
   - `has_website` (Boolean)
   - `is_responsive` (Boolean)
   - `has_ssl` (Boolean)
   - `load_time_seconds` (Float)
   - `seo_title_present` (Boolean)
   - `social_links_count` (Integer)
   - `last_scanned_at` (DateTime)

6. **ContactHistory**
   - `id` (PK)
   - `business_id` (FK -> Business.id)
   - `contact_type` (String: email, call, in_person, LinkedIn)
   - `outcome` (String)
   - `contacted_at` (DateTime)

7. **Note**
   - `id` (PK)
   - `business_id` (FK -> Business.id)
   - `content` (Text)
   - `created_at` (DateTime)
