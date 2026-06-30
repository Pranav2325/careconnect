# database.py
# This file is responsible for connecting our application to the PostgreSQL database
# and creating database sessions (conversations) for each request.

# create_engine -> Creates the main database engine (connection manager)
from sqlalchemy import create_engine

# sessionmaker -> Creates new database sessions whenever we need one
from sqlalchemy.orm import sessionmaker

# load_dotenv -> Loads variables from the .env file
from dotenv import load_dotenv

import os

# ---------------------------------------------------------
# Step 1: Load environment variables from the .env file
# ---------------------------------------------------------
# Example:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/mydatabase
load_dotenv()

# ---------------------------------------------------------
# Step 2: Read the DATABASE_URL from environment variables
# ---------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# ---------------------------------------------------------
# Step 3: Create the SQLAlchemy Engine
# ---------------------------------------------------------
# Think of the Engine as the "main gateway" to the database.
#
# It knows:
# - Database address
# - Username
# - Password
# - Which database to connect to
#
# NOTE:
# This does NOT immediately connect to PostgreSQL.
# It simply prepares everything needed for future connections.
engine = create_engine(DATABASE_URL)

# ---------------------------------------------------------
# Step 4: Create a Session Factory
# ---------------------------------------------------------
# SessionLocal is NOT a database session.
#
# Instead, it's a "factory" that creates new sessions whenever
# we call SessionLocal().
#
# Every API request gets its own session.
SessionLocal = sessionmaker(
    autocommit=False,   # Changes are NOT automatically saved.
                         # We must explicitly call db.commit().

    autoflush=False,    # SQLAlchemy won't automatically send pending
                         # changes to the database before queries.

    bind=engine         # Connect every session to our Engine.
)

# ---------------------------------------------------------
# Step 5: Dependency function used by FastAPI
# ---------------------------------------------------------
def get_db():
    """
    Creates a new database session.

    Flow:
        Create Session
              ↓
        Give it to the API route
              ↓
        API performs queries
              ↓
        Close the session automatically

    Using this pattern prevents connection leaks.
    """

    # Create a brand-new database session.
    # Think of this as opening a new conversation with PostgreSQL.
    db = SessionLocal()

    try:
        # Give this session to the API route.
        # FastAPI will pause here while the route uses the session.
        yield db

    finally:
        # This always runs, even if an error occurs.
        #
        # Closing the session returns the connection back to SQLAlchemy's
        # connection pool so it can be reused by future requests.
        db.close()