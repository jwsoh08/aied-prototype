import streamlit as st


def load_app_session_states():
    if "options" not in st.session_state:
        st.session_state.options = False

        if "school_sa_selected" not in st.session_state:
            st.session_state.school_sa_selected = ""
        # if "func_options" not in st.session_state:
        #     st.session_state.func_options = {}
        #     initialize_session_state(MENU_FUNCS, True)

        if "acknowledgement" not in st.session_state:
            st.session_state.acknowledgement = False

        if "login" not in st.session_state:
            st.session_state.login = False

        if "user" not in st.session_state:
            st.session_state.user = {}

        if "username" not in st.session_state:
            st.session_state.username = ""

        if "log_msg" not in st.session_state:
            st.session_state.log_msg = "No log or app updates within the last 2 weeks"
