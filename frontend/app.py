# Starting point of our Streamlit UI

import streamlit as st
import sys
import os

# Add parent folder to Python path so we can import backend/frontend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API functions to talk to backend
from frontend.api_client import get_all_patients, add_patient,get_patient,get_medicines,get_doctors,add_medicine,add_doctor,upload_document


# Set page configuration (title, icon, layout)
st.set_page_config(
    page_title="CareConnect",
    page_icon="../assets/logo.png",  # path to your icon image
    layout="wide"
)

# Store selected patient info in session state (memory that survives reruns)
if "selected_patient_id" not in st.session_state:
    st.session_state.selected_patient_id = None

if "selected_patient_name" not in st.session_state:
    st.session_state.selected_patient_name = None


# ---------------- SIDEBAR ----------------
with st.sidebar:
    col1, col2 = st.sidebar.columns([1, 4])

    with col1:
        st.image("../assets/logo.png", width=50)

    with col2:
        st.markdown("## CareConnect")

    # Small description text
    st.caption("AI-powered family health management")

    # Horizontal line separator
    st.divider()

    # Section heading
    st.subheader("Select Patient")

    # Get all patients from backend
    patients = get_all_patients()

    # If patients exist, show dropdown
    if patients:

        # Convert list into dictionary: name -> id
        patients_names = {p["name"]: p["id"] for p in patients}

        # Dropdown to select patient
        selected_name = st.selectbox(
            "Choose a patient",
            options=list(patients_names.keys())
        )

        # When user selects a patient
        if selected_name:

            # Save selected patient ID in session memory
            st.session_state.selected_patient_id = patients_names[selected_name]

            # Save selected patient name in session memory
            st.session_state.selected_patient_name = selected_name

            # Show success message
            st.success(f"Viewing: {selected_name}")

    else:
        # If no patients found
        st.warning("No patients found. Add one below")
    st.divider()
    
    with st.expander("+ Add New Patient"):
        with st.form("add_patient_form"):
            p_name = st.text_input("Full Name")
            p_age = st.number_input("Age", min_value=1, max_value=120, value=65)
            p_blood = st.selectbox("Blood Group",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            p_conditions = st.text_area("Known Conditions",
                placeholder="e.g. Diabetes, High BP, Heart Condition")
            p_allergies = st.text_input("Allergies",
                placeholder="e.g. Penicillin")
            p_family = st.text_input("Family Name",
                placeholder="e.g. Sharma Family")
            submitted = st.form_submit_button("Add Patient")

            if submitted and p_name and p_family:
                result = add_patient(p_name, p_age, p_blood,
                                    p_conditions, p_allergies, p_family)
                if result:
                    st.success(f" {p_name} added!")
                    st.rerun()
                else:
                    st.error("Failed to add patient")
            


# ---------------- MAIN PAGE ----------------

if not st.session_state.selected_patient_id:
    st.title("Welcome to CareConnect")
    st.markdown("""
    ### AI-powered remote health management for Indian families

    **What you can do:**
    -  View and manage patient health profiles
    -  Track medicines and dosages
    -  Manage doctors and specialists
    -  Upload and search medical reports
    -  Ask health questions in plain language
    -  Get immediate crisis support

    **Get started:** Select a patient from the sidebar or add a new one.
    """)  
    st.stop()
    
#patient selected -show dashboard
patient_id=st.session_state.selected_patient_id 
patient_name=st.session_state.selected_patient_name

st.title(f"{patient_name}'s Health Dashboard")
# ── Tabs ──────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " Profile",
    " Add Data",
    " Documents",
    " Chat",
    " Crisis Support"
])

with tab1:
    st.subheader("Patient Profile")

    patient = get_patient(patient_id)
    if patient:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Name", patient["name"])
            st.metric("Age", patient["age"])
            st.metric("Blood Group", patient["blood_group"])
        with col2:
            st.info(f"**Known Conditions:**\n{patient['conditions']}")
            st.warning(f"**Allergies:**\n{patient['allergies']}")

    st.divider()

    # Medicines
    st.subheader("Current Medicines")
    medicines = get_medicines(patient_id)
    if medicines:
        for med in medicines:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.write(f"**{med['name']}**")
            with col2:
                st.write(med['dosage'])
            with col3:
                st.write(med['timing'])
    else:
        st.info("No medicines added yet")

    st.divider()

    # Doctors
    st.subheader("Doctors")
    doctors = get_doctors(patient_id)
    if doctors:
        for doc in doctors:
            with st.expander(f"{doc['name']} — {doc['specialization']}"):
                st.write(f"{doc['hospital']}")
                st.write(f"{doc['phone']}")
    else:
        st.info("No doctors added yet")
    
  
     


with tab2:
    col1,col2=st.columns(2);
    with col1:
        st.subheader("Add Medicine")
        with st.form("add_medicine_form"):
            med_name = st.text_input("Medicine Name",
                placeholder="e.g. Metformin")
            med_dosage = st.text_input("Dosage",
                placeholder="e.g. 500mg")
            med_timing = st.text_input("Timing",
                placeholder="e.g. Morning and Night after food")
            med_submitted=st.form_submit_button("Add Medicine")
            
            if med_submitted and med_name:
                result=add_medicine(patient_id,med_name,med_dosage,med_timing)
                if result:
                    st.success(f"{med_name} added!")
                else:
                    st.error("Failed to add medicine")
    with col2:
        st.subheader("Add Doctor")
        with st.form("add_doctor_form"):
            doc_name = st.text_input("Doctor Name",
                placeholder="e.g. Dr. Anil Sharma")
            doc_spec = st.text_input("Specialization",
                placeholder="e.g. Cardiologist")
            doc_phone = st.text_input("Phone",
                placeholder="e.g. 9876543210")
            doc_hospital = st.text_input("Hospital",
                placeholder="e.g. Apollo Hospital Nagpur")
            doc_submitted = st.form_submit_button("Add Doctor")

            if doc_submitted and doc_name:
                result = add_doctor(patient_id, doc_name,
                                   doc_spec, doc_phone, doc_hospital)
                if result:
                    st.success(f"{doc_name} added!")
                else:
                    st.error("Failed to add doctor")                   
                       

with tab3:
    st.subheader("Upload Medical Documents")
    st.caption("Upload prescriptions, blood tests, ECGs, Scan reports- any PDF")
    
    uploaded_file=st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )
    if uploaded_file:
        st.info(f"Selected: **{uploaded_file.name}** ({uploaded_file.size} bytes)")
        
        if st.button("Upload and Process"):
            with st.spinner("Extracting text and storing in AI memory..."):
                result=upload_document(
                    patient_id,
                    uploaded_file.read(),
                    uploaded_file.name
                )
            if result:
                st.success(f"""
                 Document processed successfully!
                - **File:** {result['details']['filename']}
                - **Text extracted:** {result['details']['characters_extracted']} characters
                - **Chunks stored:** {result['details']['chunks_stored']}
                """)
                st.info("💡 You can now ask questions about this document in the Chat tab")
            else:
                st.error("Failed to upload document")

with tab4:
    st.subheader("Chat Tab — Coming Soon")

with tab5:
    st.subheader("Crisis Tab — Coming Soon")