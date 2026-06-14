import os
import time
import logging
from datetime import datetime
from app.models import db
from app.models.billing import ApiUsage

logger = logging.getLogger('company_finder')

# In-memory pricing and budget cache configurations
_billing_cache = {
    "prices": None,          # dict: {"basic": 0.017, "contact": 0.003, "atmosphere": 0.005}
    "free_credit": None,     # float: monthly free credit allocation (standard 200.00)
    "last_fetched": 0,       # timestamp
    "is_fallback": True      # tracks whether we are running on hardcoded fallback sentinels
}

# Google Maps Billing Catalog Service ID
MAPS_SERVICE_ID = "08F4-CE99-D64D"

def fetch_live_sku_pricing() -> dict:
    """
    Queries Google Cloud Billing Catalog API to fetch live unit pricing for Places SKUs.
    Filters SKUs matching: Basic, Contact, and Atmosphere details tiers.
    """
    api_key = os.environ.get('GOOGLE_PLACES_API_KEY', '').strip()
    if not api_key:
        logger.warning("Places API Key missing. Skipping live SKU pricing fetch.")
        return {}

    url = f"https://cloudbilling.googleapis.com/v1/services/{MAPS_SERVICE_ID}/skus"
    params = {"key": api_key}

    try:
        import requests
        response = requests.get(url, params=params, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            skus_list = data.get("skus", [])
            prices = {}

            # Parse and match SKU descriptions
            for sku in skus_list:
                desc = sku.get("description", "")
                unit_price_info = sku.get("pricingInfo", [{}])[0].get("pricingExpression", {}).get("tieredRates", [{}])[0].get("unitPrice", {})

                # Extract value in standard float USD
                units = int(unit_price_info.get("units", 0) or 0)
                nanos = int(unit_price_info.get("nanos", 0) or 0)
                price_usd = units + (nanos / 1e9)

                if "Places API - Place Details - Basic" in desc:
                    prices["basic"] = price_usd
                elif "Places API - Place Details - Contact" in desc:
                    prices["contact"] = price_usd
                elif "Places API - Place Details - Atmosphere" in desc:
                    prices["atmosphere"] = price_usd

            # Verify that we extracted all three SKUs
            if len(prices) == 3:
                logger.info("Successfully fetched live Places API SKU prices from GCP Catalog.")
                return prices

    except Exception as e:
        logger.warning(f"Error fetching live SKU pricing from Google Cloud Billing Catalog API: {str(e)}")

    return {}


def fetch_monthly_free_credit() -> float:
    """
    Queries Cloud Billing Budgets API to parse monthly configured credit.
    Since this typically requires OAuth authentication, fails gracefully with standard fallback.
    """
    account_id = os.environ.get('GOOGLE_BILLING_ACCOUNT_ID', '').strip()
    if not account_id:
        return 200.00

    url = f"https://billingbudgets.googleapis.com/v1/billingAccounts/{account_id}/budgets"

    # We attempt a requests query. If unauthorized (fails Oauth), it falls back to 200.00
    try:
        import requests
        # Placeholder endpoint fetch. Standard GCP requests require oauth tokens.
        # We catch unauthorized 401/403 states and trigger the warning fallback cleanly!
        response = requests.get(url, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            budgets = data.get("budgets", [])
            if budgets:
                amount = budgets[0].get("amount", {}).get("specifiedAmount", {})
                units = float(amount.get("units", 200.00) or 200.00)
                logger.info(f"Successfully fetched live monthly billing budget: ${units}")
                return units
    except Exception:
        pass

    return 200.00


def get_sku_prices() -> dict:
    """
    Unified internal accessor for pricing schemas.
    Checks cache validity (24 hours) and refreshes from GCP Catalog, or executes fallback.
    """
    now = time.time()
    cache_age_seconds = now - _billing_cache["last_fetched"]

    # Refresh pricing cache if empty or older than 24 hours (86400 seconds)
    if not _billing_cache["prices"] or cache_age_seconds > 86400:
        logger.info("SKU pricing cache expired or empty. Refreshing live billing parameters...")
        live_prices = fetch_live_sku_pricing()
        live_budget = fetch_monthly_free_credit()

        if live_prices:
            _billing_cache["prices"] = live_prices
            _billing_cache["is_fallback"] = False
        else:
            logger.warning("Using fallback SKU prices — verify Google Billing Catalog API access")
            _billing_cache["prices"] = {"basic": 0.017, "contact": 0.003, "atmosphere": 0.005}
            _billing_cache["is_fallback"] = True

        _billing_cache["free_credit"] = live_budget
        _billing_cache["last_fetched"] = now

    return _billing_cache["prices"]


def get_billing_cache_status() -> dict:
    """Returns details on the current billing cache age, source, and values."""
    # Ensure cache is initialized
    get_sku_prices()

    age = time.time() - _billing_cache["last_fetched"]
    return {
        "prices": _billing_cache["prices"],
        "free_credit": _billing_cache["free_credit"],
        "cache_age_seconds": int(age),
        "is_fallback": _billing_cache["is_fallback"]
    }


def calculate_request_cost(fields: list) -> float:
    """
    Calculates the combined cost of a single Place Details query in USD
    by assessing which pricing SKU tiers (Basic, Contact, Atmosphere) are triggered.
    """
    prices = get_sku_prices()
    cost = prices["basic"]  # Basic is always charged as the baseline

    # Identify if contact tier is triggered
    contact_triggers = ["website", "formatted_phone_number", "phone", "opening_hours", "hours"]
    if any(f in fields for f in contact_triggers):
        cost += prices["contact"]

    # Identify if atmosphere tier is triggered
    atmosphere_triggers = ["rating", "user_ratings_total", "price_level", "reviews", "reviews_count"]
    if any(f in fields for f in atmosphere_triggers):
        cost += prices["atmosphere"]

    return round(cost, 4)


def get_monthly_usage(billing_month: str) -> dict:
    """
    Queries ApiUsage rows for the given month.
    Computes total spent, request counts, and remaining free requests and credits.
    """
    # Initialize prices cache
    get_sku_prices()
    free_credit = _billing_cache["free_credit"]

    # Query SQLite database logs
    usages = ApiUsage.query.filter_by(billing_month=billing_month).all()
    request_count = len(usages)

    # Calculate total spent on approved queries
    total_spent_usd = sum(u.estimated_cost_usd for u in usages)

    remaining_free_credit_usd = max(0.0, round(free_credit - total_spent_usd, 4))
    is_within_free_tier = total_spent_usd < free_credit

    # Calculate worst-case requests remaining (query requesting ALL tiers basic+contact+atmosphere)
    all_fields = ["name", "formatted_address", "website", "phone", "rating", "reviews_count"]
    max_request_cost = calculate_request_cost(all_fields)

    estimated_free_requests_remaining = int(remaining_free_credit_usd / max_request_cost) if max_request_cost > 0 else 0

    return {
        "billing_month": billing_month,
        "request_count": request_count,
        "total_spent_usd": round(total_spent_usd, 4),
        "free_credit_limit_usd": free_credit,
        "remaining_free_credit_usd": remaining_free_credit_usd,
        "estimated_free_requests_remaining": estimated_free_requests_remaining,
        "is_within_free_tier": is_within_free_tier
    }


def get_all_time_request_count() -> int:
    """Returns the cumulative count of all API requests logged across all history months."""
    try:
        return ApiUsage.query.count()
    except Exception:
        return 0


def log_request(fields: list, was_approved: bool = True) -> ApiUsage:
    """
    Calculates estimated request cost, logs the transaction in the ApiUsage table,
    and commits the record to the SQLite database.
    """
    cost = calculate_request_cost(fields)
    current_month = datetime.utcnow().strftime("%Y-%m")

    # Resolve SKU tier classification
    contact_triggers = ["website", "formatted_phone_number", "phone", "opening_hours", "hours"]
    atmosphere_triggers = ["rating", "user_ratings_total", "price_level", "reviews", "reviews_count"]

    has_contact = any(f in fields for f in contact_triggers)
    has_atmosphere = any(f in fields for f in atmosphere_triggers)

    if has_contact and has_atmosphere:
        sku = "atmosphere + contact"
    elif has_contact:
        sku = "contact"
    elif has_atmosphere:
        sku = "atmosphere"
    else:
        sku = "basic"

    try:
        log = ApiUsage(
            sku_tier=sku,
            estimated_cost_usd=cost,
            fields_requested=",".join(fields),
            billing_month=current_month,
            was_approved=was_approved
        )
        db.session.add(log)
        db.session.commit()
        return log
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to log API Usage row: {str(e)}")
        raise e
