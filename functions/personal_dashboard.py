import streamlit as st
import pandas as pd

from components.modals import select_super_admin_school_modal
from database.mongodb import (
    fetch_all_schools_names,
    fetch_students_belonging_to_teacher,
    get_teacher_document,
)
from database.sqlite3 import (
    fetch_all_conversational_data,
    fetch_conversational_data_by_school,
    fetch_data_by_username,
    fetch_data_by_students,
)

from constants import AD, STU, SA


def display_conversational_data(data, columns):
    if len(data) == 0:
        st.write("No data available")
    else:
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df)


def class_dash():
    if st.session_state.user["profile_id"] == SA:
        sch_names = fetch_all_schools_names()
        school = st.selectbox("Select School", sch_names, key="app_school")
        st.write(f"#### :blue[School Selected: {school}]")

        if st.checkbox("Show all schools data"):
            data, columns = fetch_all_conversational_data()
            display_conversational_data(data, columns)

        else:
            if st.button("Show selected school data"):
                data, columns = fetch_conversational_data_by_school(school)
                display_conversational_data(data, columns)

    elif st.session_state.user["profile_id"] == AD:
        st.write(f"#### :blue[School Selected: {st.session_state.user['school_id']}]")

        if st.button("Show School Data"):
            data, columns = fetch_conversational_data_by_school(
                st.session_state.user["school_id"]
            )
            display_conversational_data(data, columns)

    elif st.session_state.user["profile_id"] == STU:
        st.write(f"#### :blue[School Selected: {st.session_state.user['school_id']}]")

        if st.button("Show personal data"):
            data, columns = fetch_data_by_username(st.session_state.user["id"])
            display_conversational_data(data, columns)

    else:
        st.write(f"#### :blue[School Selected: {st.session_state.user['school_id']}]")
        action = st.selectbox("Select Action", ["Personal", "Class"])

        if action == "Personal":
            if st.button("Show personal data"):
                data, columns = fetch_data_by_username(st.session_state.user["id"])
                display_conversational_data(data, columns)
        else:

            if st.button("Show class data"):
                teacher_doc = get_teacher_document(st.session_state.user["id"])

                school_name = teacher_doc["sch_name"]
                selected_level = st.selectbox("Select Level", teacher_doc["level"])
                selected_class = st.selectbox("Select Class", teacher_doc["class"])

                students = fetch_students_belonging_to_teacher(
                    school_name,
                    selected_level,
                    selected_class,
                )

                data, columns = fetch_data_by_students(students)
                display_conversational_data(data, columns)


def personal_dashboard():
    if (
        st.session_state.sa_selected_school == ""
        and st.session_state.user["profile_id"] == SA
    ):
        select_super_admin_school_modal()

    st.subheader(f":green[{st.session_state.option}]")
    class_dash()
    # load_templates_class()
