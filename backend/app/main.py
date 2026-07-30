import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.database import engine, Base, get_db
from backend.app.seed_data import seed_database
from backend.app.routers import health, events, compliance, models_and_agents, auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables
    Base.metadata.create_all(bind=engine)

    # Seed Database with models, agents, policies, and initial demo events
    try:
        db = next(get_db())
        seed_database(db)
        print("Database seeded successfully with model profiles, agents, and demo events.")
    except Exception as e:
        print(f"Warning: Seed database error: {e}")

    yield

app = FastAPI(
    title="Model Substitution Governance Tracker API",
    description="Enterprise Governance APIs for Monitoring, Recording, Risk Assessing, and Auditing LLM Gateway Model Substitutions",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers with /api/v1 prefix
API_PREFIX = "/api/v1"
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(auth_router.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(compliance.router, prefix=API_PREFIX)
app.include_router(models_and_agents.router, prefix=API_PREFIX)

# Mount frontend static directory if exists
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/dashboard", StaticFiles(directory=frontend_dir, html=True), name="dashboard")
