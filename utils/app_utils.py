import os
import sqlite3
import hashlib
import streamlit as st

from pymongo import MongoClient

from database.sqlite3 import initialise_sqlite_db
from database.mongodb import fetch_all_collections, fetch_school_setting
from utils.secrets_reader import SecretsRetriever
from database.sqlite3 import (
    is_app_config_condition_true,
    insert_condition_record_in_app_config,
)

from config.settings import MENU_FUNCTIONS, PROMPT_CONFIG, APP_CONFIG
from constants import GEN_AI_ACKNOWLEDGEMENT


def initialise_app():
    load_initial_app_session_states()

    if st.session_state.login == False:
        initialise_sqlite_db()
        fetch_all_collections()
        initialise_admin_account()
        initialise_log_collection()
    else:
        # At this point user has logged in
        if st.session_state.acknowledgement == False:
            generative_ai_use_acknowledgement()

        else:
            if st.session_state.user["profile_id"] == "Super Administrator":
                initialize_side_navigation_state(MENU_FUNCTIONS, True)
            else:
                set_function_access_for_user()

            load_app_configuration("prompt_templates", PROMPT_CONFIG)
            load_app_configuration("app_settings", APP_CONFIG)
            st.session_state.option = "Personal Dashboard"

        # We may need this line of code, currently i don't see it being used
        # app_config_condition = get_app_config_condition("Prompt Change Notification")


def load_app_configuration(config_type, settings):
    if st.session_state.user["profile_id"] == "Super Administrator":
        return

    excluded_fields = ["_id", "sch_name"]
    doc = fetch_school_setting(
        st.session_state.user["school_id"], config_type, settings
    )

    if not doc:
        st.error(f"No {config_type} settings found")
        return

    # Initialize session state for each field in the document, excluding certain fields
    for key, value in doc.items():
        if key not in st.session_state and key not in excluded_fields:
            session_key = key.replace(" ", "_").lower()
            st.session_state[session_key] = value


def load_initial_app_session_states():
    if "options" not in st.session_state:
        st.session_state.options = False

        if "app_config" not in st.session_state:
            st.session_state.app_config = {}

        if "sa_selected_school" not in st.session_state:
            st.session_state.sa_selected_school = ""

        if "func_options" not in st.session_state:
            st.session_state.func_options = {}
            initialize_side_navigation_state(MENU_FUNCTIONS, False)

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

        if "app_settings_collection" not in st.session_state:
            st.session_state.app_settings_collection = None


def initialise_admin_account():
    if is_app_config_condition_true("MOE Schools"):
        return

    secrets_retriever = SecretsRetriever()
    super_admin_exists = st.session_state.user_collection.find_one(
        {"username": secrets_retriever.get_secret("super_admin_username")}
    )

    if not super_admin_exists:
        DEFAULT_ADMIN_PASSWORD = secrets_retriever.get_secret("mongo_uri")
        hashed_password = hashlib.sha256(DEFAULT_ADMIN_PASSWORD).hexdigest()

        st.session_state.user_collection.insert_one(
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


def set_function_access_for_user():
    user_document = st.session_state.user_collection.find_one(
        {"username": st.session_state.user["id"]}
    )

    if not user_document:
        st.error("User not found. Please add the user first.")
        return

    sch_document = st.session_state.school_collection.find_one(
        {"sch_name": st.session_state.user["school_id"]}
    )
    if not sch_document:
        st.error("School not found. Please add the school first.")
        return

    profile_name = user_document.get("profile", "")
    user_function_access = sch_document.get(profile_name, {})

    # Initialize or update function options
    if not user_function_access:
        # Assume all functions are enabled if not explicitly disabled
        st.session_state.func_options = {key: True for key in MENU_FUNCTIONS.keys()}
    else:
        # If the profile exists and has functions
        # Load existing function options, defaulting to True (enabled) for functions not mentioned
        st.session_state.func_options = {
            func: user_function_access.get(func, True) for func in MENU_FUNCTIONS.keys()
        }


def initialize_side_navigation_state(menu_funcs, default_value):
    # set the menu options for the user where SA is all visible and other users are not
    st.session_state.func_options = {key: default_value for key in menu_funcs.keys()}


def get_function_name(function_name, default_name=""):
    """
    This helper function enables/disables the function name
    on the side navigation menu, effectively only providing
    access to what the current user is authorised to do.
    """
    if st.session_state.func_options.get(function_name, False) == False:
        return "-"
    else:
        if default_name == "":
            return function_name
        else:
            return default_name


def erase_all_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]


def load_user_profile_information(username):
    """Loads the user profile from the database and updates session state."""
    user_document = st.session_state.user_collection.find_one({"username": username})

    if user_document:
        user_profile = {
            "id": user_document["username"],
            "profile_id": user_document["profile"],
            "school_id": user_document["sch_name"],
        }
        st.session_state.user = user_profile


def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def is_valid_password(username, password):
    """Checks if the password matches the stored password."""
    hashed_password = hash_password(password)
    user_document = st.session_state.user_collection.find_one({"username": username})
    if user_document and hashed_password == user_document["password"]:
        return True
    return False


@st.experimental_dialog("Terms and Conditions of Use")
def generative_ai_use_acknowledgement():
    st.write(GEN_AI_ACKNOWLEDGEMENT)
    st.info(st.session_state.log_msg)
    if st.button("I acknowledge the above information"):
        st.session_state.acknowledgement = True
        st.rerun()  # To load more app settings after acknowledgement
