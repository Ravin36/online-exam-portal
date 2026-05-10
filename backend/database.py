from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to constructing from Supabase URL if DATABASE_URL not set
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        # Extract project ref from URL
        project_ref = SUPABASE_URL.split("https://")[1].split(".")[0]
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_SERVICE_ROLE_KEY}@db.{project_ref}.supabase.co:5432/postgres"

if not DATABASE_URL:
    raise ValueError("DATABASE_URL or SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY must be set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()