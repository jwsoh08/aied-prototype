import streamlit as st
from components.modals import select_super_admin_school_modal


def personal_dashboard():
    if st.session_state.sa_selected_school == "" and st.session_state.user["profile_id"] == "Super Administrator":
        select_super_admin_school_modal()
        
    st.subheader(f":green[{st.session_state.option}]")
    # class_dash()
    # load_templates_class()
