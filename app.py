"""
app.py
------
Main entry point for the Smart Healthcare Analytics Streamlit app.
Handles authentication gating, sidebar navigation, and page routing.

Run with:  streamlit run app.py
"""

import streamlit as st

from database import init_db, create_user, get_user
from utils import init_session_state, hash_password, inject_custom_css, logout

from login import show_login_page
from dashboard import show_dashboard_page
from patient import show_patient_page
from disease_prediction import show_prediction_page
from analytics import show_analytics_page
from risk_analysis import show_risk_analysis_page
from ai_assistant import show_ai_assistant_page
from report_generator import show_report_generator_page


st.set_page_config(
    page_title="Smart Healthcare Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


def seed_demo_admin():
    """Create a default admin account on first run for easy demoing."""
    if get_user("admin") is None:
        create_user("admin", hash_password("admin123"), "Administrator", "administrator")


def main():
    init_db()
    seed_demo_admin()
    init_session_state()
    inject_custom_css()

    if not st.session_state.logged_in:
        show_login_page()
        return

    # ---------------- Sidebar navigation ----------------
    with st.sidebar:
        st.markdown(f"### 🏥 Smart Healthcare AI")
        st.markdown(f"**{st.session_state.full_name}**  \n`{st.session_state.role}`")
        st.divider()

        pages = {
            "Dashboard": "📊",
            "Patient Management": "👥",
            "Disease Prediction": "🧬",
            "Risk Analysis": "⚠️",
            "Analytics": "📈",
            "AI Assistant": "🤖",
            "Report Generator": "📄",
        }

        for page_name, icon in pages.items():
            if st.button(f"{icon}  {page_name}", use_container_width=True,
                         type="primary" if st.session_state.page == page_name else "secondary"):
                st.session_state.page = page_name
                st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    # ---------------- Page routing ----------------
    page = st.session_state.page
    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Patient Management":
        show_patient_page()
    elif page == "Disease Prediction":
        show_prediction_page()
    elif page == "Risk Analysis":
        show_risk_analysis_page()
    elif page == "Analytics":
        show_analytics_page()
    elif page == "AI Assistant":
        show_ai_assistant_page()
    elif page == "Report Generator":
        show_report_generator_page()
    else:
        show_dashboard_page()


if __name__ == "__main__":
    main()
