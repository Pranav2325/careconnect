# backend/services/ai_service.py
# Connects Gemini AI with ChromaDB to answer health questions intelligently

from google import genai
from backend.core.config import settings
from backend.services.document_service import document_service
from backend.db.models import Patient, Medicine, Doctor
from sqlalchemy.orm import Session

# Create Gemini client with our API key
client = genai.Client(api_key=settings.GEMINI_API_KEY)


class AIService:
    def __init__(self):
        """
        Sets up Gemini model name.
        gemini-2.0-flash = latest fast model, free tier friendly.
        """
        self.model = "gemini-2.5-flash"

    def get_patient_context(self, patient_id: int, db: Session) -> str:
        """
        Fetches patient profile, medicines, and doctors from PostgreSQL
        and formats them as readable text for the prompt.
        """
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return "Patient not found"

        context = f"""
PATIENT PROFILE:
Name: {patient.name}
Age: {patient.age}
Blood Group: {patient.blood_group}
Known Conditions: {patient.conditions}
Known Allergies: {patient.allergies}
"""

        # Add medicines
        medicines = db.query(Medicine).filter(
            Medicine.patient_id == patient_id,
            Medicine.active == True
        ).all()

        if medicines:
            context += "\nCURRENT MEDICINES:\n"
            for med in medicines:
                context += f"- {med.name} {med.dosage} — {med.timing}\n"

        # Add doctors
        doctors = db.query(Doctor).filter(Doctor.patient_id == patient_id).all()
        if doctors:
            context += "\nDOCTORS:\n"
            for doc in doctors:
                context += f"- {doc.name} ({doc.specialization}) — {doc.hospital}\n"

        return context

    def build_prompt(self, question: str, patient_context: str, document_chunks: list) -> str:
        """
        Builds the complete prompt we send to Gemini.
        Rules first → profile → documents → question.
        """
        docs_text = ""
        if document_chunks:
            docs_text = "\nRELEVANT INFORMATION FROM MEDICAL DOCUMENTS:\n"
            for chunk in document_chunks:
                docs_text += f"(From {chunk['filename']}): {chunk['text']}\n\n"
        else:
            docs_text = "\nNo relevant documents found for this query.\n"

        prompt = f"""You are CareConnect, an AI health assistant helping families 
manage the health of their elderly relatives remotely.

CRITICAL RULES — NEVER BREAK THESE:
1. NEVER diagnose any medical condition
2. ALWAYS recommend consulting a doctor for medical decisions
3. Only provide information based on the patient's actual data provided below
4. If you don't know something, say so clearly
5. Be caring, clear, and concise in your responses

{patient_context}

{docs_text}

QUESTION FROM FAMILY MEMBER:
{question}

Please answer based only on the information provided above.
If the question requires medical judgment, provide the relevant facts 
and recommend consulting the appropriate doctor."""

        return prompt

    def ask(self, question: str, patient_id: int, db: Session) -> dict:
        """
        Main function — ties everything together.
        1. Get patient profile from PostgreSQL
        2. Search ChromaDB for relevant document chunks
        3. Build prompt with all context
        4. Send to Gemini
        5. Return answer with sources
        """
        # Step 1: Get patient profile
        patient_context = self.get_patient_context(patient_id, db)

        # Step 2: Search documents
        document_chunks = document_service.search_documents(
            patient_id=patient_id,
            query=question,
            n_results=3
        )

        # Step 3: Build prompt
        prompt = self.build_prompt(question, patient_context, document_chunks)

        # Step 4: Ask Gemini
        response = client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        # Step 5: Return answer with sources
        sources = list(set([chunk["filename"] for chunk in document_chunks]))

        return {
            "question": question,
            "answer": response.text,
            "sources": sources,
            "patient_id": patient_id
        }


# Single instance used across the entire app
ai_service = AIService()