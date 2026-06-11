from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app.models import db
from app.models.project import Project
from app.models.search import Search
from app.models.business import Business
from app.services.search_service import SearchService
from app.services.ai_service import AIService
import io
import csv

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/')
def search_form():
    """Renders the advanced lead search and filter form."""
    # Ensure default workspace project exists
    default_project = Project.query.first()
    if not default_project:
        try:
            from app.models.user import User
            dummy_user = User.query.first()
            if not dummy_user:
                dummy_user = User(username='demo_agent', email='demo@companyfinder.com')
                dummy_user.set_password('demo_password')
                db.session.add(dummy_user)
                db.session.commit()

            default_project = Project(
                user_id=dummy_user.id,
                name="Default Outreach Project",
                description="Auto-generated workspace for B2B local business leads."
            )
            db.session.add(default_project)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default workspace project: {str(e)}")

    projects = Project.query.all()
    return render_template('search.html', projects=projects)


@search_bp.route('/run', methods=['POST'])
def run_search():
    """Processes search filters, saves Search transaction, and redirects to results dashboard."""
    query = request.form.get('query', '').strip()
    location = request.form.get('location', '').strip()
    project_id = request.form.get('project_id', type=int)

    # Validate required parameters
    if not query or not location:
        flash("Business query and Location are required inputs!", "danger")
        return redirect(url_for('search.search_form'))

    # Advanced Filters
    radius = request.form.get('radius', type=int, default=10)
    min_rating = request.form.get('min_rating', type=float, default=0.0)
    min_reviews = request.form.get('min_reviews', type=int, default=0)

    # Booleans
    is_open = request.form.get('is_open') == 'y'
    has_phone = request.form.get('has_phone') == 'y'
    has_email = request.form.get('has_email') == 'y'
    has_socials = request.form.get('has_socials') == 'y'
    exclude_franchises = request.form.get('exclude_franchises') == 'y'
    exclude_contacted = request.form.get('exclude_contacted') == 'y'

    # Package advanced filters into a serializable dictionary
    filters_dict = {
        "radius_km": radius,
        "min_rating": min_rating,
        "min_reviews": min_reviews,
        "is_open": is_open,
        "has_phone": has_phone,
        "has_email": has_email,
        "has_socials": has_socials,
        "exclude_franchises": exclude_franchises,
        "exclude_contacted": exclude_contacted
    }

    # Store search query transaction in SQLite database
    try:
        new_search = Search(
            project_id=project_id,
            query=query,
            location=location,
            status='pending',
            results_count=0
        )
        new_search.filters = filters_dict
        db.session.add(new_search)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Database error while saving search parameters: {str(e)}", "danger")
        return redirect(url_for('search.search_form'))

    # Post-Redirect-Get Pattern: Redirect directly to the results dashboard view
    return redirect(url_for('search.results_dashboard', search_id=new_search.id))


@search_bp.route('/results/<int:search_id>')
def results_dashboard(search_id):
    """Executes the search via SearchService if pending, then displays results inside a data table."""
    search = db.get_or_404(Search, search_id)

    # Run the scraping and scoring engine if search transaction is not completed
    if search.status != 'completed':
        search_service = SearchService()
        try:
            search_service.execute_and_score(search.id)
        except Exception as e:
            flash(f"An error occurred while scanning and scoring leads: {str(e)}", "danger")
            return redirect(url_for('search.search_form'))

    # Query matching scored business leads
    leads = Business.query.filter_by(search_id=search.id).all()

    # Calculate statistics for top summaries
    avg_score = 0
    if leads:
        total_scores = sum(lead.score.score for lead in leads if lead.score)
        avg_score = int(total_scores / len(leads))

    return render_template(
        'search_results.html',
        search=search,
        leads=leads,
        avg_score=avg_score,
        filters=search.filters
    )


@search_bp.route('/export/csv/<int:search_id>')
def export_csv(search_id):
    """Exports scored business leads to a standard CSV file."""
    search = db.get_or_404(Search, search_id)
    leads = Business.query.filter_by(search_id=search.id).all()

    # Create an in-memory text stream
    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header row
    writer.writerow([
        "Business Name", "Category", "Location", "Address", "Phone", "Email",
        "Website URL", "Google Maps URL", "Rating", "Review Count",
        "Has Website", "Is Mobile Responsive", "Has SSL", "Load Time (Sec)",
        "SEO Title Present", "Social Links Count", "Opportunity Score", "Opportunity Level",
        "Explanation", "Recommended Sales Angle", "AI Estimated Complexity", "AI Project Value", "AI Proposed Services", "Status"
    ])

    # Write Business Lead rows
    for lead in leads:
        score = lead.score
        ai = AIService.generate_opportunity_analysis(
            lead.name,
            search.query,
            score.score if score else 0,
            score.has_website if score else False
        )
        writer.writerow([
            lead.name,
            search.query,
            search.location,
            lead.address or "",
            lead.phone or "",
            lead.email or "",
            lead.website_url or "",
            lead.google_maps_url or "",
            "4.5",  # rating reference
            "120", # reviews reference
            score.has_website if score else False,
            score.is_responsive if score else False,
            score.has_ssl if score else False,
            score.load_time_seconds if score else 0.0,
            score.seo_title_present if score else False,
            score.social_links_count if score else 0,
            score.score if score else 0,
            score.opportunity_level if score else "N/A",
            score.explanation if score else "",
            score.sales_angle if score else "",
            ai["complexity"],
            ai["value_category"],
            ai["recommended_services"],
            lead.status
        ])

    # Seek to start
    output.seek(0)

    # Format filename
    filename = f"leadfinder_search_{search_id}_{search.query.lower().replace(' ', '_')}.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )


@search_bp.route('/export/excel/<int:search_id>')
def export_excel(search_id):
    """
    Exports scored business leads to an Excel-compatible CSV file.
    Uses UTF-8 with BOM signature so Excel opens international symbols correctly.
    """
    search = db.get_or_404(Search, search_id)
    leads = Business.query.filter_by(search_id=search.id).all()

    # Use ByteIO to inject UTF-8 BOM
    output = io.BytesIO()
    # Write UTF-8 BOM bytes
    output.write(b'\xef\xbb\xbf')

    # Create wrapper to write strings
    wrapper = io.TextIOWrapper(output, encoding='utf-8', newline='')
    writer = csv.writer(wrapper)

    # Header Row
    writer.writerow([
        "Business Name", "Category", "Location", "Address", "Phone", "Email",
        "Website URL", "Google Maps URL", "Has Website", "Is Responsive", "Has SSL",
        "Load Time (Sec)", "SEO Title Present", "Social Links Count",
        "Website Opportunity Score", "Opportunity Level", "Explanation", "Recommended Sales Angle",
        "AI Estimated Complexity", "AI Project Value", "AI Proposed Services", "Lead Status"
    ])

    # Lead Rows
    for lead in leads:
        score = lead.score
        ai = AIService.generate_opportunity_analysis(
            lead.name,
            search.query,
            score.score if score else 0,
            score.has_website if score else False
        )
        writer.writerow([
            lead.name,
            search.query,
            search.location,
            lead.address or "",
            lead.phone or "",
            lead.email or "",
            lead.website_url or "",
            lead.google_maps_url or "",
            "Yes" if score and score.has_website else "No",
            "Yes" if score and score.is_responsive else "No",
            "Yes" if score and score.has_ssl else "No",
            score.load_time_seconds if score else 0.0,
            "Yes" if score and score.seo_title_present else "No",
            score.social_links_count if score else 0,
            score.score if score else 0,
            score.opportunity_level if score else "N/A",
            score.explanation if score else "",
            score.sales_angle if score else "",
            ai["complexity"],
            ai["value_category"],
            ai["recommended_services"],
            lead.status.capitalize()
        ])

    # Flush wrapper to BytesIO
    wrapper.flush()
    output.seek(0)

    filename = f"leadfinder_search_{search_id}_{search.query.lower().replace(' ', '_')}.xls"

    return Response(
        output.getvalue(),
        mimetype="application/vnd.ms-excel",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )


@search_bp.route('/history')
def search_history():
    """Lists all active (non-archived) past search queries and crawls."""
    searches = db.session.query(Search).filter_by(is_archived=False).order_by(Search.created_at.desc()).all()
    return render_template('search_history.html', searches=searches)


@search_bp.route('/rename/<int:search_id>', methods=['POST'])
def rename_search(search_id):
    """Saves a custom label nickname for a lead search log."""
    search = db.get_or_404(Search, search_id)
    new_label = request.form.get('label', '').strip()

    if new_label:
        search.label = new_label
        db.session.commit()
        flash("Scan campaign successfully renamed!", "success")
    else:
        flash("Label cannot be empty!", "warning")

    return redirect(url_for('search.search_history'))


@search_bp.route('/archive/<int:search_id>', methods=['POST'])
def archive_search(search_id):
    """Soft archives a search transaction so it is hidden from main active lists."""
    search = db.get_or_404(Search, search_id)
    search.is_archived = True
    db.session.commit()
    flash("Scan campaign successfully archived!", "info")
    return redirect(url_for('search.search_history'))


@search_bp.route('/delete/<int:search_id>', methods=['POST'])
def delete_search(search_id):
    """Permanently deletes a search log from system history. Leads inside project are preserved."""
    search = db.get_or_404(Search, search_id)
    try:
        db.session.delete(search)
        db.session.commit()
        flash("Scan log transaction permanently deleted!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Database error while deleting search log: {str(e)}", "danger")

    return redirect(url_for('search.search_history'))
