# Company Finder - Local B2B Lead Generation & Web Presence Scraper

**Company Finder** is a production-quality, full-stack B2B lead-generation web application. Designed for web development agencies, digital marketers, and freelancers, it identifies local businesses with weak, outdated, insecure, or non-existent web presences, calculates a custom **0-100 Website Opportunity Score**, and organizes them into Project workspaces to drive cold outreach campaigns.

---

## 🚀 Key Features

1. **SaaS Dashboard & Workspaces:** Clean responsive navigation with dark/light theme switching, statistics panels tracking total leads, average opportunity scores, and pipeline progress.
2. **Advanced Search & Filtering:** Filter leads by industry suggests, location, crawling radius, Google star ratings, public review quantity counts, and contact detail requirements.
3. **0-100 Opportunity Score Engine:** Custom scoring heuristics that rate leads based on web presence factors, online social presence reliance, and business potential demand, classifying targets into Very High, High, Medium, or Low opportunity tiers.
4. **AI-Assisted Pitch Analyst:** Automatically drafts customized recommended service proposals, project complexity estimates, and overall contract valuation tiers (Small, Medium, Large) for each prospect.
5. **Spreadsheet Exporters:** Stream scored targets directly into CSV and Excel formats with absolute UTF-8 BOM encoding for seamless Microsoft Excel compatibility.
6. **Lead Profile Cockpits:** Log outreach events (emails, calls, walk-ins), write rich personal notes, and move candidates along the pipeline (Raw Lead, Contacted, Meeting Booked, Closed Won, Closed Lost).

---

## 🛠️ Technology Stack

* **Backend:** Python 3 + Flask (Modular Application Factory architecture)
* **Database & ORM:** SQLite + Flask-SQLAlchemy (Cascades, relationships, and custom JSON serializations)
* **Frontend:** Vanilla HTML5 / Jinja2 Templates + Bootstrap 5.3 + Bootstrap Icons
* **Scripting:** Vanilla JavaScript (Theme loaders, dynamic loading overlays, and dynamic table search/sort/pagination)

---

## 📁 Project Directory Structure

```
leadfinder/
│
├── claude_memory/              # Persistent memory tracking files
│   ├── 1_PROJECT_GOALS.md
│   ├── 2_ARCHITECTURE.md
│   └── 3_ACTIVE_STATE.md
│
├── app/
│   ├── __init__.py             # Flask App Factory with logging configuration
│   ├── routes/                 # Modular Blueprint controller packages
│   │   ├── __init__.py
│   │   ├── main.py             # Home views and dashboards
│   │   ├── search.py           # Filtration forms, history lists, and spreadsheet exports
│   │   └── business.py         # Lead profile cockpits, notes, and outreach logs
│   ├── models/                 # SQLAlchemy database schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── search.py           # Custom JSON filter properties and history triggers
│   │   ├── business.py         # Business and BusinessScore schema declarations
│   │   └── outreach.py         # Notes and ContactHistory logs schemas
│   ├── services/               # Business logic core layers
│   │   ├── __init__.py
│   │   ├── data_provider.py    # Interface abstraction for swappable provider APIs
│   │   ├── mock_service.py     # Deterministic lead generation simulations
│   │   ├── scoring_service.py  # 0-100 opportunity scores & narrative compiler
│   │   └── ai_service.py       # AI-driven consulting pitches placeholder
│   ├── templates/              # Base and child Jinja2 template layers
│   └── static/                 # Stylesheets and frontend Vanilla JS
│
├── requirements.txt            # Python environment dependencies
├── .env                        # Local configurations variables template
├── run.py                      # Main entrypoint executable
├── init_db.py                  # Database tables setup script
└── README.md                   # System user guide
```

---

## ⚙️ Development Installation & Local Run

To boot up and run Company Finder locally on your system, execute the following commands in sequence:

### 1. Initialize Virtual Environment & Packages
Create your virtual environment (if not already created) and activate it:
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required modules
pip install -r requirements.txt
```

### 2. Configure Environment Parameters
Create a `.env` file at the root of the project to hold secret configurations (or keep default fallback development settings):
```env
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-me
```

### 3. Initialize the Local SQLite Database
Run the database setup script to generate SQLite database tables:
```powershell
python init_db.py
```
This script automatically:
* Establishes the standard SQLite instance path at `instance/company_finder.db`.
* Translates all 7 SQLAlchemy schema files into SQLite schemas.
* Inserts initial dummy authorization profiles and campaign projects.

### 4. Launch the Local Development Server
Execute the application runner:
```powershell
python run.py
```
Open your web browser and navigate to: **`http://127.0.0.1:5000/`** to enter the Company Finder workspace!

---

## 📊 Website Opportunity Score Heuristics

The scoring engine in `app/services/scoring_service.py` evaluates targets on a `0-100` scale. The score represents the **B2B sales opportunity size** (higher score = weaker web footprint = more receptive sales target):

### 1. Website Factors (Maximum 50 points)
* **Lacks Website completely:** **+40 points**
* **Website listed but unreachable (DNS/hosting timeout):** **+30 points**
* **Website resolves with major loading errors:** **+30 points**
* **Abandoned/Outdated attributes:** **+20 points**
  * Lacks mobile-responsive views: **+15 points**
  * Missing secure HTTPS (unsecured HTTP): **+15 points**
  * Load speed exceeding 3.0 seconds: **+10 points**

### 2. Online Presence Factors (Maximum 30 points)
* **Relying solely on social media (Facebook/Instagram profiles):** **+20 points**
* **Missing critical GMB details (Phone/Email omitted):** **+10 points**

