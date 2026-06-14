from datetime import datetime
import random
import re
from typing import List, Dict, Any
from app.services.data_provider import BaseDataProvider

class MockDataProvider(BaseDataProvider):
    """
    Mock service implementing BaseDataProvider.
    Generates highly realistic business and web presence scan data for local businesses
    spanning categories (Restaurants, Dentists, Hotels, Plumbers) in Armenia & Georgia.
    """

    def __init__(self):
        # Database of seed mock businesses
        self.seed_businesses = [
            # ----------------------------------------------------
            # YEREVAN, ARMENIA
            # ----------------------------------------------------
            {
                "name": "Elite Dental Yerevan",
                "category": "Dentist",
                "location": "Yerevan",
                "address": "12 Abovyan St, Yerevan 0010, Armenia",
                "phone": "+374 10 555222",
                "email": "info@elitedental.am",
                "website_url": None,  # No website -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=111111111111",
                "rating": 4.8,
                "reviews_count": 120
            },
            {
                "name": "Yerevan Family Dentistry",
                "category": "Dentist",
                "location": "Yerevan",
                "address": "25 Tumanyan St, Yerevan 0001, Armenia",
                "phone": "+374 10 555333",
                "email": "contact@yerevandentistry.am",
                "website_url": "http://yerevandentistry.am",  # Outdated, HTTP (no SSL), slow, non-responsive
                "google_maps_url": "https://maps.google.com/?cid=222222222222",
                "rating": 4.1,
                "reviews_count": 34
            },
            {
                "name": "Aesthetic Smiles Clinic",
                "category": "Dentist",
                "location": "Yerevan",
                "address": "4 Pushkin St, Yerevan 0010, Armenia",
                "phone": "+374 10 555444",
                "email": "smile@aestheticsmiles.am",
                "website_url": "https://aestheticsmiles.am",  # fully optimized site -> Opportunity Score: ~15
                "google_maps_url": "https://maps.google.com/?cid=333333333333",
                "rating": 4.9,
                "reviews_count": 215
            },
            {
                "name": "Tavern Yerevan",
                "category": "Restaurant",
                "location": "Yerevan",
                "address": "5 Amiryan St, Yerevan 0010, Armenia",
                "phone": "+374 10 548484",
                "email": "booking@tavernyerevan.am",
                "website_url": "https://tavernyerevan.am",  # fully optimized site -> Opportunity Score: ~15
                "google_maps_url": "https://maps.google.com/?cid=444444444444",
                "rating": 4.7,
                "reviews_count": 1450
            },
            {
                "name": "Abovyan 12 Cafe",
                "category": "Restaurant",
                "location": "Yerevan",
                "address": "12 Abovyan St, Yerevan 0010, Armenia",
                "phone": "+374 10 555777",
                "email": "hello@abovyan12.am",
                "website_url": None,  # No website -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=555555555555",
                "rating": 4.6,
                "reviews_count": 89
            },
            {
                "name": "Master Yerevan Handyman",
                "category": "Plumber",
                "location": "Yerevan",
                "address": "8 Baghramyan Ave, Yerevan 0019, Armenia",
                "phone": "+374 91 444555",
                "email": None,
                "website_url": None,  # No website -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=666666666666",
                "rating": 4.5,
                "reviews_count": 18
            },

            # ----------------------------------------------------
            # GYUMRI, ARMENIA
            # ----------------------------------------------------
            {
                "name": "Gyumri Plaza Hotel",
                "category": "Hotel",
                "location": "Gyumri",
                "address": "7 Gorki St, Gyumri 3101, Armenia",
                "phone": "+374 312 55501",
                "email": "info@gyumriplaza.am",
                "website_url": "https://gyumriplaza.am",  # fully optimized -> Opportunity Score: ~15
                "google_maps_url": "https://maps.google.com/?cid=777777777777",
                "rating": 4.4,
                "reviews_count": 142
            },
            {
                "name": "Berlin Art Hotel Gyumri",
                "category": "Hotel",
                "location": "Gyumri",
                "address": "25 Hakobyan St, Gyumri 3104, Armenia",
                "phone": "+374 312 55502",
                "email": "berlin@arthotel.com",
                "website_url": "http://berlinarthotel.com",  # Outdated, no SSL, slow
                "google_maps_url": "https://maps.google.com/?cid=888888888888",
                "rating": 4.2,
                "reviews_count": 78
            },
            {
                "name": "Shirak Guesthouse",
                "category": "Hotel",
                "location": "Gyumri",
                "address": "15 Sayat-Nova St, Gyumri 3101, Armenia",
                "phone": "+374 312 55503",
                "email": "shirak@guesthouse.am",
                "website_url": None,  # No website -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=999999999999",
                "rating": 3.9,
                "reviews_count": 12
            },
            {
                "name": "Gyumri Dental Center",
                "category": "Dentist",
                "location": "Gyumri",
                "address": "100 Ryzhkov St, Gyumri 3101, Armenia",
                "phone": "+374 312 44411",
                "email": None,
                "website_url": None,  # No website -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=101010101010",
                "rating": 4.3,
                "reviews_count": 22
            },

            # ----------------------------------------------------
            # TBILISI, GEORGIA
            # ----------------------------------------------------
            {
                "name": "Shavi Lomi",
                "category": "Restaurant",
                "location": "Tbilisi",
                "address": "28 Zurab Kvlividze St, Tbilisi 0102, Georgia",
                "phone": "+995 32 2555110",
                "email": "contact@shavilomi.ge",
                "website_url": "https://shavilomi.ge",  # fully optimized -> Opportunity Score: ~15
                "google_maps_url": "https://maps.google.com/?cid=111100001111",
                "rating": 4.6,
                "reviews_count": 920
            },
            {
                "name": "Tbilisi Khinkali House",
                "category": "Restaurant",
                "location": "Tbilisi",
                "address": "37 Rustaveli Ave, Tbilisi 0108, Georgia",
                "phone": "+995 32 2555111",
                "email": "khinkali@house.ge",
                "website_url": None,  # No website -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=222200002222",
                "rating": 4.3,
                "reviews_count": 480
            },
            {
                "name": "Rustaveli Traditional Dining",
                "category": "Restaurant",
                "location": "Tbilisi",
                "address": "15 Rustaveli Ave, Tbilisi 0108, Georgia",
                "phone": "+995 32 2555112",
                "email": "dining@rustaveli.ge",
                "website_url": "http://rustavelidining.ge",  # Outdated, broken URL -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=333300003333",
                "rating": 3.8,
                "reviews_count": 65
            },
            {
                "name": "Tbilisi Central Dental Clinic",
                "category": "Dentist",
                "location": "Tbilisi",
                "address": "45 Chavchavadze Ave, Tbilisi 0179, Georgia",
                "phone": "+995 32 2444333",
                "email": "info@tbilisidental.ge",
                "website_url": None,  # No website -> Opportunity Score: 100
                "google_maps_url": "https://maps.google.com/?cid=444400004444",
                "rating": 4.7,
                "reviews_count": 154
            }
        ]

    def search_businesses(self, query: str, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Filters seed database records by keyword matching both query and location.
        If no seed matches are found, it generates highly realistic dynamic local business data.
        """
        cleaned_query = query.lower().strip()
        cleaned_location = location.lower().strip()

        # Step 1: Filter from local seed list
        matches = []
        for biz in self.seed_businesses:
            # Match location (Yerevan, Gyumri, Tbilisi)
            loc_match = cleaned_location in biz['location'].lower() or cleaned_location in biz['address'].lower()

            # Match query with name or category
            query_match = (cleaned_query in biz['category'].lower() or
                           cleaned_query in biz['name'].lower() or
                           any(word in biz['name'].lower() for word in cleaned_query.split()))

            if loc_match and query_match:
                matches.append(biz)

        # Step 2: If seed list yields insufficient results, dynamically generate highly realistic ones
        if len(matches) < 3:
            dynamic_data = self._generate_dynamic_leads(query, location, count=(limit - len(matches)))
            matches.extend(dynamic_data)

        # Truncate to limit and return copy
        results = matches[:limit]
        return [dict(r) for r in results]

    def scan_website(self, url: str) -> Dict[str, Any]:
        """
        Simulates auditing a website URL.
        Returns detailed, realistic audit indicators depending on url properties.
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

        cleaned_url = url.lower()

        # 1. Broken / Inactive site
        if "broken" in cleaned_url or "rustavelidining" in cleaned_url:
            return {
                "has_website": False,  # Technically resolves as inactive, so treated as no website
                "is_responsive": False,
                "has_ssl": False,
                "load_time_seconds": 15.0,  # Timeout
                "seo_title_present": False,
                "social_links_count": 0
            }

        # 2. Strong/Fully Optimized Web Presence
        if "aestheticsmiles" in cleaned_url or "tavernyerevan" in cleaned_url or "shavilomi" in cleaned_url or "gyumriplaza" in cleaned_url:
            return {
                "has_website": True,
                "is_responsive": True,
                "has_ssl": True,
                "load_time_seconds": round(random.uniform(0.6, 1.8), 2),
                "seo_title_present": True,
                "social_links_count": random.randint(2, 5)
            }

        # 3. Weak / Outdated Web Presence (yerevandentistry, berlinarthotel, etc.)
        # Default fallback is treated as weak to offer a realistic outreach sales target
        has_ssl = cleaned_url.startswith("https://")
        return {
            "has_website": True,
            "is_responsive": random.choice([True, False, False]),  # Mostly unresponsive
            "has_ssl": has_ssl,
            "load_time_seconds": round(random.uniform(3.5, 8.2), 2),  # Slow loading
            "seo_title_present": random.choice([True, False]),
            "social_links_count": random.choice([0, 1])
        }

    def _generate_dynamic_leads(self, query: str, location: str, count: int) -> List[Dict[str, Any]]:
        """Generates realistic, structured business directories dynamically when seeds are dry."""
        categories = ["Restaurant", "Dentist", "Hotel", "Plumber", "Cafe", "Bakery", "Gym", "Salon"]
        matched_cat = "Business"
        for cat in categories:
            if cat.lower() in query.lower():
                matched_cat = cat
                break

        # Define dynamic structures based on city
        loc_clean = location.capitalize()
        country = "Armenia" if loc_clean in ["Yerevan", "Gyumri"] else "Georgia"
        phone_prefix = "+374" if country == "Armenia" else "+995"
        city_code = "10" if loc_clean == "Yerevan" else "312" if loc_clean == "Gyumri" else "32"

        streets = {
            "Yerevan": ["Baghramyan Ave", "Abovyan St", "Tumanyan St", "Pushkin St", "Saryan St", "Nalbandyan St"],
            "Gyumri": ["Ryzhkov St", "Gorki St", "Hakobyan St", "Sayat-Nova St", "Rustaveli St"],
            "Tbilisi": ["Rustaveli Ave", "Chavchavadze Ave", "Pekini St", "Kote Marjanishvili St", "Leselidze St"]
        }
        chosen_streets = streets.get(loc_clean, ["Central Street"])

        business_names_parts = {
            "Restaurant": ["Tavern", "Bistro", "Traditional Dine", "House", "Kitchen", "Table"],
            "Dentist": ["Dental Center", "Clinic", "Smile Care", "Ortho Dent", "Aesthetic Dental"],
            "Hotel": ["Plaza Hotel", "Guesthouse", "Inn", "Boutique Hotel", "Suites"],
            "Plumber": ["Plumbing Pros", "Master Plumber", "Pipe Service", "Rapid Handyman"],
            "Cafe": ["Roasters", "Beans Cafe", "Corner Cafe", "Lounge", "Brew Bar"],
            "Bakery": ["Artisan Bakery", "Sweet Crumb", "Oven Fresh", "Baguette", "Patisserie"],
            "Gym": ["Fitness Center", "Iron Gym", "Power Studio", "Athletic Club", "Health Club"],
            "Salon": ["Beauty Salon", "Studio Barber", "Elite Hair & Spa", "Glamour", "Cut & Color"]
        }
        parts = business_names_parts.get(matched_cat, ["Group", "Enterprise", "Associates", "Solutions"])

        dynamic_leads = []
        for i in range(count):
            random.seed(hash(query + location) + i) # Deterministic but highly variable seeds

            # Generate Name
            p1 = random.choice([loc_clean, "Central", "Elite", "Royal", "Apex", "Golden", "Local", "Aesthetic"])
            p2 = parts[i % len(parts)]
            biz_name = f"{p1} {p2}" if random.choice([True, False]) else f"{p2} {p1}"

            # Generate Address
            street = random.choice(chosen_streets)
            num = random.randint(1, 140)
            postal = f"00{random.randint(10, 99)}" if country == "Armenia" else f"01{random.randint(10, 99)}"
            address = f"{num} {street}, {loc_clean} {postal}, {country}"

            # Generate Phone
            phone = f"{phone_prefix} {city_code} {random.randint(500, 999)}{random.randint(100, 999)}"

            # Generate Category-Specific Emails and Websites
            domain = re.sub(r'[^a-zA-Z0-9]', '', biz_name.lower())
            domain_ext = ".am" if country == "Armenia" else ".ge"

            # Determine Web state: 50% No Website, 25% Outdated/Weak, 25% Optimized
            web_roll = random.random()
            if web_roll < 0.50:
                website_url = None
                email = f"info@{domain}{domain_ext}" if random.choice([True, False]) else None
            elif web_roll < 0.75:
                website_url = f"http://{domain}{domain_ext}"  # Outdated HTTP
                email = f"contact@{domain}{domain_ext}"
            else:
                website_url = f"https://www.{domain}{domain_ext}"  # Optimized HTTPS
                email = f"office@{domain}{domain_ext}"

            google_maps_url = f"https://maps.google.com/?cid={random.randint(100000000000, 999999999999)}"
            rating = round(random.uniform(3.5, 4.9), 1)
            reviews = random.randint(5, 300)

            dynamic_leads.append({
                "name": biz_name,
                "category": matched_cat,
                "location": loc_clean,
                "address": address,
                "phone": phone,
                "email": email,
                "website_url": website_url,
                "google_maps_url": google_maps_url,
                "rating": rating,
                "reviews_count": reviews
            })

        return dynamic_leads
