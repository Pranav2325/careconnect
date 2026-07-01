# backend/api/patients.py
# Handles all API requests related to patients

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

# Database session
from backend.db.database import get_db
# Database tables (models)
from backend.db.models import Patient, Family
# Create a router for all patient-related routes
# Every route in this file will start with /patients
router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

# Request Schema
# Defines what data the user must send while creating a patient
class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    blood_group: Optional[str] = None
    conditions: Optional[str] = None
    allergies: Optional[str] = None

    # Family name is required
    family_name: str

# Response Schema
# Defines what data we send back to the user
class PatientResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]
    blood_group: Optional[str]
    conditions: Optional[str]
    allergies: Optional[str]
    family_id: int

    class Config:
        # Allows FastAPI to convert SQLAlchemy objects into this schema
        from_attributes = True

# Create Patient
@router.post("/", response_model=PatientResponse)
def create_patient(
    patient_data: PatientCreate,          # Data sent by the user
    db: Session = Depends(get_db)         # Database session
):
    # Check if the family already exists
    family = (
        db.query(Family)
        .filter(Family.name == patient_data.family_name)
        .first()
    )

    # If family doesn't exist, create it
    if not family:
        family = Family(name=patient_data.family_name)

        db.add(family)      # Add to database
        db.commit()         # Save changes
        db.refresh(family)  # Get generated values like family.id

    # Create a new patient object
    patient = Patient(
        family_id=family.id,
        name=patient_data.name,
        age=patient_data.age,
        blood_group=patient_data.blood_group,
        conditions=patient_data.conditions,
        allergies=patient_data.allergies
    )

    # Save patient in database
    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Return the created patient
    return patient

# Get One Patient
@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    # Find patient using the given ID
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    # If patient doesn't exist, return 404 error
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Return patient details
    return patient



# Get All Patients
@router.get("/", response_model=list[PatientResponse])
def get_all_patients(
    db: Session = Depends(get_db)
):
    # Fetch every patient from the database
    patients = db.query(Patient).all()

    # Return the list of patients
    return patients