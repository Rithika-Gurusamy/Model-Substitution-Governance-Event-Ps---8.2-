import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from .database import engine, Base, SessionLocal
from .models.models import ModelProfile, Agent
from .routers import events, compliance, models_and_agents
from .services.risk_assessor import DEFAULT_MODEL_PROFILES
from .services.compliance_engine import DEFAULT_AGENT_POLICIES

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed database with initial profiles if empty
    db = SessionLocal()
    try:
        if db.query(ModelProfile).count() == 0:
            for name, data in DEFAULT_MODEL_PROFILES.items():
                profile = ModelProfile(
                    model_name=name,
                    context_window=data["context_window"],
                    guardrail_level=data["guardrail_level"],
                    bias_score=data["bias_score"],
                    description=f"Standard benchmark profile for {name}"
                )
                db.add(profile)
        
        if db.query(Agent).count() == 0:
            for agent_id, approved in DEFAULT_AGENT_POLICIES.items():
                agent = Agent(
                    agent_id=agent_id,
                    agent_name=f"{agent_id} Production",
                    approved_models=approved
                )
                db.add(agent)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning during startup data seeding: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title="Model Substitution Governance Tracker API",
    description="Enterprise API to record, assess capability risk, and audit model substitutions across LLM Gateways.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(events.router)
app.include_router(compliance.router)
app.include_router(models_and_agents.router)

# Mount Frontend Dashboard static files if directory exists
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_dashboard():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy", "service": "Model Substitution Governance Tracker"}
