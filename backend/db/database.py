# backend/db/database.py
# Database connection setup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Railway PostgreSQL URLs start with "postgres://" (old format)
# SQLAlchemy needs "postgresql://" (new format)
# This fixes that automatically
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# engine = actual connection to database
engine = create_engine(DATABASE_URL)

# SessionLocal = factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Provides a database session to API routes.
    Opens session, yields it, closes when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()