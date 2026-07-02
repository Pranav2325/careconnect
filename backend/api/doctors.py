
# backend/api/doctors.py
# API routes for managing patient doctors

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.db.database import get_db
from backend.db.models import Doctor, Patient

# All routes in this file will start with /doctors
router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)

# ── Pydantic Schemas ──────────────────────────────────────────────

# Request body for creating a new doctor
class DoctorCreate(BaseModel):
    """Data required to add a new doctor"""
    patient_id: int
    name: str
    specialization: Optional[str] = None
    phone: Optional[str] = None
    hospital: Optional[str] = None

# Response returned after creating or fetching a doctor
class DoctorResponse(BaseModel):
    """Data we send back after creating/fetching a doctor"""
    id: int
    patient_id: int
    name: str
    specialization: Optional[str]
    phone: Optional[str]
    hospital: Optional[str]

    class Config:
        # Allows Pydantic to read SQLAlchemy model objects
        from_attributes = True


# ── Routes ───────────────────────────────────────────────────────

# Create a new doctor
@router.post("/", response_model=DoctorResponse)
def add_doctor(doctor_data: DoctorCreate, db: Session = Depends(get_db)):
    """
    Add a new doctor for a patient.
    """
    # Check if the patient exists
    patient = db.query(Patient).filter(Patient.id == doctor_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Create a Doctor object
    doctor = Doctor(
        patient_id=doctor_data.patient_id,
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        phone=doctor_data.phone,
        hospital=doctor_data.hospital
    )

    # Add it to the database session
    db.add(doctor)

    # Save changes to the database
    db.commit()

    # Refresh object to get updated values (like generated id)
    db.refresh(doctor)

    # Return the created doctor
    return doctor


# Get all doctors for a patient
@router.get("/patient/{patient_id}", response_model=list[DoctorResponse])
def get_patient_doctors(patient_id: int, db: Session = Depends(get_db)):
    """
    Get all doctors for a specific patient.
    """
    # Check if the patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Fetch all doctors linked to the patient
    doctors = db.query(Doctor).filter(Doctor.patient_id == patient_id).all()

    # Return the list of doctors
    return doctors


# Get one doctor using its id
@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """
    Get a specific doctor by ID.
    """
    # Find the doctor
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    # Return error if doctor doesn't exist
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Return the doctor details
    return doctor

