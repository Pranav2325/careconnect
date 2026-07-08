# Starting point of our Streamlit UI

import streamlit as st
import sys
import os

# Add parent folder to Python path so we can import backend/frontend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API functions to talk to backend
from frontend.api_client import get_all_patients, add_patient,get_patient,get_medicines,get_doctors,add_medicine,add_doctor,upload_document,ask_question,analyze_crisis,get_chat_history,clear_chat_history,log_vital,get_trends,get_vitals,delete_vital


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
    
# Read active tab from URL params — survives refresh
if "tab" in st.query_params:
    st.session_state.active_tab = int(st.query_params["tab"])
else:
    st.session_state.active_tab = 0


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
page = st.radio(
    "Navigate",
    ["Profile", "Add Data","Vitals", "Documents", "Chat", "Crisis Support"],
    horizontal=True,
    label_visibility="collapsed",
    index=st.session_state.active_tab
)

tab_map = {
    "Profile": 0,
    "Add Data": 1,
    "Vitals": 2,
    "Documents": 3,
    "Chat": 4,
    "Crisis Support": 5
}
st.session_state.active_tab = tab_map.get(page, 0)
st.query_params["tab"] = str(st.session_state.active_tab)
st.divider()

# Show content based on selection
if page == "Profile":

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

elif page == "Add Data":

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
                    
elif page=="Vitals":
    st.subheader("Vitals Tracking")
    st.caption("Log and track daily health readings")  
    
    st.subheader("Log New Reading") 
    col1,col2=st.columns(2)
    with col1:
        vital_type = st.selectbox(
            "Vital Type",
            ["blood_pressure", "blood_sugar", "heart_rate", "weight"]
        )

        if vital_type == "blood_pressure":
            bp_sys = st.text_input("Systolic (top number)", placeholder="e.g. 130")
            bp_dia = st.text_input("Diastolic (bottom number)", placeholder="e.g. 85")
            unit = "mmHg"
        elif vital_type == "blood_sugar":
            value = st.text_input("Blood Sugar", placeholder="e.g. 142")
            unit = "mg/dL"
        elif vital_type == "heart_rate":
            value = st.text_input("Heart Rate", placeholder="e.g. 72")
            unit = "bpm"
        elif vital_type == "weight":
            value = st.text_input("Weight", placeholder="e.g. 70")
            unit = "kg"
    
    with col2:
        notes=st.text_input("Notes (optional)",placeholder="e.g. Fasting reading, after walking")
        
        if st.button("log Reading",type="primary"):
            if vital_type == "blood_pressure":
                if bp_sys and bp_dia:
                    result = log_vital(patient_id, vital_type,
                                      bp_sys, bp_dia, unit, notes)
                else:
                    st.warning("Please enter both systolic and diastolic values")
                    result = None
            else:
                if value:
                    result = log_vital(patient_id, vital_type,
                                      value, None, unit, notes)
                else:
                    st.warning("Please enter a value")
                    result = None

            if result:
                st.success("Reading logged successfully!")
                
    st.divider()
    
    trends=get_trends(patient_id)
    if trends:
        for vtype,trend_data in trends.items():
            with st.expander(f"{vtype.replace('_', ' ').title()}"):
                if trend_data["trend"] == "insufficient_data":
                    st.info(f"{trend_data['message']}")
                elif trend_data["trend"] == "complex":
                    st.info(f"Latest: {trend_data['latest_value']} — {trend_data['message']}")
                else:
                    # Show trend with color
                    if trend_data.get("alert"):
                        st.error(f"RISING — {trend_data['change_percent']}% increase detected")
                    elif trend_data["trend"] == "falling":
                        st.warning(f"Falling — {trend_data['change_percent']}% decrease")
                    else:
                        st.success(f"Stable — only {trend_data['change_percent']}% change")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Latest", f"{trend_data['latest_value']} {trend_data.get('latest_unit', '')}")
                    with col2:
                        st.metric("Oldest", f"{trend_data['oldest_value']}")
                    with col3:
                        st.metric("Readings", trend_data['readings_count']) 
    st.divider()
    
    st.subheader("Recent Readings")    
    vitals = get_vitals(patient_id)

    if vitals:
        for vtype, readings in vitals.items():
            st.write(f"**{vtype.replace('_', ' ').title()}**")
            for reading in readings[:5]:  # show last 5
                col1, col2, col3,col4 = st.columns([2, 2, 3,1])
                with col1:
                    if reading["value_secondary"]:
                        st.write(f"{reading['value']}/{reading['value_secondary']} {reading['unit']}")
                    else:
                        st.write(f"{reading['value']} {reading['unit']}")
                with col2:
                    st.write(reading["recorded_at"][:10])
                with col3:
                    st.write(reading["notes"] or "")
                with col4:
                    # Unique key per button using reading ID
                    if st.button("🗑️", key=f"del_vital_{reading['id']}",
                                help="Delete this reading"):
                        if delete_vital(reading["id"]):
                            st.success("Deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete")
            st.divider()
    else:
        st.info("No vitals logged yet")               
        
        

