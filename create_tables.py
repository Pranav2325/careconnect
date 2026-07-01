
# Purpose:
# This script creates all the database tables in PostgreSQL
# based on the SQLAlchemy models we defined in models.py.
#
# Think of it like this:
#
# models.py        -> Blueprint of the database
# database.py      -> Connection to PostgreSQL
# create_tables.py -> Builder that constructs the tables
# ------------------------------------------------------------

# Import the database engine (connection to PostgreSQL)
from backend.db.database import engine

# Import Base, which contains metadata about all our models
from backend.db.models import Base

print("Creating tables...")

# ------------------------------------------------------------
# Step 2: Create all tables
# ------------------------------------------------------------
# Base.metadata contains information about every model
# that inherits from Base.
#
# Example:
#   Family
#   User
#   Patient
#   Doctor
#   Medicine
#
# create_all() looks through all of those models,
# generates the corresponding SQL CREATE TABLE commands,
# and executes them on the database.

# bind=engine tells SQLAlchemy WHICH database to use.
# NOTE:
# - If a table doesn't exist, it will be created.
# - If a table already exists, SQLAlchemy leaves it unchanged.
# - It does NOT delete existing data.
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")