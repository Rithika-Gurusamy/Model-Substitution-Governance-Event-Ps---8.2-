# Model Substitution Governance Tracker 🛡️

A comprehensive enterprise governance platform designed for **LLM Gateways** to intercept, record, risk-assess, and audit model substitutions in real-time.

---

## 📌 Problem Context & Challenge

LLM gateways routinely substitute models for **cost**, **availability**, or **policy** reasons—routing to a smaller model when budget limits are reached or switching providers during outages. Traditionally, this is treated as a silent routing decision, leaving compliance logs claiming the requested model was used. However, substituted models often possess significantly different context capacities, safety guardrail behaviors, and bias characteristics.

**Model Substitution Governance Tracker** captures every model substitution as a formal **Governance Event**, evaluating capability risk and enforcing agent compliance policies.

---

## 🏗️ Architecture Overview

```
Customer's LLM Gateway
        │
  (select_model)
        │
        ▼
Governance Interceptor (Python SDK)
        │
  [requested != actual?]
        │ POST /events
        ▼
Cloud Tracker Service (FastAPI)
        ├── Governance Event Recorder
        ├── Capability & Risk Assessor
        ├── Compliance Engine
        └── PostgreSQL / Database
                 │ REST API (/events, /compliance, /models)
                 ▼
 Enterprise Dashboard (HTML5 / CSS3 / Vanilla JS)
```

### Core Deliverables

1. **Governance Interceptor (`interceptor/`)**: Lightweight Python SDK package (`governance-interceptor`) integrated directly into customer LLM gateways to detect when `requested_model != actual_model`.
2. **FastAPI Cloud Tracker Backend (`backend/`)**: High-performance REST service providing event ingestion, deterministic risk assessment, agent compliance enforcement, and retroactive exposure auditing.
3. **Enterprise Governance Dashboard (`frontend/`)**: Modern glassmorphic web dashboard with live event stream, risk matrix modal, agent whitelist manager, and retroactive audit reporter.
4. **Gateway Substitution Simulator (`examples/`)**: Runnable demonstration showcasing Cost, Availability, and Policy substitution triggers.

---

## ✨ Features & Governance Logic

### 1. Interceptor SDK
- **Non-blocking Execution**: Captures substitution events and sends them asynchronously or with fail-safe fallbacks without blocking the main LLM pipeline.
- **Automatic Delta Detection**: Evaluates `requested_model == actual_model` before posting.

### 2. Risk Assessor Engine
Determines a material capability downgrade using multi-dimensional comparisons:
- **Context Window Drop**: Flags `High` / `Critical` risk if context window drops significantly (e.g., `128,000` to `32,000` tokens).
- **Guardrail Level Downgrade**: Detects safety drops (e.g., `High` to `Medium` or `Low`).
- **Bias Score Degradation**: Monitors changes in bias benchmarks.

### 3. Compliance Flag Engine
- Compares `actual_model` against agent-specific **Approved Model Whitelists**.
- Automatically sets `compliance_flagged = True` and records detailed compliance violation reasons if substitution lands outside approved bounds.

### 4. Retroactive Compliance Exposure Audit (Bonus Feature)
- Scans historical event logs over custom time ranges to compute:
  - Total requests served by non-approved models.
  - Overall compliance violation rate.
  - High-risk exposure ratio.
  - Affected agent statistics.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Install Dependencies & SDK

```bash
# Clone the repository
git clone https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-.git
cd Model-Substitution-Governance-Event-Ps---8.2-

# Install Backend dependencies
pip install -r backend/requirements.txt

# Install Governance Interceptor SDK locally
pip install -e interceptor/
```

### 3. Run the Backend API & Dashboard

```bash
# Start the FastAPI server (serves REST API and Frontend Dashboard at http://localhost:8000)
python -m uvicorn backend.app.main:app --reload --port 8000
```

Open your browser to:
- **Enterprise Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Specs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Trigger Gateway Substitution Simulator

In a second terminal, run the gateway simulator to generate sample substitution events across all 3 scenarios:

```bash
python examples/gateway_sim.py
```

Observe the events appearing live on the dashboard!

### 5. Run Automated Tests

```bash
python -m pytest backend/tests
```

---

## 📡 API Endpoint Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/events` | Record a model substitution event & trigger risk/compliance assessment |
| `GET` | `/events` | Query governance events (filter by `agent_id`, `reason`, time range, `compliance_flagged`, `risk_level`) |
| `GET` | `/events/{id}` | Inspect details of a specific governance event record |
| `GET` | `/compliance/audit` | Generate retroactive compliance impact & exposure report |
| `GET` | `/models` | View supported model capability profiles |
| `GET` | `/agents` | View agent whitelist compliance policies |

---

## 📦 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI Entrypoint & CORS setup
│   │   ├── database.py                # SQLAlchemy DB session engine
│   │   ├── models/models.py           # DB Models (GovernanceEvent, ModelProfile, Agent)
│   │   ├── schemas/schemas.py         # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── risk_assessor.py       # Capability risk assessment logic
│   │   │   └── compliance_engine.py   # Whitelist compliance & audit engine
│   │   └── routers/
│   │       ├── events.py              # Ingestion & event query endpoints
│   │       ├── compliance.py          # Audit report endpoints
│   │       └── models_and_agents.py   # Profiles & policy endpoints
│   ├── requirements.txt
│   └── tests/test_backend.py          # Pytest suite
├── interceptor/
│   ├── governance_interceptor/        # Interceptor SDK source
│   │   ├── __init__.py
│   │   └── interceptor.py
│   └── setup.py                       # Packaging setup script
├── frontend/
│   ├── index.html                     # Enterprise dashboard layout
│   ├── styles.css                     # Dark mode & glassmorphism styles
│   └── app.js                         # REST integration & UI interactivity
├── examples/
│   └── gateway_sim.py                 # Gateway substitution simulator script
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
