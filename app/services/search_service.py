import os
from app.models import db
from app.models.business import Business, BusinessScore
from app.models.search import Search
from app.services.scoring_service import ScoringService

class BillingApprovalRequiredError(Exception):
    """Exception raised when the monthly Google Places free budget has been exhausted and manual user approval is required."""
    def __init__(self, estimated_cost_usd: float):
        self.estimated_cost_usd = estimated_cost_usd
        super().__init__(f"Monthly budget exhausted. Estimated cost: ${estimated_cost_usd:.4f}. Authorization required.")

def get_data_provider(user_approved: bool = False):
    """Factory function returning the configured B2B lead data provider."""
    provider_name = os.environ.get('DATA_PROVIDER', 'mock').strip().lower()
    if provider_name == 'google':
        from app.services.google_maps_service import GoogleMapsDataProvider
        return GoogleMapsDataProvider(user_approved=user_approved)
    else:
        from app.services.mock_service import MockDataProvider
        return MockDataProvider()

class SearchService:
    """Orchestrates lead search crawling, filtration, website auditing, scoring, and SQLite database storage."""

    def __init__(self, user_approved: bool = False):
        self.provider = get_data_provider(user_approved)

    def execute_and_score(self, search_id: int) -> int:
        """
        Runs local business search, filters rows according to database parameters,
        runs website presence audits, scores them, and commits to local SQLite db.

        Returns:
            int: Total matching leads stored.
        """
        search = db.session.get(Search, search_id)
        if not search:
            raise ValueError(f"Search ID {search_id} not found in database.")

        if search.status == 'completed':
            return search.results_count

        try:
            search.status = 'in_progress'
            db.session.commit()

            # 1. Fetch leads from swappable DataProvider (detects approval status internally)
            raw_leads = self.provider.search_businesses(search.query, search.location)

            # PRE-REQUEST APPROVAL GATE CHECK
            # If the provider blocked the Place Details due to exhausted budget and lack of approval
            if raw_leads and isinstance(raw_leads[0], dict) and raw_leads[0].get("status") == "approval_required":
                raise BillingApprovalRequiredError(raw_leads[0]["estimated_cost_usd"])

            filters = search.filters
            stored_leads_count = 0

            # 2. Iterate and apply advanced search criteria filters
            for lead in raw_leads:
                # Filter by Min Star Rating
                min_rating = float(filters.get('min_rating', 0.0))
                if float(lead.get('rating', 0.0) or 0.0) < min_rating:
                    continue

                # Filter by Min Reviews
                min_reviews = int(filters.get('min_reviews', 0))
                if int(lead.get('reviews_count', 0) or 0) < min_reviews:
                    continue

                # Filter by Phone Presence
                if filters.get('has_phone', False) and not lead.get('phone'):
                    continue

                # Filter by Email Presence
                if filters.get('has_email', False) and not lead.get('email'):
                    continue

                # Run detailed website audits with Real Scraper and defensive mock fallback
                website_url = lead.get('website_url')
                audit = None
                try:
                    from app.services.scraper_service import audit_website
                    audit = audit_website(website_url)
                except Exception as scraper_err:
                    # In case of connection failure, fallback to the provider's mock audit
                    print(f"Defensive Crawler Fallback for {website_url}: {str(scraper_err)}")
                    audit = self.provider.scan_website(website_url)

                # Filter by Social Presence
                if filters.get('has_socials', False) and int(audit.get('social_links_count', 0) or 0) == 0:
                    continue

                # 3. Calculate Advanced 0-100 Opportunity Score & Recommendations
                score, level, explanation, sales_angle = ScoringService.calculate_advanced_score(lead, audit)

                # 4. Save Business lead into database
                business = Business(
                    project_id=search.project_id,
                    search_id=search.id,
                    name=lead['name'],
                    address=lead.get('address'),
                    phone=lead.get('phone'),
                    email=lead.get('email'),
                    website_url=website_url,
                    google_maps_url=lead.get('google_maps_url'),
                    status='lead'
                )
                db.session.add(business)
                db.session.flush()  # Flush to generate business.id for the Score relationship

                # 5. Save corresponding detailed Score parameters
                score_record = BusinessScore(
                    business_id=business.id,
                    score=score,
                    opportunity_level=level,
                    explanation=explanation,
                    sales_angle=sales_angle,
                    has_website=audit.get('has_website', False),
                    is_responsive=audit.get('is_responsive', False),
                    has_ssl=audit.get('has_ssl', False),
                    load_time_seconds=audit.get('load_time_seconds', 0.0),
                    seo_title_present=audit.get('seo_title_present', True if audit.get('seo_title') else False),
                    social_links_count=audit.get('social_links_count', 0)
                )
                db.session.add(score_record)
                stored_leads_count += 1

            # 6. Complete and update Search transaction
            search.status = 'completed'
            search.results_count = stored_leads_count
            db.session.commit()

            return stored_leads_count

        except Exception as e:
            db.session.rollback()
            search.status = 'failed'
            db.session.commit()
            print(f"Exception during search execute and score: {str(e)}")
            raise e
