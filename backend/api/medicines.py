# backend/api/medicines.py
# API routes for managing medicines

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.db.database import get_db
from backend.db.models import Medicine, Patient


# Create router for medicines API
router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"]
)

# Request schema (input)
class MedicineCreate(BaseModel):
    patient_id: int  # patient to whom medicine belongs
    doctor_id: Optional[int] = None
    name: str  # medicine name
    dosage: Optional[str] = None
    timing: Optional[str] = None


# Response schema (output)
class MedicineResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[int]
    name: str
    dosage: Optional[str]
    timing: Optional[str]
    active: bool  # shows if medicine is active or stopped

    class Config:
        from_attributes = True  # convert DB object to response

# Add medicine
@router.post("/", response_model=MedicineResponse)
def add_medicine(medicine_data: MedicineCreate, db: Session = Depends(get_db)):

    # check if patient exists
    patient = db.query(Patient).filter(Patient.id == medicine_data.patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # create medicine object
    medicine = Medicine(
        patient_id=medicine_data.patient_id,
        doctor_id=medicine_data.doctor_id,
        name=medicine_data.name,
        dosage=medicine_data.dosage,
        timing=medicine_data.timing
    )

    # save to database
    db.add(medicine)
    db.commit()
    db.refresh(medicine)

    return medicine



# Get all medicines of a patient
@router.get("/patient/{patient_id}", response_model=list[MedicineResponse])
def get_patient_medicines(patient_id: int, db: Session = Depends(get_db)):

    # check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # get all active medicines for this patient
    medicines = db.query(Medicine).filter(
        Medicine.patient_id == patient_id,
        Medicine.active == True
    ).all()

    return medicines



# Deactivate medicine (soft delete)
@router.patch("/{medicine_id}/deactivate")
def deactivate_medicine(medicine_id: int, db: Session = Depends(get_db)):

    # find medicine by id
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()

    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # mark medicine as inactive instead of deleting
    medicine.active = False

    # save changes
    db.commit()

    return {"message": "Medicine deactivated successfully"}