import streamlit as st
from pymongo import MongoClient
from utils.secrets_reader import SecretsRetriever

from constants import STU


def fetch_all_collections():
    if "school_collection" in st.session_state:
        st.session_state.school_collection = None
    if "user_collection" in st.session_state:
        st.session_state.user_collection = None

    secrets_retriever = SecretsRetriever()
    MONGO_URI = secrets_retriever.get_secret("mongo_uri")
    DATABASE_NAME = secrets_retriever.get_secret("mongo_database")

    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = client[DATABASE_NAME]
    st.session_state.school_collection = db["schools"]
    st.session_state.user_collection = db["users"]
    st.session_state.app_settings_collection = db["app_settings"]


def fetch_school_setting(sch_name, field_name=None, dict_input=None):
    document = st.session_state.app_settings_collection.find_one({"sch_name": sch_name})
    # If the document doesn't exist and both field_name and dict_input are provided,
    # create a new document with these details

    if not document and field_name and dict_input is not None:
        new_document = {"sch_name": sch_name, field_name: dict_input}
        st.session_state.app_settings_collection.insert_one(new_document)
        return dict_input

    # If the document exists but doesn't contain the field_name, handle the missing key
    if document and field_name and document.get(field_name) is None:
        if dict_input is not None:
            # If dict_input is provided, update the document with this new field and value
            st.session_state.app_settings_collection.update_one(
                {"sch_name": sch_name}, {"$set": {field_name: dict_input}}
            )
            return dict_input
        else:
            # If dict_input is not provided, just return None or a default value
            return None

    # If the document and field_name exist, return its value
    return document.get(field_name)


def fetch_all_schools_names():
    documents = st.session_state.school_collection.find({}, {"sch_name": 1, "_id": 0})
    sch_names = [doc["sch_name"] for doc in documents]

    if not sch_names:
        return []

    return sch_names


def fetch_students_belonging_to_teacher(school_name, selected_level, selected_class):

    if selected_level and selected_class:
        students_cursor = st.session_state.users_collection.find(
            {
                "sch_name": school_name,
                # Check if 'selected_level' is in the list of levels
                "level": {"$in": [selected_level]},
                # Check if 'selected_class' is in the list of classes
                "class": {"$in": [selected_class]},
                # Assuming "STU" is a constant representing the student profile
                "profile": STU,
            },
            # Project only the username
            {"_id": 0, "username": 1},
        )

        students = [student["username"] for student in students_cursor]

        if not students:
            st.warning("No students found for this class.")
            return []
        else:
            return students
    else:
        # If level or class is not selected, return an empty list (or you may handle this case differently)
        return []


def get_teacher_document(teacher_username):
    return st.session_state.users_collection.find_one({"username": teacher_username})
