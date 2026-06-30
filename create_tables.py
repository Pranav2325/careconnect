# This script creates all our database tables in PostgreSQL based on our models

from backend.db.database import engine
from backend.db.models import Base

print("Creating tables...")

# This line reads all our model classes and creates matching tables in PostgreSQL
Base.metadata.create_all(bind=engine)

print("✅ All tables created successfully!")