import time
import logging
from datetime import datetime
from flask import Blueprint, render_template, request
from app.models import db
from app.models.project import Project
from app.models.search import Search
from app.models.business import Business, BusinessScore
from app.services.billing_service import get_monthly_usage, get_all_time_request_count, get_billing_cache_status

logger = logging.getLogger('company_finder')
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Renders the main SaaS application dashboard driven 100% by real SQLite database metrics."""
    logger.info("Accessing live system database metrics for home dashboard rendering...")

    # 1. Fetch real-world counts from SQLAlchemy SQLite tables
    total_projects = Project.query.count()
    total_searches = db.session.query(Search).count()
    total_businesses = Business.query.count()

    # 2. Query BusinessScore metrics to compile realistic aggregates
    scores = db.session.query(BusinessScore).all()
    no_website_count = sum(1 for s in scores if not s.has_website)
    weak_website_count = sum(1 for s in scores if s.has_website and s.score >= 50)
    strong_website_count = sum(1 for s in scores if s.has_website and s.score < 50)

    total_scored = len(scores)
    avg_opportunity_score = int(sum(s.score for s in scores) / total_scored) if total_scored > 0 else 0

    # Compile ratios safely for dashboard progress meters
    no_web_ratio = int((no_website_count / total_businesses) * 100) if total_businesses > 0 else 0
    weak_web_ratio = int((weak_website_count / total_businesses) * 100) if total_businesses > 0 else 0
    strong_web_ratio = int((strong_website_count / total_businesses) * 100) if total_businesses > 0 else 0

    stats = {
        "total_projects": total_projects,
        "total_searches": total_searches,
        "total_businesses": total_businesses,
        "no_website_count": no_website_count,
        "weak_website_count": weak_website_count,
        "strong_website_count": strong_website_count,
        "no_web_ratio": no_web_ratio,
        "weak_web_ratio": weak_web_ratio,
        "strong_web_ratio": strong_web_ratio,
        "avg_opportunity_score": avg_opportunity_score
    }

    # 3. Fetch actual recent business leads ordered by creation timestamps
    recent_leads = Business.query.order_by(Business.created_at.desc()).limit(4).all()

    # 4. Fetch live GCP API billing metrics
    current_month = datetime.utcnow().strftime("%Y-%m")
    usage = get_monthly_usage(current_month)
    all_time_requests = get_all_time_request_count()
    cache = get_billing_cache_status()

    # Calculate last fetched cache timestamps description
    last_fetched_ts = time.time() - cache["cache_age_seconds"]
    last_fetched_dt = datetime.fromtimestamp(last_fetched_ts)
    last_fetched_str = last_fetched_dt.strftime('%H:%M')

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_leads=recent_leads,
        usage=usage,
        all_time_requests=all_time_requests,
        is_fallback=cache["is_fallback"],
        last_fetched_str=last_fetched_str
    )


@main_bp.route('/businesses')
def list_businesses():
    """Renders global leads catalog, supporting custom keyword searches."""
    query_param = request.args.get('q', '').strip()

    if query_param:
        logger.info(f"Filtering global business catalog for keyword query: '{query_param}'")
        # Run search query matching name, address, phone or email fields
        leads = Business.query.filter(
            (Business.name.ilike(f'%{query_param}%')) |
            (Business.address.ilike(f'%{query_param}%')) |
            (Business.phone.ilike(f'%{query_param}%')) |
            (Business.email.ilike(f'%{query_param}%'))
        ).all()
    else:
        logger.info("Retrieving full business directory database log rows...")
        leads = Business.query.all()

    return render_template('businesses.html', leads=leads, query_param=query_param)
