"""
risk_analysis.py
-----------------
Combines a patient's stored predictions across all diseases into an
overall composite risk score and displays recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from database import get_patients, get_predictions_for_patient
from utils import badge, risk_color


RISK_WEIGHTS = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}

RECOMMENDATIONS = {
    "diabetes": "Recommend HbA1c testing, dietary consultation, and regular glucose monitoring.",
    "heart": "Recommend cardiology referral, lipid profile, and ECG/stress test follow-up.",
    "kidney": "Recommend nephrology referral, renal function panel, and blood pressure management.",
}


def show_risk_analysis_page():
    st.title("⚠️ Patient Risk Analysis")

    patients_df = get_patients(st.session_state.username)
    if patients_df.empty:
        st.info("No patients available yet.")
        return

    selected_name = st.selectbox("Select Patient", patients_df["name"].tolist())
    patient = patients_df[patients_df["name"] == selected_name].iloc[0]
    patient_id = int(patient["id"])

    preds = get_predictions_for_patient(patient_id)

    st.markdown(f"### Profile: {patient['name']} ({patient['age']} yrs, {patient['gender']})")

    if preds.empty:
        st.warning("No predictions on record for this patient yet. Run predictions from the Disease Prediction page first.")
        return

    # Take latest prediction per disease
    latest = preds.sort_values("created_at").groupby("disease").tail(1)

    col1, col2, col3 = st.columns(3)
    overall_score = 0
    max_score = 0
    for i, (_, row) in enumerate(latest.iterrows()):
        col = [col1, col2, col3][i % 3]
        color = risk_color(row["risk_level"])
        with col:
            st.markdown(
                f"""<div style="background:white;border-radius:12px;padding:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                <b>{row['disease'].title()}</b><br>
                Result: {row['result']}<br>
                Probability: {row['probability']*100:.1f}%<br>
                {badge(row['risk_level'], color)}
                </div>""",
                unsafe_allow_html=True
            )
        overall_score += RISK_WEIGHTS.get(row["risk_level"], 0)
        max_score += 4

    st.divider()

    overall_pct = (overall_score / max_score * 100) if max_score else 0
    st.subheader("Composite Risk Score")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_pct,
        title={"text": "Overall Risk (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#34495e"},
            "steps": [
                {"range": [0, 30], "color": "#2ecc71"},
                {"range": [30, 60], "color": "#f1c40f"},
                {"range": [60, 80], "color": "#e67e22"},
                {"range": [80, 100], "color": "#e74c3c"},
            ],
        }
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Clinical Recommendations")
    for _, row in latest.iterrows():
        if row["risk_level"] in ("High", "Critical"):
            st.warning(f"**{row['disease'].title()}** — {RECOMMENDATIONS.get(row['disease'], 'Consult a specialist.')}")
        elif row["risk_level"] == "Moderate":
            st.info(f"**{row['disease'].title()}** — Monitor regularly and reassess in 3–6 months.")
        else:
            st.success(f"**{row['disease'].title()}** — No immediate concerns; maintain healthy lifestyle.")

    st.subheader("Full Prediction History")
    st.dataframe(
        preds[["disease", "result", "probability", "risk_level", "created_at"]],
        use_container_width=True
    )
