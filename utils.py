"""
utils.py
--------
Shared helper functions: password hashing, session-state helpers,
custom CSS injection, and small formatting utilities.
"""

import hashlib
import streamlit as st


def hash_password(password: str) -> str:
    """Return a SHA-256 hash of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def init_session_state():
    """Ensure all keys used across pages exist in st.session_state."""
    defaults = {
        "logged_in": False,
        "username": None,
        "full_name": None,
        "role": None,
        "page": "Dashboard",
        "selected_patient_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout():
    for key in ["logged_in", "username", "full_name", "role", "selected_patient_id"]:
        st.session_state[key] = False if key == "logged_in" else None


def risk_level_from_probability(prob: float) -> str:
    """Bucket a model probability (0-1) into a human-readable risk level."""
    if prob < 0.3:
        return "Low"
    elif prob < 0.6:
        return "Moderate"
    elif prob < 0.8:
        return "High"
    return "Critical"


def risk_color(level: str) -> str:
    return {
        "Low": "#2ecc71",
        "Moderate": "#f1c40f",
        "High": "#e67e22",
        "Critical": "#e74c3c",
    }.get(level, "#95a5a6")


def inject_custom_css():
    st.markdown("""
        <style>
        .main { background-color: #f7f9fc; }
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-align: center;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
        .risk-badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
        }
        </style>
    """, unsafe_allow_html=True)


def badge(text: str, color: str) -> str:
    return f'<span class="risk-badge" style="background-color:{color}">{text}</span>'
