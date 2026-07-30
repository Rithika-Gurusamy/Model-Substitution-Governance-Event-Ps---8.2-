# Model Substitution Governance Tracker

An enterprise AI governance platform for monitoring, recording, risk assessing, and auditing LLM Gateway model substitutions.

## Architecture Overview

```
Developer / Gateway Admin
       │
       ▼
GitHub Releases CDN (Global Distribution)
       │
       ├── Download Governance Interceptor SDK (v1.0.0)
       ├── Download Sample Gateway (v1.0.0)
       │
       ▼
Install into Enterprise LLM Gateway
       │
       ├── Routing Decision (Requested != Actual Model)
       │
       ▼
Governance Tracker Cloud API (FastAPI on Render)
       ├── Ingestion & Event Validation
       ├── Context Window Risk Assessor Engine
       ├── Agent Whitelist Compliance Engine
       │
       ▼
PostgreSQL Database (Supabase)
       │
       ▼
Enterprise Governance Dashboard (Vercel)
```

## SDK Distribution

The **Governance Interceptor SDK** is distributed via **GitHub Releases**.

### Why GitHub Releases?
- **Global CDN**: Instant artifact downloads without backend cold starts.
- **Versioned Releases**: Clean enterprise release management (`v1.0.0`, `v1.1.0`).
- **Separation of Responsibilities**: The FastAPI cloud backend is reserved exclusively for high-throughput governance APIs.

## Installation

```bash
pip install governance-interceptor
```

Or download release zip packages directly from GitHub Releases:
- **SDK Package**: `governance-interceptor-v1.0.0.zip`
- **Sample Gateway**: `sample-gateway-v1.0.0.zip`

## Quick Start (Gateway Integration)

```python
from governance_interceptor import GovernanceInterceptor

interceptor = GovernanceInterceptor(tracker_url="https://model-substitution-governance-event.onrender.com")

# After routing decision:
interceptor.intercept(
    requested_model="GPT-5",
    actual_model="GPT-4o Mini",
    reason="cost",
    agent_id="HR-Agent",
    session_id="sess-101"
)
```

## Production Deployment URLs
- **Enterprise Web Dashboard**: [https://model-substitution-governance-event.vercel.app](https://model-substitution-governance-event.vercel.app)
- **FastAPI Cloud Backend**: [https://model-substitution-governance-event.onrender.com](https://model-substitution-governance-event.onrender.com)
- **OpenAPI Swagger Specs**: [https://model-substitution-governance-event.onrender.com/docs](https://model-substitution-governance-event.onrender.com/docs)