elif page == "Documents":

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

elif page == "Chat":
    st.subheader("Ask Health Questions")
    st.caption("Ask anything about the patient's health in plain language")

    # Load chat history from database on every load
    # This survives browser refresh because it's in PostgreSQL
    chat_history = get_chat_history(patient_id)

    # Clear button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Clear", help="Clear chat history"):
            clear_chat_history(patient_id)
            st.rerun()

    # Display chat history from database
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["sources"]:
                st.caption(f"Sources: {', '.join(message['sources'])}")

    # Chat input
    question = st.chat_input("Ask a health question...")

    if question:
        # Show user message immediately
        with st.chat_message("user"):
            st.write(question)

        # Get AI answer — this also saves to database automatically
        with st.chat_message("assistant"):
            with st.spinner("Searching medical records and thinking..."):
                result = ask_question(patient_id, question)

            if result:
                st.write(result["answer"])
                if result["sources"]:
                    st.caption(f"Sources: {', '.join(result['sources'])}")
            else:
                st.error("Failed to get answer")

elif page == "Crisis Support":
    st.subheader("Crisis Support")
    st.error("⚠️For life-threatening emergencies, call 108 or 112 immediately")
    st.caption("Describe what's happening and get immediate guidance")

    symptoms = st.text_area(
        "Describe the symptoms",
        placeholder="e.g. Dad has chest pain and is sweating heavily, feels dizzy and weak",
        height=100
    )

    if st.button("Analyze Crisis", type="primary"):
        if symptoms:
            with st.spinner("Analyzing emergency situation..."):
                result = analyze_crisis(patient_id, symptoms)

            if result:
                # Ambulance alert
                if result["call_ambulance"]:
                    st.error("CALL AMBULANCE IMMEDIATELY — Dial 108 or 112")
                else:
                    st.warning("Monitor situation closely and contact doctor")

                # Immediate steps
                st.subheader("Immediate Steps")
                for i, step in enumerate(result["immediate_steps"], 1):
                    st.write(f"**{i}.** {step}")

                # Possible causes
                st.subheader("Possible Causes")
                st.caption("(Not a diagnosis — consult a doctor)")
                for cause in result["possible_causes"]:
                    st.write(f"• {cause}")

                # Reassurance
                st.info(f"{result['reassurance']}")

                # Emergency card
                st.subheader("Emergency Card")
                st.caption("Show this to the ER doctor")
                st.code(result["emergency_card"])

                # What to tell doctor
                st.subheader("What to Tell the Doctor")
                st.write(result["what_to_tell_doctor"])
            else:
                st.error("Failed to analyze crisis")
        else:
            st.warning("Please describe the symptoms first")




