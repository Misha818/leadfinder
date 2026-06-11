from typing import Dict, Any, Tuple

class ScoringService:
    """Advanced Service to calculate 0-100 Website Opportunity Score and Sales Recommendations."""

    @staticmethod
    def calculate_advanced_score(business_info: Dict[str, Any], audit_metrics: Dict[str, Any]) -> Tuple[int, str, str, str]:
        """
        Calculates a B2B sales opportunity score (0-100) and maps it to
        Opportunity Levels, Explanations, and Recommended Sales Angles.

        Returns:
            Tuple[int, str, str, str]: (score, opportunity_level, explanation, sales_angle)
        """
        score = 0
        reasons = []

        has_website = audit_metrics.get('has_website', False)
        website_url = business_info.get('website_url')

        # 1. Website Factors
        if not has_website:
            if not website_url:
                score += 40
                reasons.append("No website listed in directories (+40)")
            else:
                # Site exists but is broken or unreachable
                score += 30
                reasons.append("Website is unreachable or DNS resolution fails (+30)")
                score += 30
                reasons.append("Major server connection or response errors (+30)")
        else:
            # Outdated/Abandoned Indicators
            is_slow = (audit_metrics.get('load_time_seconds', 0.0) or 0.0) > 3.0
            is_unresponsive = not audit_metrics.get('is_responsive', True)
            is_insecure = not audit_metrics.get('has_ssl', True)

            if is_slow or is_unresponsive or is_insecure:
                score += 20
                reasons.append("Website shows signs of being outdated or abandoned (+20)")
                if is_unresponsive:
                    score += 15
                    reasons.append("Site lacks dynamic mobile responsiveness (+15)")
                if is_insecure:
                    score += 15
                    reasons.append("Missing secure HTTPS / SSL certificate validation (+15)")
                if is_slow:
                    score += 10
                    reasons.append("Extremely slow page load speed (+10)")

        # 2. Online Presence Factors
        # Check if they only have social media presence (facebook, instagram, linkedin, etc.)
        social_count = int(audit_metrics.get('social_links_count', 0) or 0)
        if not has_website and social_count > 0:
            score += 20
            reasons.append("Exclusively relies on Facebook/Instagram profiles (+20)")

        # Missing essential GMB (Google Business Info)
        if not business_info.get('phone') or not business_info.get('email'):
            score += 10
            reasons.append("Incomplete public contact details (Phone or Email missing) (+10)")

        # 3. Business Potential
        rating = float(business_info.get('rating', 0.0) or 0.0)
        reviews = int(business_info.get('reviews_count', 0) or 0)

        if (rating >= 4.2 or reviews >= 50) and (not has_website or score >= 30):
            score += 20
            reasons.append("Highly reviewed business with strong customer base but poor web presence (+20)")

        # Clamp score between 0 and 100
        final_score = min(100, max(0, score))

        # 4. Map to Opportunity Levels
        if final_score >= 90:
            opportunity_level = "Very High"
        elif final_score >= 70:
            opportunity_level = "High"
        elif final_score >= 40:
            opportunity_level = "Medium"
        else:
            opportunity_level = "Low"

        # 5. Generate Explanation and Recommended Sales Angles
        explanation = "The business has an opportunity score of {}/100 because: {}.".format(
            final_score, ", ".join(reasons) if reasons else "it maintains a fully functional, fast, and optimized web footprint"
        )

        # Sales angle selections
        if final_score >= 90:
            sales_angle = "Pitch a comprehensive Professional Website Launch Package featuring speed optimizations, mobile responsiveness, an SSL certificate, and direct conversion triggers (e.g., booking forms or quote requests) to turn search traffic into customers."
        elif final_score >= 70:
            if not has_website:
                sales_angle = "Demonstrate how relying solely on Facebook/Instagram risks losing organic traffic, and propose a dedicated Landing Page with integrated contact CTAs."
            else:
                sales_angle = "Showcase mobile accessibility and speed bottlenecks of their current site, and offer a custom redesigned WordPress/HTML5 portfolio optimized for speed and local SEO rankings."
        elif final_score >= 40:
            sales_angle = "Offer a Technical Security and Speed optimization package focusing on migrating their site to HTTPS (SSL activation) and resolving responsive view alignment bugs."
        else:
            sales_angle = "Propose advanced programmatic expansion services, localized blog writing, or digital advertising management to leverage their already outstanding web footprint."

        return final_score, opportunity_level, explanation, sales_angle
