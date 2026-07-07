# backend/api/chat.py
# API route for asking health questions about a patient

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.db.database import get_db
from backend.db.models import Patient,ChatMessage
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
    
class ChatMessageResponse(BaseModel):
    id: int
    patient_id: int
    role: str
    content: str
    sources: Optional[str]

    class Config:
        from_attributes = True


# ── Routes ───────────────────────────────────────────────────────

@router.post("/ask")
def ask_question(chat_input: ChatQuestion, db: Session = Depends(get_db)):
    """
    Ask a health question.
    Saves both question and answer to database for persistence.
    """
    patient = db.query(Patient).filter(
        Patient.id == chat_input.patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        # Get AI answer
        result = ai_service.ask(
            question=chat_input.question,
            patient_id=chat_input.patient_id,
            db=db
        )

        # Save user message to database
        user_msg = ChatMessage(
            patient_id=chat_input.patient_id,
            role="user",
            content=chat_input.question,
            sources=None
        )
        db.add(user_msg)

        # Save assistant message to database
        assistant_msg = ChatMessage(
            patient_id=chat_input.patient_id,
            role="assistant",
            content=result["answer"],
            sources=",".join(result["sources"]) if result["sources"] else None
        )
        db.add(assistant_msg)
        db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )
        
@router.get("/history/{patient_id}")
def get_chat_history(patient_id: int, db: Session = Depends(get_db)):
    """
    Get full chat history for a patient from database.
    Called when the chat tab loads — restores previous conversations.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.patient_id == patient_id
    ).order_by(ChatMessage.created_at).all()

    return [
        {
            "role": msg.role,
            "content": msg.content,
            "sources": msg.sources.split(",") if msg.sources else []
        }
        for msg in messages
    ]
@router.delete("/history/{patient_id}")
def clear_chat_history(patient_id: int, db: Session = Depends(get_db)):
    """
    Clear chat history for a patient.
    Called when user clicks Clear button in UI.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.query(ChatMessage).filter(
        ChatMessage.patient_id == patient_id
    ).delete()
    db.commit()

    return {"message": "Chat history cleared"}