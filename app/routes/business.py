import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db
from app.models.business import Business, BusinessScore
from app.models.outreach import ContactHistory, Note
from app.services.ai_service import AIService
from datetime import datetime

logger = logging.getLogger('company_finder')
business_bp = Blueprint('business', __name__, url_prefix='/business')

@business_bp.route('/<int:business_id>')
def business_detail(business_id):
    """Renders the comprehensive profile management console for a single business lead."""
    business = Business.query.get_or_404(business_id)
    # Fetch notes in reverse chronological order
    notes = Note.query.filter_by(business_id=business.id).order_by(Note.created_at.desc()).all()
    # Fetch contact history
    history = ContactHistory.query.filter_by(business_id=business.id).order_by(ContactHistory.contacted_at.desc()).all()

    # Call AI-Assisted Opportunity Analyst
    ai_analysis = AIService.generate_opportunity_analysis(
        business_name=business.name,
        category=business.search.query if business.search else "Local Business",
        score=business.score.score if business.score else 0,
        has_website=business.score.has_website if business.score else False
    )

    return render_template(
        'business_detail.html',
        business=business,
        score=business.score,
        notes=notes,
        history=history,
        ai_analysis=ai_analysis
    )

@business_bp.route('/<int:business_id>/status', methods=['POST'])
def update_status(business_id):
    """Updates a lead's outreach workflow status in SQLite."""
    business = Business.query.get_or_404(business_id)
    new_status = request.form.get('status')

    # Validation against supported workflow states
    valid_statuses = ['lead', 'contacted', 'not_interested', 'website_exists', 'meeting_booked', 'closed_won', 'closed_lost']
    if new_status in valid_statuses:
        try:
            business.status = new_status
            db.session.commit()
            logger.info(f"Updated lead status for Biz ID {business_id} to '{new_status}'")
            flash(f"Lead status successfully updated to '{new_status.replace('_', ' ').capitalize()}'!", "success")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating lead status for Biz ID {business_id}: {str(e)}")
            flash(f"Database error while saving status: {str(e)}", "danger")
    else:
        flash("Invalid status selected!", "danger")

    return redirect(url_for('business.business_detail', business_id=business.id))

@business_bp.route('/<int:business_id>/note', methods=['POST'])
def add_note(business_id):
    """Saves a personal note to the SQLite notes table."""
    business = Business.query.get_or_404(business_id)
    content = request.form.get('content', '').strip()

    if content:
        try:
            new_note = Note(business_id=business.id, content=content)
            db.session.add(new_note)
            db.session.commit()
            logger.info(f"Added new note to Biz ID {business_id}")
            flash("Personal note successfully saved!", "success")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving note for Biz ID {business_id}: {str(e)}")
            flash(f"Database error while saving note: {str(e)}", "danger")
    else:
        flash("Note content cannot be empty!", "warning")

    return redirect(url_for('business.business_detail', business_id=business.id))

@business_bp.route('/<int:business_id>/contact', methods=['POST'])
def add_contact_log(business_id):
    """Logs an outreach interaction event in SQLite ContactHistory."""
    business = Business.query.get_or_404(business_id)
    contact_type = request.form.get('contact_type')
    outcome = request.form.get('outcome', '').strip()

    if contact_type:
        try:
            log = ContactHistory(
                business_id=business.id,
                contact_type=contact_type,
                outcome=outcome if outcome else "No immediate reply."
            )
            db.session.add(log)

            # Automatically advance business state to 'contacted' if it was a raw 'lead'
            if business.status == 'lead':
                business.status = 'contacted'

            db.session.commit()
            logger.info(f"Logged outreach ({contact_type}) for Biz ID {business_id}")
            flash(f"Logged outreach ({contact_type.capitalize()}) successfully!", "success")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error logging outreach for Biz ID {business_id}: {str(e)}")
            flash(f"Database error while logging outreach: {str(e)}", "danger")
    else:
        flash("Outreach contact method is required!", "warning")

    return redirect(url_for('business.business_detail', business_id=business.id))
