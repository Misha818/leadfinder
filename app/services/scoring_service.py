from typing import Dict, Any, Tuple

class ScoringService:
    """Advanced Service to calculate 0-100 Website Opportunity Score and Sales Recommendations."""

    @staticmethod
    def calculate_advanced_score(business_info: Dict[str, Any], audit_metrics: Dict[str, Any]) -> Tuple[int, str, str, str]:
        """
        Calculates a B2B sales opportunity score (0-100) and maps it to
        Opportunity Levels, Explanations, and Recommended Sales Angles.
        Supports both Mock directory audits and real HTTP/HTTPS Scraper audits.

        Returns:
            Tuple[int, str, str, str]: (score, opportunity_level, explanation, sales_angle)
        """
        score = 0
        reasons = []

        # Check if audit is from the real scraper_service or the mock_service
        # Real scraper has a 'status' key
        is_real_scraper = 'status' in audit_metrics
        status = audit_metrics.get('status', 'success')

        # ----------------------------------------------------
        # Case A: No Website listed or completely empty
        # ----------------------------------------------------
        if status == 'no_website' or not audit_metrics.get('has_website', False):
            score += 40
            reasons.append("No website listed in local directories (+40)")

            # Reliance on Social channels check (Facebook, etc.)
            social_count = int(audit_metrics.get('social_links_count', 0) or 0)
            if social_count > 0:
                score += 20
                reasons.append("Exclusive reliance on Facebook/Instagram profiles (+20)")

        # ----------------------------------------------------
        # Case B: Website is listed but unreachable (Timeout / DNS)
        # ----------------------------------------------------
        elif status == 'unreachable' or not audit_metrics.get('reachability', True):
            score += 30
            reasons.append("Website is unreachable or DNS resolution fails (+30)")
            score += 30
            reasons.append("Major server connection timeout or response errors (+30)")

        # ----------------------------------------------------
        # Case C: Website is active (Process Technical Checklist)
        # ----------------------------------------------------
        else:
            status_code = audit_metrics.get('status_code', 200) or 200
            # Client / Server Error response (4xx, 5xx)
            if status_code != 200:
                score += 30
                reasons.append(f"Site returned HTTP client/server errors ({status_code}) (+30)")

            # SSL validation check
            has_ssl = audit_metrics.get('has_ssl', True)
            ssl_error = audit_metrics.get('ssl_error', False)
            if not has_ssl or ssl_error:
                score += 15
                reason_txt = "Expired/Invalid SSL certificate detected" if ssl_error else "Missing secure HTTPS validation (HTTP protocol)"
                reasons.append(f"{reason_txt} (+15)")

            # Mobile responsiveness check
            is_responsive = audit_metrics.get('is_responsive', True)
            if not is_responsive:
                score += 15
                reasons.append("Site lacks dynamic mobile-friendly viewport tags (+15)")

            # Load speed check
            load_time = float(audit_metrics.get('load_time_seconds', 0.0) or 0.0)
            if load_time > 3.0:
                score += 10
                reasons.append(f"Slow page loading speed ({load_time}s) (+10)")

            # SEO Metadata checks
            if is_real_scraper:
                seo_title = audit_metrics.get('seo_title', '')
                seo_desc = audit_metrics.get('seo_description', '')
                if not seo_title or not seo_desc:
                    score += 10
                    missing_parts = []
                    if not seo_title: missing_parts.append("Title tag")
                    if not seo_desc: missing_parts.append("Meta description")
                    reasons.append("Missing critical SEO tags ({}) (+10)".format(" and ".join(missing_parts)))
            else:
                # Fallback for Mock structures
                seo_title_present = audit_metrics.get('seo_title_present', True)
                if not seo_title_present:
                    score += 10
                    reasons.append("Missing meta SEO title parameters (+10)")

            # Contact Signals crawling (Real Scraper only)
            if is_real_scraper:
                has_tel = audit_metrics.get('has_tel_links', False)
                has_mail = audit_metrics.get('has_mailto_links', False)
                if not has_tel and not has_mail:
                    score += 5
                    reasons.append("No active contact anchors (tel: or mailto:) found (+5)")

        # ----------------------------------------------------
        # Presence & Potential Modifiers (Global)
        # ----------------------------------------------------
        # Missing critical local contact information
        if not business_info.get('phone') or not business_info.get('email'):
            score += 10
            reasons.append("Incomplete public contact details (Phone or Email missing) (+10)")

        # High ratings with poor web footprint indicating sales potential
        rating = float(business_info.get('rating', 0.0) or 0.0)
        reviews = int(business_info.get('reviews_count', 0) or 0)
        if (rating >= 4.2 or reviews >= 50) and (status == 'no_website' or score >= 35):
            score += 20
            reasons.append("Highly rated business with strong demand offset by poor web presence (+20)")

        # Clamp the calculated opportunity score
        final_score = min(100, max(0, score))

        # Map Opportunity Levels
        if final_score >= 90:
            opportunity_level = "Very High"
        elif final_score >= 70:
            opportunity_level = "High"
        elif final_score >= 40:
            opportunity_level = "Medium"
        else:
            opportunity_level = "Low"

        # Generate Explanation
        explanation = "The business has an opportunity score of {}/100 because: {}.".format(
            final_score, ", ".join(reasons) if reasons else "it maintains a fully functional, secure, and optimized web footprint"
        )

        # Sales angle selections
        if final_score >= 90:
            sales_angle = "Pitch a comprehensive Professional Website Launch Package featuring speed optimizations, mobile responsiveness, an SSL certificate, and direct conversion triggers (e.g., booking forms or quote requests) to turn search traffic into customers."
        elif final_score >= 70:
            if status == 'no_website' or not audit_metrics.get('has_website', False):
                sales_angle = "Demonstrate how relying solely on Facebook/Instagram risks losing organic traffic, and propose a dedicated Landing Page with integrated contact CTAs."
            else:
                sales_angle = "Showcase mobile accessibility and speed bottlenecks of their current site, and offer a custom redesigned WordPress/HTML5 portfolio optimized for speed and local SEO rankings."
        elif final_score >= 40:
            sales_angle = "Offer a Technical Security and Speed optimization package focusing on migrating their site to HTTPS (SSL activation) and resolving responsive view alignment bugs."
        else:
            sales_angle = "Propose advanced programmatic expansion services, localized blog writing, or digital advertising management to leverage their already outstanding web footprint."

        return final_score, opportunity_level, explanation, sales_angle
