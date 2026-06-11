from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db
from app.models.project import Project
from app.models.business import Business
from app.models.search import Search

project_bp = Blueprint('project', __name__, url_prefix='/project')

@project_bp.route('/')
def list_projects():
    """Lists all active B2B outreach projects and workspaces."""
    projects = Project.query.all()

    # Calculate quick counts for card displays
    project_stats = []
    for proj in projects:
        total_leads = Business.query.filter_by(project_id=proj.id).count()
        contacted_leads = Business.query.filter_by(project_id=proj.id).filter(Business.status != 'lead').count()
        project_stats.append({
            "project": proj,
            "total_leads": total_leads,
            "contacted_leads": contacted_leads
        })

    return render_template('projects.html', project_stats=project_stats)


@project_bp.route('/new', methods=['POST'])
def create_project():
    """Creates a new Project workspace in SQLite."""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash("Workspace Name is a required field!", "danger")
        return redirect(url_for('project.list_projects'))

    try:
        # Check for active user, create dummy if none exists
        from app.models.user import User
        demo_user = User.query.first()
        if not demo_user:
            demo_user = User(username='demo_agent', email='demo@companyfinder.com')
            demo_user.set_password('demo_password')
            db.session.add(demo_user)
            db.session.commit()

        new_proj = Project(
            user_id=demo_user.id,
            name=name,
            description=description if description else "Workspace for local business outreach campaigns."
        )
        db.session.add(new_proj)
        db.session.commit()
        flash(f"Workspace project '{name}' successfully created!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Database error while creating workspace: {str(e)}", "danger")

    return redirect(url_for('project.list_projects'))


@project_bp.route('/<int:project_id>')
def project_dashboard(project_id):
    """Renders comprehensive conversion funnel and analytics for a single project."""
    project = Project.query.get_or_404(project_id)
    leads = Business.query.filter_by(project_id=project.id).all()
    searches = db.session.query(Search).filter_by(project_id=project.id, is_archived=False).all()

    # Funnel and Conversion metrics
    total_leads = len(leads)
    high_opportunity = 0
    contacted_count = 0
    meeting_booked = 0
    closed_won = 0
    closed_lost = 0
    not_interested = 0
    website_exists = 0

    for lead in leads:
        # Count high-opportunity scores (>= 70)
        if lead.score and lead.score.score >= 70:
            high_opportunity += 1

        # Count outreach statuses
        if lead.status == 'contacted':
            contacted_count += 1
        elif lead.status == 'meeting_booked':
            meeting_booked += 1
            contacted_count += 1
        elif lead.status == 'closed_won':
            closed_won += 1
            contacted_count += 1
        elif lead.status == 'closed_lost':
            closed_lost += 1
            contacted_count += 1
        elif lead.status == 'not_interested':
            not_interested += 1
            contacted_count += 1
        elif lead.status == 'website_exists':
            website_exists += 1

    # Conversion Rate: Won / Total Contacted
    total_contacted = contacted_count
    conversion_rate = 0
    if total_contacted > 0:
        conversion_rate = int((closed_won / total_contacted) * 100)

    stats = {
        "total_leads": total_leads,
        "high_opportunity": high_opportunity,
        "total_contacted": total_contacted,
        "meeting_booked": meeting_booked,
        "closed_won": closed_won,
        "closed_lost": closed_lost,
        "not_interested": not_interested,
        "website_exists": website_exists,
        "conversion_rate": conversion_rate
    }

    return render_template(
        'project_dashboard.html',
        project=project,
        leads=leads,
        searches=searches,
        stats=stats
    )
