# backend/api/vitals.py
# API routes for logging and retrieving patient vitals

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.db.database import get_db
from backend.db.models import Vital, Patient

router = APIRouter(
    prefix="/vitals",
    tags=["Vitals"]
)

# ── Pydantic Schemas ──────────────────────────────────────────────

class VitalCreate(BaseModel):
    """
    Data required to log a new vital reading.
    recorded_at is optional — defaults to now if not provided.
    Useful when family enters a reading that was taken earlier.
    """
    patient_id: int
    vital_type: str  # "blood_pressure", "blood_sugar", "heart_rate", "weight"
    value: str
    value_secondary: Optional[str] = None  # diastolic for BP
    unit: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None

class VitalResponse(BaseModel):
    id: int
    patient_id: int
    vital_type: str
    value: str
    value_secondary: Optional[str]
    unit: Optional[str]
    notes: Optional[str]
    recorded_at: datetime

    class Config:
        from_attributes = True


# ── Routes ───────────────────────────────────────────────────────

@router.post("/", response_model=VitalResponse)
def log_vital(vital_data: VitalCreate, db: Session = Depends(get_db)):
    """Log a new vital reading for a patient."""
    patient = db.query(Patient).filter(Patient.id == vital_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    vital = Vital(
        patient_id=vital_data.patient_id,
        vital_type=vital_data.vital_type,
        value=vital_data.value,
        value_secondary=vital_data.value_secondary,
        unit=vital_data.unit,
        notes=vital_data.notes,
        recorded_at=vital_data.recorded_at or datetime.utcnow()
    )
    db.add(vital)
    db.commit()
    db.refresh(vital)
    return vital


@router.get("/{patient_id}")
def get_vitals(patient_id: int, db: Session = Depends(get_db)):
    """Get all vitals for a patient, grouped by type."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    vitals = db.query(Vital).filter(
        Vital.patient_id == patient_id
    ).order_by(Vital.recorded_at.desc()).all()

    # Group by vital type for easier frontend display
    grouped = {}
    for vital in vitals:
        if vital.vital_type not in grouped:
            grouped[vital.vital_type] = []
        grouped[vital.vital_type].append({
            "id": vital.id,
            "value": vital.value,
            "value_secondary": vital.value_secondary,
            "unit": vital.unit,
            "notes": vital.notes,
            "recorded_at": vital.recorded_at.isoformat()
        })

    return grouped


@router.get("/{patient_id}/trends")
def get_trends(patient_id: int, db: Session = Depends(get_db)):
    """
    Analyze trends for each vital type.
    Compares last 7 readings to detect rising/falling/stable patterns.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    vital_types = ["blood_pressure", "blood_sugar", "heart_rate", "weight"]
    trends = {}

    for vtype in vital_types:
        # Get last 7 readings for this vital type
        readings = db.query(Vital).filter(
            Vital.patient_id == patient_id,
            Vital.vital_type == vtype
        ).order_by(Vital.recorded_at.desc()).limit(7).all()

        if len(readings) < 2:
            # Not enough data for trend
            trends[vtype] = {
                "trend": "insufficient_data",
                "message": "Need at least 2 readings for trend analysis",
                "readings_count": len(readings)
            }
            continue

        # Compare oldest vs newest in our window
        # readings[0] = most recent, readings[-1] = oldest
        try:
            latest_value = float(readings[0].value)
            oldest_value = float(readings[-1].value)
            change = latest_value - oldest_value
            change_percent = (change / oldest_value) * 100

            if change_percent > 5:
                trend = "rising"
                alert = True
            elif change_percent < -5:
                trend = "falling"
                alert = False  # falling can be good or bad depending on vital
            else:
                trend = "stable"
                alert = False

            trends[vtype] = {
                "trend": trend,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "latest_value": readings[0].value,
                "latest_unit": readings[0].unit,
                "oldest_value": readings[-1].value,
                "readings_count": len(readings),
                "alert": alert
            }

        except ValueError:
            # BP values like "130/85" can't be directly converted to float
            trends[vtype] = {
                "trend": "complex",
                "message": "Manual review recommended",
                "latest_value": readings[0].value,
                "readings_count": len(readings)
            }

    return trends

@router.delete("/{vital_id}")
def delete_vital(vital_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific vital reading by ID.
    Why by ID? Each reading is unique — deleting by ID is precise
    and won't accidentally delete other readings.
    """
    vital = db.query(Vital).filter(Vital.id == vital_id).first()
    if not vital:
        raise HTTPException(status_code=404, detail="Vital reading not found")

    db.delete(vital)
    db.commit()

    return {"message": f"Vital reading {vital_id} deleted successfully"}