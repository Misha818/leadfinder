from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Renders the main SaaS application dashboard."""
    # Simulation stats for mockup rendering
    stats = {
        "total_projects": 3,
        "total_searches": 12,
        "total_businesses": 145,
        "no_website_count": 87,
        "weak_website_count": 42,
        "avg_opportunity_score": 78
    }

    # Simulation recent leads
    recent_leads = [
        {"name": "Joe's Auto Repair", "city": "Denver, CO", "phone": "303-555-0199", "score": 95, "status": "lead", "has_website": False},
        {"name": "Apex Dental", "city": "Denver, CO", "phone": "303-555-0144", "score": 82, "status": "contacted", "has_website": True},
        {"name": "Green Valley Landscaping", "city": "Aurora, CO", "phone": "720-555-0122", "score": 100, "status": "lead", "has_website": False},
        {"name": "Bella Italia Pizzeria", "city": "Boulder, CO", "phone": "303-555-0188", "score": 45, "status": "meeting_booked", "has_website": True}
    ]

    return render_template('dashboard.html', stats=stats, recent_leads=recent_leads)
