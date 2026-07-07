# frontend/api_client.py
# Helper functions for calling our FastAPI backend

import requests

# Base URL of the FastAPI backend
BASE_URL = "http://127.0.0.1:8000"


def get_patient(patient_id: int) -> dict:
    """Get a patient's profile by ID"""

    # Send a GET request to the backend
    response = requests.get(f"{BASE_URL}/patients/{patient_id}")

    # If request is successful, return the patient data
    if response.status_code == 200:
        return response.json()

    # Return None if something went wrong
    return None


def get_all_patients() -> list:
    """Get all patients"""

    # Send a GET request to fetch all patients
    response = requests.get(f"{BASE_URL}/patients/")

    # Return the list if successful
    if response.status_code == 200:
        return response.json()

    # Return an empty list if request fails
    return []


def add_patient(name: str, age: int, blood_group: str,
                conditions: str, allergies: str, family_name: str) -> dict:
    """Create a new patient profile"""

    # Send patient details to the backend
    response = requests.post(f"{BASE_URL}/patients/", json={
        "name": name,
        "age": age,
        "blood_group": blood_group,
        "conditions": conditions,
        "allergies": allergies,
        "family_name": family_name
    })

    # Return the created patient
    if response.status_code == 200:
        return response.json()

    # Return None if request fails
    return None


def get_medicines(patient_id: int) -> list:
    """Get all medicines for a patient"""

    # Request medicines for the given patient
    response = requests.get(f"{BASE_URL}/medicines/patient/{patient_id}")

    # Return medicine list if successful
    if response.status_code == 200:
        return response.json()

    # Return empty list if request fails
    return []


def add_medicine(patient_id: int, name: str, dosage: str, timing: str) -> dict:
    """Add a medicine for a patient"""

    # Send medicine details to the backend
    response = requests.post(f"{BASE_URL}/medicines/", json={
        "patient_id": patient_id,
        "name": name,
        "dosage": dosage,
        "timing": timing
    })

    # Return added medicine
    if response.status_code == 200:
        return response.json()

    # Return None if request fails
    return None


def get_doctors(patient_id: int) -> list:
    """Get all doctors for a patient"""

    # Request doctors linked to the patient
    response = requests.get(f"{BASE_URL}/doctors/patient/{patient_id}")

    # Return doctor list if successful
    if response.status_code == 200:
        return response.json()

    # Return empty list if request fails
    return []


def add_doctor(patient_id: int, name: str, specialization: str,
               phone: str, hospital: str) -> dict:
    """Add a doctor for a patient"""

    # Send doctor details to the backend
    response = requests.post(f"{BASE_URL}/doctors/", json={
        "patient_id": patient_id,
        "name": name,
        "specialization": specialization,
        "phone": phone,
        "hospital": hospital
    })

    # Return added doctor
    if response.status_code == 200:
        return response.json()

    # Return None if request fails
    return None


def upload_document(patient_id: int, file_bytes: bytes, filename: str) -> dict:
    """Upload a PDF document for a patient"""

    # Upload the PDF file
    response = requests.post(
        f"{BASE_URL}/documents/upload/{patient_id}",
        files={
            "file": (filename, file_bytes, "application/pdf")
        }
    )

    # Return upload result
    if response.status_code == 200:
        return response.json()

    # Return None if upload fails
    return None


def ask_question(patient_id: int, question: str) -> dict:
    """Ask a health question about a patient"""

    # Send the patient's question
    response = requests.post(f"{BASE_URL}/chat/ask", json={
        "patient_id": patient_id,
        "question": question
    })

    # Return AI response
    if response.status_code == 200:
        return response.json()

    # Return None if request fails
    return None


def analyze_crisis(patient_id: int, symptoms: str) -> dict:
    """Analyze a crisis situation"""

    # Send symptoms to the backend
    response = requests.post(f"{BASE_URL}/crisis/analyze", json={
        "patient_id": patient_id,
        "symptoms": symptoms
    })

    # Return analysis result
    if response.status_code == 200:
        return response.json()

    # Return None if request fails
    return None

def get_chat_history(patient_id: int) -> list:
    """Get chat history for a patient from database"""
    response = requests.get(f"{BASE_URL}/chat/history/{patient_id}")
    if response.status_code == 200:
        return response.json()
    return []


def clear_chat_history(patient_id: int) -> bool:
    """Clear chat history for a patient"""
    response = requests.delete(f"{BASE_URL}/chat/history/{patient_id}")
    return response.status_code == 200