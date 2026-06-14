import os
import requests
import time
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
import urllib3
from app.services.data_provider import BaseDataProvider

# Suppress insecure SSL connection warnings during web auditing scans
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GoogleMapsDataProvider(BaseDataProvider):
    """
    Google Places API data provider for discovering and auditing real business listings.
    Integrates live Places Text Search & Details and runs full web crawler presence checks.
    """

    def __init__(self, user_approved: bool = False):
        self.api_key = os.environ.get('GOOGLE_PLACES_API_KEY', '').strip()
        self.user_approved = user_approved

    def search_businesses(self, query: str, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Queries Google Places API (Text Search -> Place Details) with token pagination.

        Returns:
            List[Dict[str, Any]]: Processed list of real-world business listings.
        """
        if not self.api_key:
            raise ValueError(
                "CRITICAL GOOGLE PLACES API ERROR: Google Places API Key is missing. "
                "Configure GOOGLE_PLACES_API_KEY inside your .env file."
            )

        search_query = f"{query} in {location}"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": search_query,
            "key": self.api_key
        }

        results = []
        next_page_token = None

        try:
            # Query first batch
            response = requests.get(url, params=params, timeout=10.0)

            # Quota Exceeded (HTTP 429)
            if response.status_code == 429:
                raise RuntimeError("Google Places API quota limit exhausted (HTTP 429). Please try again later.")

            data = response.json()
            status = data.get("status")

            # Error cases handling
            if status == "REQUEST_DENIED":
                raise PermissionError(
                    "Google Places API Authentication Denied (HTTP 403). "
                    "Ensure your GOOGLE_PLACES_API_KEY is active and valid."
                )
            elif status == "ZERO_RESULTS":
                return []
            elif status == "OVER_QUERY_LIMIT":
                raise RuntimeError("Google Places API Quota Exceeded (OVER_QUERY_LIMIT). Verify billing on Google Console.")

            results.extend(data.get("results", []))
            next_page_token = data.get("next_page_token")

            # Page Token Loop Pagination
            while len(results) < limit and next_page_token:
                # Places API pagetokens need ~2 seconds to initialize and become active
                time.sleep(2.0)
                paginated_params = {
                    "pagetoken": next_page_token,
                    "key": self.api_key
                }
                response = requests.get(url, params=paginated_params, timeout=10.0)
                data = response.json()

                if data.get("status") == "OK":
                    results.extend(data.get("results", []))
                    next_page_token = data.get("next_page_token")
                else:
                    break

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error connecting to Google Places API: {str(e)}")

        # Clean search results list and query Places details to acquire full B2B profiles
        cleaned_businesses = []
        for index, raw in enumerate(results[:limit]):
            place_id = raw.get("place_id")
            if not place_id:
                continue

            # Query detailed B2B specifications for place
            details = self._fetch_place_details(place_id)
            if not details:
                continue

            # If details contains the approval_required token indicator, return it directly to the calling route!
            if isinstance(details, dict) and details.get("status") == "approval_required":
                return [details]

            # Resolve category type
            types = details.get("types", [])
            category = types[0].replace("_", " ").capitalize() if types else query.capitalize()

            cleaned_businesses.append({
                "name": details.get("name"),
                "category": category,
                "location": location,
                "address": details.get("formatted_address"),
                "phone": details.get("formatted_phone_number"),
                "email": None,  # Google Places API does not publish emails
                "website_url": details.get("website"),
                "google_maps_url": details.get("url"),
                "rating": details.get("rating", 0.0),
                "reviews_count": details.get("user_ratings_total", 0)
            })

        return cleaned_businesses

    def _fetch_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Queries Google Place Details API for comprehensive listing parameters.
        Enforces a protective budget approval gate check before launching requests.
        """
        from app.services.billing_service import get_monthly_usage, calculate_request_cost, log_request

        fields_list = ["name", "formatted_address", "formatted_phone_number", "website", "url", "rating", "user_ratings_total", "types", "opening_hours"]

        # PRE-REQUEST APPROVAL GATE CHECK
        current_month = datetime.utcnow().strftime("%Y-%m")
        usage = get_monthly_usage(current_month)

        if not usage["is_within_free_tier"] and not self.user_approved:
            # Free credit exhausted and user hasn't explicitly approved -> trigger gate
            cost = calculate_request_cost(fields_list)
            return {
                "status": "approval_required",
                "estimated_cost_usd": cost,
                "message": "Monthly Google Places free tier budget limits exceeded. This request requires authorization."
            }

        url = "https://maps.googleapis.com/maps/api/place/details/json"
        fields = ",".join(fields_list)
        params = {
            "place_id": place_id,
            "fields": fields,
            "key": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10.0)
            data = response.json()
            if data.get("status") == "OK":
                # Log successful API details consumption inside database
                log_request(fields_list, was_approved=True)
                return data.get("result", {})
        except requests.exceptions.RequestException:
            pass
        return {}

    def scan_website(self, url: str) -> Dict[str, Any]:
        """
        Runs a real live technical web footprint audit on the business domain.
        Uses requests and BeautifulSoup to compile responsiveness, SSL, load speeds, and social indices.
        """
        if not url:
            return {
                "has_website": False,
                "is_responsive": False,
                "has_ssl": False,
                "load_time_seconds": 0.0,
                "seo_title_present": False,
                "social_links_count": 0
            }

        from app.services.scraper_service import is_social_media_url
        if is_social_media_url(url):
            return {
                "has_website": False,
                "is_social_media_only": True,
                "social_links_count": 1,
                "is_responsive": False,
                "has_ssl": False,
                "load_time_seconds": 0.0,
                "seo_title_present": False
            }

        # Format scheme
        target_url = url
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url

        start_time = time.time()
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CompanyFinder/1.0'}
            # verify=False prevents SSL handshake crashes on websites with invalid/expired certs, letting us analyze them!
            response = requests.get(target_url, timeout=5.0, headers=headers, verify=False)
            load_time = round(time.time() - start_time, 2)

            has_ssl = target_url.lower().startswith('https://') or response.url.lower().startswith('https://')

            # Parse HTML layout
            soup = BeautifulSoup(response.text, 'html.parser')

            # Mobile responsive viewport tag check
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            is_responsive = False
            if viewport and 'width=device-width' in viewport.get('content', '').lower():
                is_responsive = True

            # SEO Title present check
            title = soup.find('title')
            seo_title_present = True if title and title.text.strip() else False

            # Social links counter
            social_links_count = 0
            social_domains = ['facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com', 'youtube.com']
            for a in soup.find_all('a', href=True):
                href = a['href'].lower()
                if any(domain in href for domain in social_domains):
                    social_links_count += 1

            return {
                "has_website": True,
                "is_responsive": is_responsive,
                "has_ssl": has_ssl,
                "load_time_seconds": load_time,
                "seo_title_present": seo_title_present,
                "social_links_count": social_links_count
            }

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
            # Domain is unreachable or broken -> Optimal sales prospect!
            print(f"B2B live crawler connection failed for {target_url}: {str(e)}")
            return {
                "has_website": False,  # Treated as no website
                "is_responsive": False,
                "has_ssl": False,
                "load_time_seconds": 15.0,  # Simulated timeout penalty
                "seo_title_present": False,
                "social_links_count": 0
            }
