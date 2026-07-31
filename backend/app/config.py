from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Model Substitution Governance Tracker"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    
    DATABASE_URL: str = "postgresql://postgres.fzluhjcenawlekrqdlxb:thisismyseconddeploy@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
    CORS_ORIGINS: List[str] = ["*"]
    API_PREFIX: str = "/api/v1"
    
    SUPABASE_URL: str = "https://fzluhjcenawlekrqdlxb.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6bHVoamNlbmF3bGVrcnFkbHhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzNTEwMTAsImV4cCI6MjEwMDkyNzAxMH0.TVumRBiAFlF-x4YOs8jyaAQXOg8Y616HUcK3SY9tYYo"
    SUPABASE_JWT_SECRET: str = "kg7gGK+/Nv7ZqTUYkp6ynZ3B9ouiGTkzgB9Nho9cyyNGHATX/UFOb2jfGWqrVY5O5xB9hsuDYmdhZgY+tFcf9Q=="

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
