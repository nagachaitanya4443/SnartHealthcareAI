"""
patient.py
----------
Patient management: add new patients, browse patient list, view a
patient's profile with prediction history.
"""

import streamlit as st
import pandas as pd
from database import add_patient, get_patients, delete_patient, get_predictions_for_patient
from utils import badge, risk_color


def show_patient_page():
    st.title("👥 Patient Management")

    tab_list, tab_add = st.tabs(["📋 Patient List", "➕ Add New Patient"])

    # ---------------- ADD PATIENT ----------------
    with tab_add:
        with st.form("add_patient_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *")
                age = st.number_input("Age", min_value=0, max_value=120, value=30)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            with col2:
                phone = st.text_input("Phone Number")
                address = st.text_area("Address", height=100)

            submitted = st.form_submit_button("Add Patient", use_container_width=True)

        if submitted:
            if not name:
                st.error("Patient name is required.")
            else:
                pid = add_patient(st.session_state.username, name, age, gender, phone, address)
                st.success(f"Patient '{name}' added successfully (ID: {pid}).")
                st.rerun()

    # ---------------- PATIENT LIST ----------------
    with tab_list:
        df = get_patients(st.session_state.username)

        if df.empty:
            st.info("No patients yet. Add one from the 'Add New Patient' tab.")
            return

        search = st.text_input("🔍 Search by name")
        if search:
            df = df[df["name"].str.contains(search, case=False, na=False)]

        st.write(f"**{len(df)} patient(s) found**")

        for _, row in df.iterrows():
            with st.expander(f"🧑 {row['name']}  |  Age: {row['age']}  |  {row['gender']}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**Phone:** {row['phone'] or '—'}")
                    st.write(f"**Address:** {row['address'] or '—'}")
                with col2:
                    st.write(f"**Registered:** {row['created_at'][:10]}")
                    st.write(f"**Patient ID:** {row['id']}")
                with col3:
                    if st.button("View Profile", key=f"view_{row['id']}"):
                        st.session_state.selected_patient_id = int(row["id"])
                        st.session_state.page = "Disease Prediction"
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                        delete_patient(int(row["id"]))
                        st.warning(f"Deleted patient '{row['name']}'.")
                        st.rerun()

                # Prediction history preview
                preds = get_predictions_for_patient(int(row["id"]))
                if not preds.empty:
                    st.markdown("**Recent Predictions:**")
                    for _, p in preds.head(3).iterrows():
                        color = risk_color(p["risk_level"])
                        st.markdown(
                            f"- {p['disease'].title()}: {p['result']} "
                            f"{badge(p['risk_level'], color)} "
                            f"<span style='color:gray;font-size:0.8rem;'>({p['created_at'][:16]})</span>",
                            unsafe_allow_html=True
                        )
