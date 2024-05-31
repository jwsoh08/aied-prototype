import streamlit as st
from pymongo import MongoClient
from utils.secrets_reader import SecretsRetriever


def initialise_mongodb():
    if "s_collection" in st.session_state:
        st.session_state.s_collection = None
    if "u_collection" in st.session_state:
        st.session_state.u_collection = None

    secrets_retriever = SecretsRetriever()
    MONGO_URI = secrets_retriever.get_secret("mongo_uri")
    DATABASE_NAME = secrets_retriever.get_secret("mongo_database")

    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = client[DATABASE_NAME]
    st.session_state.s_collection = db["schools"]
    st.session_state.u_collection = db["users"]
