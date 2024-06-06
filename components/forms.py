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


def ai_chatbot_settings():
    with st.form(key="sliders_form"):
        st.write("Current User Bot Settings")
        temp = st.slider(
            "Temp",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state.default_temp),
            step=0.01,
        )
        presence_penalty = st.slider(
            "Presence Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=float(st.session_state.default_presence_penalty),
            step=0.01,
        )
        frequency_penalty = st.slider(
            "Frequency Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=float(st.session_state.default_frequency_penalty),
            step=0.01,
        )
        chat_memory = st.slider(
            "Chat Memory",
            min_value=0,
            max_value=10,
            value=int(st.session_state.default_k_memory),
            step=1,
        )
        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state.default_top_p),
            step=0.01,
        )

        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            st.session_state.default_temp = temp
            st.session_state.default_presence_penalty = presence_penalty
            st.session_state.default_frequency_penalty = frequency_penalty
            st.session_state.default_k_memory = chat_memory
            st.session_state.default_top_p = top_p
            st.success("Parameters saved!")