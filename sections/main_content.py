import streamlit as st
from components.forms import login_form
from functions.personal_dashboard import personal_dashboard
from functions.ai_chatbot import ai_chatbot
from utils.app_utils import erase_all_session_state

from dotenv import load_dotenv

load_dotenv()


def load_app_main_content():
    if st.session_state.option == "Users login":
        col1, col2 = st.columns(2)

        placeholder = st.empty()
        with placeholder:
            with col1:
                login_form()

    elif st.session_state.option == "Personal Dashboard":
        personal_dashboard()

    elif st.session_state.option == "AI Chatbot":
        ai_chatbot()

    elif st.session_state.option == "Authoring Copilot":
        # Friday 7th Jun (6 hours)
        st.write("Authoring Copilot")

    elif st.session_state.option == "Short Answer FA":
        # Saturday 8th Jun (6 hours)
        st.write("Short Answer FA")

    elif st.session_state.option == "KB (RAG) Management":
        # Sunday 9th Jun (6 hours)
        st.write("KB (RAG) Management")

    elif st.session_state.option == "Prompt Management":
        # Monday 10th Jun (6 hours)
        st.write("Prompt Management")

    elif st.session_state.option == "Org Management":
        # Tuesday 11th Jun (6 hours)
        st.write("Org Management")

    elif st.session_state.option == "Profile Settings":
        # Wednesday 12th Jun (6 hours)
        st.write("Profile Settings")

    elif st.session_state.option == "Application & Prompt change logs":
        # Thursday 13th Jun (4 hours)
        st.write("Application & Prompt change logs")

    elif st.session_state.option == "Application Info":
        # Thursday 13th Jun (4 hours)
        st.write("Application Info")

    elif st.session_state.option == "Logout":
        print("logging out")
        erase_all_session_state()
        st.rerun()
