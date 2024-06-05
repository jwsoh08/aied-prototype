import streamlit as st
from pymongo import MongoClient
from utils.secrets_reader import SecretsRetriever


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


def fetch_document(sch_name, field_name=None, dict_input=None):
    sch_document = st.session_state.app_settings_collection.find_one(
        {"sch_name": sch_name}
    )
    # If the sch_document doesn't exist and both field_name and dict_input are provided,
    # create a new sch_document with these details

    if not sch_document and field_name and dict_input is not None:
        new_document = {"sch_name": sch_name, field_name: dict_input}
        st.session_state.app_settings_collection.insert_one(new_document)
        return dict_input

    # If the sch_document exists but doesn't contain the field_name, handle the missing key
    if sch_document and field_name and sch_document.get(field_name) is None:
        if dict_input is not None:
            # If dict_input is provided, update the sch_document with this new field and value
            st.session_state.app_settings_collection.update_one(
                {"sch_name": sch_name}, {"$set": {field_name: dict_input}}
            )
            return dict_input
        else:
            # If dict_input is not provided, just return None or a default value
            return None

    # If the sch_document and field_name exist, return its value
    return sch_document.get(field_name)
