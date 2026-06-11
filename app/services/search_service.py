from app.models import db
from app.models.business import Business, BusinessScore
from app.models.search import Search
from app.services.mock_service import MockDataProvider
from app.services.scoring_service import ScoringService

class SearchService:
    """Orchestrates lead search crawling, filtration, website auditing, scoring, and SQLite database storage."""

    def __init__(self):
        self.provider = MockDataProvider()

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

            # 1. Fetch leads from swappable MockDataProvider
            raw_leads = self.provider.search_businesses(search.query, search.location)
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

                # Run detailed website audits
                website_url = lead.get('website_url')
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
                    has_website=audit['has_website'],
                    is_responsive=audit['is_responsive'],
                    has_ssl=audit['has_ssl'],
                    load_time_seconds=audit['load_time_seconds'],
                    seo_title_present=audit['seo_title_present'],
                    social_links_count=audit['social_links_count']
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
