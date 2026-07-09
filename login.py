"""
login.py
--------
Renders the login / sign-up screen and handles authentication.
"""

import streamlit as st
from database import create_user, get_user
from utils import hash_password, verify_password


def show_login_page():
    st.markdown(
        "<h1 style='text-align:center;'>🏥 Smart Healthcare Analytics</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;color:gray;'>AI-powered disease prediction & patient risk analytics</p>",
        unsafe_allow_html=True
    )
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔑 Login", "🆕 Sign Up"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user = get_user(username)
                    if user and verify_password(password, user["password_hash"]):
                        st.session_state.logged_in = True
                        st.session_state.username = user["username"]
                        st.session_state.full_name = user["full_name"]
                        st.session_state.role = user["role"]
                        st.success(f"Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_signup:
            with st.form("signup_form"):
                full_name = st.text_input("Full Name")
                new_username = st.text_input("Choose a Username")
                role = st.selectbox("Role", ["doctor", "nurse", "administrator", "analyst"])
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                signup_submitted = st.form_submit_button("Create Account", use_container_width=True)

            if signup_submitted:
                if not all([full_name, new_username, new_password, confirm_password]):
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, msg = create_user(new_username, hash_password(new_password), full_name, role)
                    if ok:
                        st.success(msg + " You can now log in from the Login tab.")
                    else:
                        st.error(msg)

    st.markdown(
        "<p style='text-align:center;color:gray;font-size:0.8rem;margin-top:2rem;'>"
        "Demo credentials: create a new account above, or use username <b>admin</b> / password <b>admin123</b> "
        "after first-run seeding.</p>",
        unsafe_allow_html=True
    )
