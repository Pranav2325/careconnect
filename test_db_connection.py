# test_db_connection.py
# This file checks if our Python app can successfully connect to PostgreSQL

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load variables from .env file into our program
load_dotenv()

# Get the database connection string we just set up
database_url = os.getenv("DATABASE_URL")
print(f"Trying to connect to: {database_url}")

try:
    # create_engine prepares the connection (doesn't connect yet)
    engine = create_engine(database_url)
    
    # This actually opens a connection and runs a simple test query
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✅ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
except Exception as e:
    print("❌ Connection failed!")
    print(f"Error: {e}")