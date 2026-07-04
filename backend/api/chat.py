# backend/api/chat.py
# API route for asking health questions about a patient

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.db.database import get_db
from backend.db.models import Patient
from backend.services.ai_service import ai_service

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# ── Pydantic Schemas ──────────────────────────────────────────────

class ChatQuestion(BaseModel):
    """
    What comes in when family member asks a question.
    patient_id tells us whose profile and documents to search.
    """
    question: str
    patient_id: int


# ── Routes ───────────────────────────────────────────────────────

@router.post("/ask")
def ask_question(chat_input: ChatQuestion, db: Session = Depends(get_db)):
    """
    Ask a health question about a patient.
    Returns an AI-generated answer based on their
    actual profile and uploaded medical documents.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(
        Patient.id == chat_input.patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        result = ai_service.ask(
            question=chat_input.question,
            patient_id=chat_input.patient_id,
            db=db
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )