import requests
import time
import logging
from bs4 import BeautifulSoup
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress insecure SSL warnings for scraper requests made with verify=False
urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger('company_finder')

def is_social_media_url(url: str) -> bool:
    """Helper to detect if a URL belongs to a social media platform instead of a dedicated business website."""
    if not url:
        return False
    social_domains = [
        'facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com',
        'youtube.com', 'pinterest.com', 'tiktok.com', 'tumblr.com', 'reddit.com'
    ]
    cleaned_url = url.lower().strip()
    return any(domain in cleaned_url for domain in social_domains)

def audit_website(url: str) -> dict:
    """
    Performs a real, live HTTP/HTTPS crawl of the given URL to audit its technical and presence metrics.
    Employs an intelligent SSL-fallback routine and parses SEO metadata, responsive viewports,
    contact signals, and CMS fingerprints.

    Args:
        url (str): The website domain or link of the local business.

    Returns:
        dict: Detailed audit specifications containing status, reachability, SSL, meta tags, responsive viewport,
              contact signals, CMS fingerprint, load time, and headers.
    """
    # 1. Immediate exit for empty, missing, or social media URLs
    if not url:
        return {"status": "no_website"}

    if is_social_media_url(url):
        logger.info(f"Classified {url} as social media profile only (not a dedicated website).")
        return {
            "status": "no_website",
            "has_website": False,
            "is_social_media_only": True,
            "social_links_count": 1,
            "is_responsive": False,
            "has_ssl": False,
            "load_time_seconds": 0.0
        }

    # Clean and normalize URL scheme
    target_url = url.strip()
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    start_time = time.time()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    response = None
    reachability = False
    has_ssl = False
    ssl_error = False
    status_code = None
    load_time = 0.0

    # 2. First attempt: Standard verification with SSL validation
    try:
        response = requests.get(target_url, timeout=5.0, headers=headers, verify=True)
        load_time = round(time.time() - start_time, 2)
        status_code = response.status_code
        reachability = response.ok
        has_ssl = response.url.lower().startswith('https://')
    except requests.exceptions.SSLError as e:
        ssl_error = True
        logger.warning(f"SSL certificate validation failed for {target_url}, attempting fallback check: {str(e)}")
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
        logger.warning(f"Crawl connection failed for {target_url}: {str(e)}")
        return {
            "status": "unreachable",
            "reachability": False,
            "has_website": True,
            "has_ssl": False,
            "ssl_error": False,
            "status_code": None,
            "load_time_seconds": 5.0
        }

    # 3. Second attempt (Fallback): Disable SSL verification if SSL check raised error
    if ssl_error:
        try:
            start_time = time.time()
            response = requests.get(target_url, timeout=5.0, headers=headers, verify=False)
            load_time = round(time.time() - start_time, 2)
            status_code = response.status_code
            reachability = response.ok
            has_ssl = False  # SSL is present but expired/broken/unverified
        except Exception as e:
            logger.warning(f"Fallback connection failed for {target_url}: {str(e)}")
            return {
                "status": "unreachable",
                "reachability": False,
                "has_website": True,
                "has_ssl": False,
                "ssl_error": True,
                "status_code": None,
                "load_time_seconds": 5.0
            }

    # 4. Technical Scraping via BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Mobile viewport detection
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    is_responsive = False
    if viewport and 'width=device-width' in viewport.get('content', '').lower():
        is_responsive = True

    # SEO Metadata extraction
    title = soup.find('title')
    title_text = title.text.strip() if title else ""

    desc_meta = soup.find('meta', attrs={'name': 'description'})
    desc_text = desc_meta.get('content', '').strip() if desc_meta else ""

    # Open Graph tags check
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    has_og = True if (og_title or og_desc) else False

    # Contact signals crawling (tel: and mailto: links) and social links count
    has_tel_links = False
    has_mailto_links = False
    social_links_count = 0
    social_domains = ['facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com', 'youtube.com']

    for a in soup.find_all('a', href=True):
        href = a['href'].lower().strip()
        if href.startswith('tel:'):
            has_tel_links = True
        elif href.startswith('mailto:'):
            has_mailto_links = True
        elif any(domain in href for domain in social_domains):
            social_links_count += 1
            has_tel_links = True
        elif href.startswith('mailto:'):
            has_mailto_links = True

    # CMS Fingerprinting
    cms = "Unknown"
    html_text = response.text.lower()
    generator_meta = soup.find('meta', attrs={'name': 'generator'})
    generator_text = generator_meta.get('content', '').lower() if generator_meta else ""

    if "wp-content" in html_text or "wp-includes" in html_text or "wordpress" in generator_text:
        cms = "WordPress"
    elif "wix.com" in html_text or "wixstatic.com" in html_text:
        cms = "Wix"
    elif "squarespace.com" in html_text or "static1.squarespace.com" in html_text:
        cms = "Squarespace"
    elif "shopify.com" in html_text or "cdn.shopify.com" in html_text:
        cms = "Shopify"

    # Last-modified header extraction
    last_modified = response.headers.get('Last-Modified', 'Not provided')

    return {
        "status": "success",
        "reachability": reachability,
        "has_ssl": has_ssl,
        "ssl_error": ssl_error,
        "status_code": status_code,
        "load_time_seconds": load_time,
        "is_responsive": is_responsive,
        "seo_title": title_text,
        "seo_description": desc_text,
        "has_og_tags": has_og,
        "has_tel_links": has_tel_links,
        "has_mailto_links": has_mailto_links,
        "social_links_count": social_links_count,
        "cms_fingerprint": cms,
        "last_modified": last_modified,
        # Standard indicators for compatibility
        "has_website": True
    }
