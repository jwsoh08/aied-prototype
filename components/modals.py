import streamlit as st
from config.settings import PROMPT_CONFIG, APP_CONFIG
from database.mongodb import fetch_all_schools_names, fetch_school_setting


def process_selected_school(school):
    st.session_state.user["school_id"] = school
    prompt_templates = fetch_school_setting(school, "prompt_templates", PROMPT_CONFIG)
    ai_model_settings = fetch_school_setting(school, "app_settings", APP_CONFIG)

    doc = {**prompt_templates, **ai_model_settings}

    # Initialize session state for each field in the document, excluding certain fields
    excluded_fields = ["_id", "sch_name"]
    for key, value in doc.items():
        if key not in st.session_state and key not in excluded_fields:
            session_key = key.replace(" ", "_").lower()
            st.session_state[session_key] = value

    st.success(f"{school} settings loaded successfully")
    st.session_state.sa_selected_school = school
    st.rerun()  # reload settings to update UI


@st.experimental_dialog("Select Super Admin School")
def select_super_admin_school_modal():
    st.warning("Super Administrator must select a school to load settings")

    st.write(
        f"####  :blue[Current Super Admin School: {st.session_state.sa_selected_school}]"
    )

    school_names = fetch_all_schools_names()

    if school_names == []:
        st.error("No schools found")
    else:
        school = st.selectbox(
            "###### Select School Profile/Settings (Super Admin)",
            ["Select School"] + school_names,
            key="sa_app_school",
        )

        if school != "Select School" and school != None:
            process_selected_school(school)
