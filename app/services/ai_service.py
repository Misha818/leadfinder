from typing import Dict, Any

class AIService:
    """Mock Service for AI-Assisted B2B Opportunity Analysis and Lead Sales Consultations."""

    @staticmethod
    def generate_opportunity_analysis(business_name: str, category: str, score: int, has_website: bool) -> Dict[str, Any]:
        """
        Generates mock AI-driven B2B consultancy summaries, estimated project complexities,
        and value tiers based on scored business lead profiles.

        Args:
            business_name (str): The name of target business.
            category (str): General industry sector (e.g., Dentist, Restaurant).
            score (int): Opportunity score (0-100).
            has_website (bool): True if website is active.

        Returns:
            Dict[str, Any]: Structured recommendations containing:
                - recommended_services (str)
                - complexity (str) - Low, Medium, High
                - value_category (str) - Small, Medium, Large
        """
        # Formulate tailored recommendations based on scored opportunity
        if not has_website:
            recommended_services = "Full-stack Custom Website Development, responsive layouts, local SEO structuring, Google Business profile optimization, and online contact forms."
            complexity = "Medium"
            value_category = "Large"
        elif score >= 70:
            recommended_services = "Website Redesign & Modernization, SSL certificate deployment, PageSpeed loading optimizations, and mobile-responsive CSS refactoring."
            complexity = "Medium"
            value_category = "Medium"
        elif score >= 40:
            recommended_services = "HTTPS Migration (SSL Certificate), basic responsive view tweaks, SEO meta title injections, and social sharing links integration."
            complexity = "Low"
            value_category = "Small"
        else:
            recommended_services = "Conversion rate optimizations, advanced programmatic local SEO expansions, and managed marketing lead generation campaigns."
            complexity = "High"
            value_category = "Medium"

        return {
            "recommended_services": recommended_services,
            "complexity": complexity,
            "value_category": value_category
        }