### 3. Business Potential Factors (Maximum 20 points)
* **Strong consumer demand offset:** Highly rated or reviewed business (Rating $\ge$ 4.2 or reviews $\ge$ 50) that suffers from a weak web presences represents an optimal, high-value conversion prospect: **+20 points**

---

## 🔌 Configuring Real Google Places API & Live Crawler

Company Finder is pre-wired for seamless switching between offline simulations and real, live-crawled local business directories.

### 1. Activating Live Google Places Searches
To query live businesses in any city globally instead of mock data:
1. Open your `.env` file at the root of the project.
2. Toggle the data provider variable:
   ```env
   DATA_PROVIDER=google
   ```
3. Set your Google Cloud API key:
   ```env
   GOOGLE_PLACES_API_KEY=your_actual_google_places_api_key_here
   ```

### 2. Google Cloud Console Requirements
For the `google` provider to successfully run searches, your Google API Key must have the following configurations enabled:
* **Required API Libraries:** You must enable the **Places API** (not the legacy Places API, ensure the modern Places API is active) inside your Google Cloud Console project.
* **Billing Enabled:** Google Cloud requires a valid billing account linked to your project to run Places queries, though they provide a free monthly credit tier.
* **API Restrictions (Recommended):** To secure your API Key, restrict its usage to the *Places API* only under "Key Restrictions" in your API Credentials dashboard.

### 3. Live Web Scraper Architecture (`app/services/scraper_service.py`)
When you execute a scan or click the **"Re-Audit Website"** button inside a lead's cockpit, the system triggers a real-time HTTP crawler:
* **SSL-Resilient Crawling:** Checks SSL certificates natively. If a domain has an expired, invalid, or self-signed certificate, the crawler catches the `SSLError` defensively and falls back to an unverified HTTPS/HTTP request (`verify=False`). This enables the crawler to safely extract metadata from broken domains without crashing.
* **Metadata Extractors:** Uses `BeautifulSoup` to parse HTML, checking for meta responsive parameters (`viewport` tags), SEO indicators (`<title>` and `<meta name="description">`), open graph tags (`og:title`), and CMS signatures (auto-fingerprints WordPress, Wix, Squarespace, and Shopify).
* **Defensive Failure Fallbacks:** If a live crawl fails (network timeouts, DNS errors), the backend catches the error and falls back to mock evaluations, ensuring a single slow website never interrupts your search result queries!


## 💰 API Credit Management & Google Cloud Billing

Company Finder includes a high-end, real-time Google Cloud Platform Billing and Budget Tracker inside `app/services/billing_service.py` to prevent any unexpected charges and keep your searches safely inside Google Maps Platform's free tier credits!

### 1. Active Configuration Variables (.env)
To track live project pricing and budgets, configure your Google Cloud identifiers:
```env
# GCP Identifiers
GOOGLE_CLOUD_PROJECT_ID=your_gcp_project_id
GOOGLE_BILLING_ACCOUNT_ID=your_billing_account_id
```

### 2. Live SKU Pricing & Catalog Cache
* **Google Billing Catalog API:** On startup, the application queries Google's live Catalog API (`cloudbilling.googleapis.com`) for modern Maps Platform Places SKUs.
* **Matched Tiers:** Extracts real-time unit pricing for three specific tiers matching descriptions:
  - *Places API - Place Details - Basic* (always added)
  - *Places API - Place Details - Contact* (website, phone, and opening hours fields)
  - *Places API - Place Details - Atmosphere* (rating, review counts, and price levels)
* **24-Hour Cache:** Pricing values are cached in memory for 24 hours to avoid hitting the Billing API on every lead scan.
* **Defensive Fallback Sentinels:** If connection to Google Cloud Billing fails (due to lack of OAuth/GCP setup), the engine logs a `WARNING` and falls back to these secure hardcoded sentinel rates: `{"basic": 0.017, "contact": 0.003, "atmosphere": 0.005}`.

### 3. Monthly Budgets & Approval Gate Checks
* **Budgets API Integration:** Queries `billingbudgets.googleapis.com` for billing account budget settings. If not configured or unreachable, defaults to Google's standard **$200.00** monthly Maps free credit.
* **Pre-Request Approval Gate:** Before launching Place Details queries, the system checks the current month's SQLite usage logs (`ApiUsage` table).
* **Payment Required Interrupt (HTTP 402):** If your monthly spent reaches your configured free budget threshold, the backend blocks the Places query, and returns a JSON payload with **`HTTP 402 Payment Required`** containing the estimated cost of the request.
* **Interactive Modal Authorization:** The frontend JavaScript intercepts the `402` state and triggers a beautiful **Free Credit Exhausted** modal. If you click "Approve & Continue", the request is re-sent with an `X-User-Approved: true` header. The backend parses this, executes the Places Details query, and commits the transaction log with `was_approved=True`.

### 4. Billing Monitor Dashboard API Endpoints
* **`GET /search/api/usage/summary`:** Single source of truth for the frontend dashboard panels, returning total spent, request counts, remaining free requests, and cache metrics.
* **`GET /search/api/billing/prices`:** Exposes cached pricing data and pricing source (tooltip reveals if "Live Pricing" or "⚠️ Fallback Pricing Active").

> ⚠️ **IMPORTANT NOTE:** Local `ApiUsage` tracking is an estimate computed on your database transactions logs and does not replace the Google Cloud Console billing dashboard as your authoritative billing source. Always verify budget alerts on your Google Cloud Platform console!
