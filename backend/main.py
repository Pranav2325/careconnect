# This is the main file of the backend.
# When we run the server, execution starts from here.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import app settings (app name, version, etc.)
from backend.core.config import settings
# Import database connection
from backend.db.database import engine
# Import all database models
from backend.db.models import Base
from backend.api import patients, medicines, doctors, documents, chat

# Create all tables in the database if they don't already exist
Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered remote health management agent for Indian families"
)

# Allow the frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,

    # Allow requests from any frontend
    # (Use your frontend URL instead of "*" in production)
    allow_origins=["*"],

    # Allow cookies and authentication headers
    allow_credentials=True,

    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],

    # Allow all request headers
    allow_headers=["*"],
)

#Register router
app.include_router(patients.router)
app.include_router(medicines.router)
app.include_router(doctors.router)
app.include_router(documents.router)
app.include_router(chat.router)

# Home route
# Open http://localhost:8000/
@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


# Health check route
# Open http://localhost:8000/health
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }