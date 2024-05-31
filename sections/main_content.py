import streamlit as st
from components.login_form import login_form


def load_app_main_content():
    if st.session_state.option == "Users login":
        col1, col2 = st.columns(2)

        placeholder = st.empty()
        with placeholder:
            with col1:
                login_form()

    user = st.session_state["user"]
    if user:
        st.write("welcome!" + " " + user.id)
