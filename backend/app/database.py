import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

logger = logging.getLogger("DatabaseSetup")

db_url = settings.DATABASE_URL

# Safe Engine Initialization with SQLite Fallback for Cloud Hosting (Render IPv4 compatibility)
try:
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        # PostgreSQL / Supabase pool configuration with timeout
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 5}
        )
        # Test connection ping
        with engine.connect() as conn:
            logger.info("Successfully connected to remote PostgreSQL database.")
except Exception as e:
    logger.warning(f"Failed to connect to primary DATABASE_URL ({db_url}): {e}. Falling back to local SQLite engine.")
    engine = create_engine("sqlite:///./governance.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
