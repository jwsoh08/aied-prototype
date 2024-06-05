import streamlit as st
from components.login_form import login_form
from utils.app_utils import erase_all_session_state


def load_app_main_content():
    if st.session_state.option == "Users login":
        col1, col2 = st.columns(2)

        placeholder = st.empty()
        with placeholder:
            with col1:
                login_form()

    elif st.session_state.option == "Personal Dashboard":
        st.write("personal dashboard")

    elif st.session_state.option == "AI Chatbot":
        st.write("AI Chatbot")

    elif st.session_state.option == "Authoring Copilot":
        st.write("Authoring Copilot")

    elif st.session_state.option == "Short Answer FA":
        st.write("Short Answer FA")

    elif st.session_state.option == "KB (RAG) Management":
        st.write("KB (RAG) Management")

    elif st.session_state.option == "Prompt Management":
        st.write("Prompt Management")

    elif st.session_state.option == "Org Management":
        st.write("Org Management")

    elif st.session_state.option == "Profile Settings":
        st.write("Profile Settings")

    elif st.session_state.option == "Application & Prompt change logs":
        st.write("Application & Prompt change logs")

    elif st.session_state.option == "Application Info":
        st.write("Application Info")

    elif st.session_state.option == "Logout":
        erase_all_session_state()
        st.rerun()
