"""
dashboard.py
------------
Main landing dashboard shown after login: summary metrics, recent
activity, and quick links.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_patients, get_all_predictions
from utils import badge, risk_color


def show_dashboard_page():
    st.title(f"👋 Welcome, {st.session_state.full_name}")
    st.caption("Here's a snapshot of your patient population and recent activity.")

    patients_df = get_patients(st.session_state.username)
    preds_df = get_all_predictions(st.session_state.username)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(_metric_card("👥 Total Patients", len(patients_df)), unsafe_allow_html=True)
    col2.markdown(_metric_card("🧬 Total Predictions", len(preds_df)), unsafe_allow_html=True)

    high_risk_count = int(preds_df["risk_level"].isin(["High", "Critical"]).sum()) if not preds_df.empty else 0
    col3.markdown(_metric_card("⚠️ High/Critical Risk Cases", high_risk_count), unsafe_allow_html=True)

    latest_date = preds_df["created_at"].max()[:10] if not preds_df.empty else "—"
    col4.markdown(_metric_card("🕒 Last Prediction", latest_date), unsafe_allow_html=True)

    st.divider()

    if preds_df.empty:
        st.info("No prediction activity yet. Add patients and run predictions to populate the dashboard.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Predictions by Disease")
        counts = preds_df["disease"].value_counts().reset_index()
        counts.columns = ["Disease", "Count"]
        fig = px.bar(counts, x="Disease", y="Count", color="Disease", text="Count")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk Level Overview")
        risk_counts = preds_df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Count"]
        color_map = {"Low": "#2ecc71", "Moderate": "#f1c40f", "High": "#e67e22", "Critical": "#e74c3c"}
        fig = px.pie(risk_counts, names="Risk Level", values="Count",
                     color="Risk Level", color_discrete_map=color_map, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Activity")
    recent = preds_df.sort_values("created_at", ascending=False).head(8)
    for _, row in recent.iterrows():
        color = risk_color(row["risk_level"])
        st.markdown(
            f"**{row['patient_name']}** — {row['disease'].title()}: {row['result']} "
            f"{badge(row['risk_level'], color)} "
            f"<span style='color:gray;font-size:0.8rem;'> · {row['created_at'][:16]}</span>",
            unsafe_allow_html=True
        )


def _metric_card(label, value):
    return f"""
    <div class="metric-card">
        <div style="font-size:0.85rem;color:gray;">{label}</div>
        <div style="font-size:1.8rem;font-weight:700;">{value}</div>
    </div>
    """
