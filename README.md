# MODEL SUBSTITUTION GOVERNANCE & AUDIT PLATFORM

**Real-Time Monitoring, Capability Risk Assessment, and Compliance Auditing for Dynamic LLM Gateway Model Routing**

---

## LIVE PRODUCTION LINKS

* **GitHub Repository**: [Rithika-Gurusamy/Model-Substitution-Governance-Event](https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-)
* **Live Web Dashboard**: [model-substitution-governance-event.vercel.app](https://model-substitution-governance-event.vercel.app)
* **Cloud API Engine**: [model-substitution-governance-event.onrender.com](https://model-substitution-governance-event.onrender.com)
* **OpenAPI / Swagger Specs**: [model-substitution-governance-event.onrender.com/docs](https://model-substitution-governance-event.onrender.com/docs)
* **SDK GitHub Release**: [v1.0.0 Release Package](https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-/releases/download/v1.0.0/governance-interceptor-v1.0.0.zip)

---

## EXECUTIVE SUMMARY

Modern AI applications use **LLM Gateways** (such as LiteLLM, Portkey, or custom routing services) to dynamically route prompt requests based on cost, latency, or rate limits. When a high-capability model (e.g., `GPT-4o` or `Claude 3.5 Sonnet`) is swapped for a smaller model (e.g., `Gemini 1.5 Flash` or `GPT-4o Mini`), **silent model substitutions** occur.

Without governance tracking:
* **Context Degradation**: Shrinking context windows (e.g., 200k tokens down to 128k) cause subtle reasoning failures or truncation in multi-turn workflows.
* **Compliance & Policy Violations**: AI agents may route prompts to unapproved or non-whitelisted model providers in regulated environments (e.g., HIPAA, SOC2, GDPR).
* **Zero Visibility**: Gateway administrators have no unified audit trail mapping requested vs. actual models used across organizational teams.

This platform provides a complete governance solution: a **Zero-Latency Interceptor SDK**, a **FastAPI Cloud Backend**, a **PostgreSQL (Supabase) Database**, and a real-time **Vercel Interactive Dashboard**.

---

## KEY FEATURES & CAPABILITIES

* **ZERO-LATENCY INTERCEPTOR SDK (`governance_interceptor`)**:
  - Intercepts gateway routing decisions in memory.
  - Automatically compares `requested_model` vs. `actual_model`.
  - Sends non-blocking background HTTP requests to the cloud tracker without slowing down LLM response streaming.

* **CAPABILITY RISK ASSESSOR ENGINE**:
  - Evaluates original vs. substituted model capability profiles (Context Window size, Max Output Tokens, Provider tier).
  - Automatically calculates context downgrade % and assigns risk severity ratings (**LOW**, **MEDIUM**, **HIGH**, **CRITICAL**).

* **AGENT COMPLIANCE & WHITELIST ENGINE**:
  - Enforces strict per-agent model whitelists.
  - Instantly flags unauthorized model substitutions (e.g., if a `Finance-Agent` is restricted to OpenAI but routed to an external provider).

* **RETROACTIVE COMPLIANCE AUDIT ENGINE**:
  - Performs batch compliance audits across historical log data.
  - Computes organizational flag rates, high-risk exposure percentages, and unapproved request metrics.

* **MULTI-TENANT DATA ISOLATION & API SECURITY**:
  - Secure account isolation using **Supabase JWT authentication** and **Hashed Developer API Keys** (`usr_live_...`).
  - Automatic database-level scoping ensuring users only access their own organization's logs and agents.

* **INTERACTIVE LIVE SIMULATOR ("TRY DEMO")**:
  - Built-in live traffic simulator allowing prospective users and evaluators to trigger simulated gateway model substitutions with 1-click visual feedback and guided walkthrough prompts.

---

## SYSTEM ARCHITECTURE & WORKFLOW

```text
+-----------------------------------------------------------------------------------+
|                            CLIENT APPLICATION / AI AGENT                          |
|  Sends prompt request specifying Target Requested Model (e.g., GPT-4o)            |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                              LLM GATEWAY ROUTER ENGINE                            |
|  Evaluates routing rules (Cost budgets, availability, token length)               |
|  Selects Actual Model to invoke (e.g., Gemini 1.5 Flash)                          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            GOVERNANCE INTERCEPTOR SDK                             |
|  Checks if Requested Model != Actual Model Used                                   |
|  Posts asynchronous HTTP event to Cloud Tracker with Developer API Key            |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        FASTAPI CLOUD TRACKER ENGINE (Render)                      |
|  1. Authenticates Developer API Key & resolves Organization Scope                 |
|  2. Risk Assessor Engine calculates Context Downgrade % & Risk Level              |
|  3. Compliance Engine verifies Agent Whitelist & flags policy violations          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         SUPABASE POSTGRESQL DATABASE                              |
|  Persists structured event records, risk analytics, and compliance audit logs     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         VERCEL GOVERNANCE DASHBOARD UI                            |
|  Displays real-time event logs, risk distribution matrices, and audit reports     |
+-----------------------------------------------------------------------------------+
```

---

## QUICK START & LOCAL SETUP

### Prerequisites
* **Python 3.10+**
* **Pip** (Python Package Installer)
* **PostgreSQL Database** (Supabase or Local Postgres)

### 1. Clone the Repository
```bash
git clone https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-.git
cd Model-Substitution-Governance-Event
```

### 2. Set Up Python Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
DATABASE_URL="postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres"
SUPABASE_URL="https://[YOUR_PROJECT_REF].supabase.co"
SUPABASE_ANON_KEY="your-supabase-anon-key"
SUPABASE_JWT_SECRET="your-supabase-jwt-secret"
SECRET_KEY="your-backend-secret-key"
```

### 5. Run the Cloud Backend Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
* Interactive Swagger OpenAPI documentation will be live at: `http://localhost:8000/docs`

### 6. Launch the Dashboard
Open `frontend/index.html` directly in your browser, or serve it using any HTTP server:
```bash
python -m http.server 3000 --directory frontend
```
Navigate to `http://localhost:3000`.

---

## REPOSITORY & PROJECT STRUCTURE

Below is a guide to the project layout:

```text
Model-Substitution-Governance-Event/
├── backend/                             # FastAPI Backend Engine
│   ├── app/
│   │   ├── auth.py                      # API Key Verification & Supabase JWT Auth Middleware
│   │   ├── config.py                    # Environment Configuration Settings
│   │   ├── database.py                  # SQLAlchemy Supabase PostgreSQL Session Manager
│   │   ├── main.py                      # FastAPI App Initialization, CORS & DDL Migrations
│   │   ├── models.py                    # SQLAlchemy ORM Schemas (Events, Agents, Model Profiles)
│   │   ├── schemas.py                   # Pydantic Request & Response Data Transfer Objects
│   │   ├── routers/
│   │   │   ├── auth_router.py           # Developer API Key & User Auth Endpoints
│   │   │   ├── compliance.py            # Retroactive Compliance Audit & Whitelist Endpoints
│   │   │   ├── events.py                # High-Throughput Event Ingestion & Search Endpoints
│   │   │   ├── models.py                # Model Capability Reference Directory Endpoints
│   │   │   └── statistics.py            # Executive KPI & Risk Matrix Aggregation Endpoints
│   │   └── services/
│   │       ├── compliance_service.py    # Agent Model Whitelist Verification Logic
│   │       └── risk_engine.py           # Capability Context Window Downgrade Risk Algorithm
│   └── requirements.txt                 # Python Production Backend Dependencies
│
├── frontend/                            # Single-Page Web Dashboard (Vanilla JS + Glassmorphism CSS)
│   ├── app.js                           # Dashboard State, Charts, Data Fetching & Interactive Demo
│   ├── config.js                        # Environment Base URLs (Render API Endpoint)
│   ├── index.html                       # Dashboard Layout (Tabs, Modals, Integration Guides)
│   └── styles.css                       # Modern Dark/Light Glassmorphism Design System
│
├── interceptor/                         # Lightweight Python SDK Package
│   ├── governance_interceptor/
│   │   ├── __init__.py                  # Package Exports
│   │   └── interceptor.py               # GovernanceInterceptor SDK Implementation
│   └── setup.py                         # PyPI & Pip Package Installer Setup
│
├── vercel.json                          # Vercel SPA Routing Configuration
├── README.md                            # Project Overview & Setup Documentation
└── governance-interceptor-v1.0.0.zip    # Standalone Interceptor SDK Distribution Archive
```

---

## INTERCEPTOR SDK INTEGRATION

Connecting your AI application or LLM Gateway to the Governance Tracker requires only **3 lines of code**:

### Installation
```bash
pip install governance-interceptor
```

### Usage
```python
import os
from governance_interceptor import GovernanceInterceptor

# 1. Initialize Interceptor (reads API_KEY and TRACKER_URL from environment)
interceptor = GovernanceInterceptor(
    tracker_url="https://model-substitution-governance-event.onrender.com",
    api_key=os.getenv("API_KEY")
)

# 2. Call interceptor after gateway model selection
interceptor.intercept(
    requested_model="GPT-4o",          # Model requested by client prompt
    actual_model="Gemini 1.5 Flash",    # Actual model selected by LLM Gateway
    reason="cost",                     # Routing reason: 'cost', 'availability', or 'policy'
    agent_id="Financial-Analyzer",      # Identifier of calling agent
    session_id="doc-proc-9902"          # Session / transaction reference ID
)
```

---

## LICENSE
Distributed under the **MIT License**. See `LICENSE` for details.
