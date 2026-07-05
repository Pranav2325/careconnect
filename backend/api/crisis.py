# backend/api/crisis.py
# API route for crisis/emergency support

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.db.database import get_db
from backend.db.models import Patient
from backend.agents.crisis_agent import crisis_agent

router = APIRouter(
    prefix="/crisis",
    tags=["Crisis Support"]
)

# ── Pydantic Schemas ──────────────────────────────────────────────

class CrisisInput(BaseModel):
    """
    What comes in during a crisis.
    symptoms = plain language description of what's happening
    patient_id = whose profile to pull
    """
    symptoms: str
    patient_id: int


# ── Routes ───────────────────────────────────────────────────────

@router.post("/analyze")
def analyze_crisis(crisis_input: CrisisInput, db: Session = Depends(get_db)):
    """
    Analyze a crisis situation and return immediate action steps.

    This is the most critical endpoint in the entire app.
    It pulls the patient's full profile, searches their documents,
    and returns structured guidance + an emergency card.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(
        Patient.id == crisis_input.patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        result = crisis_agent.analyze_crisis(
            symptoms=crisis_input.symptoms,
            patient_id=crisis_input.patient_id,
            db=db
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Crisis agent error: {str(e)}"
        )