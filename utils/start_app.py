import os
import sqlite3
import hashlib
import streamlit as st

from pymongo import MongoClient

from database.sqlite3 import initialise_sqlite_db, get_app_config_condition
from database.mongodb import initialise_mongodb
from utils.secrets_reader import SecretsRetriever
from database.sqlite3 import (
    is_app_config_condition_true,
    insert_condition_record_in_app_config,
)

from config.settings import MENU_FUNCTIONS


def initialise_app():
    load_app_session_states()

    if st.session_state.login == False:
        initialise_sqlite_db()
        initialise_mongodb()
        initialise_admin_account()
        initialise_log_collection()

        # We may need this line of code, currently i don't see it being used
        # app_config_condition = get_app_config_condition("Prompt Change Notification")


def initialize_side_navigation_state(menu_funcs, default_value):
    # set the menu options for the user where SA is all visible and other users are not
    st.session_state.func_options = {key: default_value for key in menu_funcs.keys()}


def load_app_session_states():
    if "options" not in st.session_state:
        st.session_state.options = False

        if "school_sa_selected" not in st.session_state:
            st.session_state.school_sa_selected = ""
        if "func_options" not in st.session_state:
            st.session_state.func_options = {}
            initialize_side_navigation_state(MENU_FUNCTIONS, True)

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

        if "log_collection" not in st.session_state:
            st.session_state.log_collection = None


def initialise_admin_account():
    if is_app_config_condition_true("MOE Schools"):
        return

    secrets_retriever = SecretsRetriever()
    super_admin_exists = st.session_state.u_collection.find_one(
        {"username": secrets_retriever.get_secret("super_admin_username")},
    )

    if not super_admin_exists:
        DEFAULT_ADMIN_PASSWORD = secrets_retriever.get_secret("mongo_uri")
        hashed_password = hashlib.sha256(DEFAULT_ADMIN_PASSWORD).hexdigest()

        st.session_state.u_collection.insert_one(
            {
                "username": secrets_retriever.get_secret("super_admin_username"),
                "user_id": 0,
                "password": hashed_password,
                "profile": "Super Administrator",
                "sch_name": "MOE Schools",
            }
        )

    insert_condition_record_in_app_config("MOE Schools", True)


def initialise_log_collection():
    secrets_retriever = SecretsRetriever()
    MONGO_URI = secrets_retriever.get_secret("mongo_uri")
    DATABASE_NAME = secrets_retriever.get_secret("mongo_database")

    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = client[DATABASE_NAME]
    st.session_state.log_collection = db["log_change"]

    # Implement the log change from MongoDB to Sqlite3
    cwd = os.getcwd()
    WORKING_DIRECTORY = os.path.join(cwd, "database")
    if not os.path.exists(WORKING_DIRECTORY):
        os.makedirs(WORKING_DIRECTORY)
    WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, "sqlite3.db")
    conn = sqlite3.connect(WORKING_DATABASE)
    cursor = conn.cursor()

    # Check if the SQLite table is empty
    # If the SQLite table is empty, extract data from MongoDB and insert into SQLite
    cursor.execute("SELECT COUNT(*) FROM change_log_table")
    count = cursor.fetchone()[0]

    if count == 0:
        documents = st.session_state.log_collection.find()
        for doc in documents:
            now = doc["date"]
            app_feature = doc["app_feature"]
            prompt = doc["prompt_version"]
            changes = doc["changes"]

            cursor.execute(
                """
                INSERT INTO change_log_table (date, app_feature, prompt, changes)
                VALUES (?, ?, ?, ?)
            """,
                (now, app_feature, prompt, changes),
            )

        conn.commit()
        conn.close()
