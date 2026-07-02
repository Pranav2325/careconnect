# backend/api/documents.py
# API routes for uploading and searching medical documents

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.db.database import get_db
from backend.db.models import Patient
from backend.services.document_service import document_service

# Create router for all document-related endpoints
router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# ── Request Schema ───────────────────────────────────────────────

class SearchQuery(BaseModel):
    """
    Request body for document search.

    query: natural language question from user
    n_results: how many relevant chunks to return
    """
    query: str
    n_results: int = 3


# ── UPLOAD DOCUMENT ──────────────────────────────────────────────

@router.post("/upload/{patient_id}")
async def upload_document(
    patient_id: int,
    file: UploadFile = File(...),  # required uploaded file
    db: Session = Depends(get_db)
):
    """
    Upload and process a PDF document for a specific patient.

    Flow:
    PDF → extract text → split into chunks → store in ChromaDB
    """

    # Step 1: Check if patient exists in relational DB
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Step 2: Only allow PDF files (current system supports PDF parsing only)
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # Step 3: Read uploaded file into memory as bytes
    file_bytes = await file.read()

    # Step 4: Send file to document service (AI pipeline)
    result = document_service.add_document(
        patient_id=patient_id,
        file_bytes=file_bytes,
        filename=file.filename
    )

    # Step 5: Handle extraction failure (empty or unreadable PDF)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Step 6: Return success response with processing details
    return {
        "message": "Document uploaded and processed successfully",
        "patient_id": patient_id,
        "details": result
    }


# ── SEARCH DOCUMENTS ─────────────────────────────────────────────

@router.post("/search/{patient_id}")
def search_documents(
    patient_id: int,
    search_query: SearchQuery,
    db: Session = Depends(get_db)
):
    """
    Search medical documents of a specific patient using semantic search.

    Flow:
    user query → embedding → vector search → top matching chunks
    """

    # Step 1: Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Step 2: Perform semantic search using ChromaDB
    results = document_service.search_documents(
        patient_id=patient_id,
        query=search_query.query,
        n_results=search_query.n_results
    )

    # Step 3: If no matching documents found
    if not results:
        return {
            "message": "No documents found for this patient",
            "results": []
        }

    # Step 4: Return ranked search results
    return {
        "query": search_query.query,
        "results": results
    }