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

## 🔮 Future AI and Scraping Roadmap

Company Finder has been deliberately structured to allow seamless expansion:

1. **Swapping Data Providers (`app/services/data_provider.py`):**
   * Currently, the system runs on a deterministic, realistic mock listing service (`MockDataProvider`).
   * To upgrade to live Google Maps listings, create `app/services/google_maps_service.py` inheriting from `BaseDataProvider` and configure it to query the standard Google Places API. Swap references inside `search_service.py` with one line of code.
2. **Upgrading Scraper Audits (`app/services/mock_service.py`):**
   * Hook up real web crawling engines! Integrate standard libraries like `requests` and `beautifulsoup4` inside the data provider class to crawl websites, checking for meta tags, loading times, and active SSL ports in real-time.
3. **Integrating OpenAI/Claude LLM APIs (`app/services/ai_service.py`):**
   * Replace mock AI strings with live Anthropic SDK calls!
   * Query the Claude API (e.g., `claude-haiku-4-5-20251001` for cost-effective speed or `claude-sonnet-4-6` for deep insights) passing the scraped business profile. Ask the model to generate a custom email cold-pitch sequence or a customized website redesign scope dynamically.
