import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_data import seed_database

from backend.app.routers.health import router as health_router
from backend.app.routers.events import router as events_router
from backend.app.routers.compliance import router as compliance_router
from backend.app.routers.models_and_agents import router as models_agents_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB Tables & Seed Data on Startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Model Substitution Governance & Compliance Tracking API",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(events_router, prefix=settings.API_V1_STR)
app.include_router(compliance_router, prefix=settings.API_V1_STR)
app.include_router(models_agents_router, prefix=settings.API_V1_STR)

# Serve Enterprise Dashboard Static Assets
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_dashboard():
        index_path = os.path.join(frontend_dir, "index.html")
        return FileResponse(index_path)
