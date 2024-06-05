import streamlit as st
from utils.app_utils import is_valid_password, load_user_profile_information,check_update_dates
from database.sqlite3 import get_last_prompt_changes


def login_form():
    with st.form("Student login"):
        username = st.text_input("Enter Username:", max_chars=20).lower()
        password = st.text_input("Enter Password:", type="password", max_chars=16)
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if is_valid_password(username, password):
                load_user_profile_information(username)
                safa_prompt_date_change, acp_prompt_date_change, app_prompt_date_change = get_last_prompt_changes()
                st.session_state.log_msg = check_update_dates(safa_prompt_date_change, acp_prompt_date_change, app_prompt_date_change)

                st.session_state.login = True
                st.rerun()  # to move on to acknowledgement form

            else:
                st.error("Username and Password is incorrect")
