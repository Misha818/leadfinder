# Project Goals - Company Finder

## Core Mission
The core mission of **Company Finder** is to create a robust, production-ready B2B lead-generation web application. The tool is designed for web developers, agency owners, and freelancers to identify local businesses that either completely lack a website or have a very weak online presence.

By analyzing key indicators of a business's online footprint, the application will calculate a **Website Opportunity Score (0-100)**. This score will help identify high-value targets who are most in need of professional web development and digital marketing services.

## Key Functionalities
1. **Local Business Discovery (Searches):** Integrate Google Maps API (or a mock/scraper service for fallback) to discover local businesses by keyword and location (e.g., "dentist in Chicago", "plumber in Austin").
2. **Website & Presence Analyzer:** Inspect discovered businesses to check if they have a website, if the domain is active, if it is mobile-friendly, has SSL, is fast, and checks basic SEO.
3. **Website Opportunity Score (0-100):** A custom scoring algorithm where:
   - **100** means no website at all (maximum opportunity for a sale).
   - **70-90** means very weak, outdated, or broken website.
   - **0-30** means a fully optimized, modern web presence (low opportunity).
4. **Lead Organization (Projects):** Group target businesses into "Projects" or "Outreach Lists" to organize cold-calling, email campaigns, or walk-ins.
5. **Outreach Management:** Track contact history (emails sent, calls made, meetings booked) and log personal notes for each business lead.
