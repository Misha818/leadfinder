from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseDataProvider(ABC):
    """
    Abstract Base Class representing a local business data provider.
    This architecture enables easily swapping out the data source
    (e.g., from mock data to Google Maps API or Apify Scrapers) in the future.
    """

    @abstractmethod
    def search_businesses(self, query: str, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for local businesses based on query and location parameters.

        Args:
            query (str): Industry or category keyword (e.g., "Dentist", "Restaurant").
            location (str): City or region (e.g., "Yerevan", "Tbilisi", "Gyumri").
            limit (int, optional): Max records to retrieve. Defaults to 20.

        Returns:
            List[Dict[str, Any]]: A list of business dictionaries. Each business has:
                - name (str)
                - address (str, nullable)
                - phone (str, nullable)
                - email (str, nullable)
                - website_url (str, nullable)
                - google_maps_url (str, nullable)
                - rating (float, nullable)
                - reviews_count (int)
                - category (str)
        """
        pass

    @abstractmethod
    def scan_website(self, url: str) -> Dict[str, Any]:
        """
        Audits a website URL to calculate metrics for Website Opportunity Score.

        Args:
            url (str): The website URL of the business.

        Returns:
            Dict[str, Any]: Scan metrics:
                - has_website (bool)
                - is_responsive (bool)
                - has_ssl (bool)
                - load_time_seconds (float)
                - seo_title_present (bool)
                - social_links_count (int)
        """
        pass
