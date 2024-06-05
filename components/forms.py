import streamlit as st
from utils.app_utils import is_valid_password, load_user_profile_information


def login_form():
    with st.form("Student login"):
        username = st.text_input("Enter Username:", max_chars=20).lower()
        password = st.text_input("Enter Password:", type="password", max_chars=16)
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if is_valid_password(username, password):
                load_user_profile_information(username)
                st.session_state.login = True
                st.rerun()  # to move on to acknowledgement form

            else:
                st.error("Username and Password is incorrect")
