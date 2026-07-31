import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from backend.app.database import engine, Base, get_db
from backend.app.seed_data import seed_database
from backend.app.routers import health, events, compliance, models_and_agents, auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create DB tables via SQLAlchemy Metadata
    Base.metadata.create_all(bind=engine)

    # 2. Additive DDL Schema Migration: Ensure user_profile_id columns & api_keys table exist
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS user_profile_id VARCHAR;"))
            conn.execute(text("ALTER TABLE governance_events ADD COLUMN IF NOT EXISTS user_profile_id VARCHAR;"))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id VARCHAR PRIMARY KEY,
                    key_prefix VARCHAR(12) NOT NULL,
                    key_hash VARCHAR(64) NOT NULL UNIQUE,
                    user_profile_id VARCHAR NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE
                );
            """))
            conn.commit()
            print("Database schema migration: user_profile_id columns & api_keys table verified.")
    except Exception as e:
        print(f"Notice: Schema migration check: {e}")

    # 3. Seed Database with models, agents, policies, and demo events
    try:
        db = next(get_db())
        seed_database(db)
        print("Database seeded successfully with model profiles, agents, and demo user data.")
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
