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


@business_bp.route('/api/business/<int:business_id>/audit')
def live_reaudit_api(business_id):
    """
    Exposes a real-time JSON API executing on-demand HTTP/HTTPS audits
    and saving updated scoring metrics to local SQLite tables.
    """
    business = Business.query.get_or_404(business_id)

    try:
        from app.services.scraper_service import audit_website
        from app.services.scoring_service import ScoringService

        # 1. Run live crawler
        audit = audit_website(business.website_url)

        # Build lead dict reference for potential demand calculations
        lead_dict = {
            "name": business.name,
            "phone": business.phone,
            "email": business.email,
            "website_url": business.website_url,
            "rating": 4.5,  # static reference fallbacks
            "reviews_count": 120
        }

        # 2. Re-calculate score driven by actual scraper outputs
        score, level, explanation, sales_angle = ScoringService.calculate_advanced_score(lead_dict, audit)

        # 3. Save / Update corresponding scored leads rows inside SQLite database
        score_record = business.score
        if not score_record:
            score_record = BusinessScore(business_id=business.id)
            db.session.add(score_record)

        score_record.score = score
        score_record.opportunity_level = level
        score_record.explanation = explanation
        score_record.sales_angle = sales_angle
        score_record.has_website = audit.get("has_website", False)
        score_record.is_responsive = audit.get("is_responsive", False)
        score_record.has_ssl = audit.get("has_ssl", False)
        score_record.load_time_seconds = audit.get("load_time_seconds", 0.0)
        score_record.seo_title_present = True if audit.get("seo_title") else False
        score_record.social_links_count = audit.get("social_links_count", 0)
        score_record.last_scanned_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"On-demand live web re-audit succeeded for Biz ID {business_id}. New score: {score}")

        return {
            "success": True,
            "score": score,
            "opportunity_level": level,
            "explanation": explanation,
            "sales_angle": sales_angle,
            "has_website": score_record.has_website,
            "is_responsive": score_record.is_responsive,
            "has_ssl": score_record.has_ssl,
            "load_time_seconds": score_record.load_time_seconds,
            "seo_title_present": score_record.seo_title_present,
            "social_links_count": score_record.social_links_count,
            "cms_fingerprint": audit.get("cms_fingerprint", "Unknown"),
            "last_scanned_at": score_record.last_scanned_at.strftime('%Y-%m-%d %H:%M')
        }
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error executing live re-audit API for Biz ID {business_id}: {str(e)}")
        return {"success": False, "error": str(e)}, 500
