import streamlit as st
import hashlib


def load_user_profile_information():
    """Loads the user profile from the database and updates session state."""
    user_document = st.session_state.u_collection.find_one(
        {"username": st.session_state.username}
    )
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
    user_document = st.session_state.u_collection.find_one({"username": username})

    if user_document and hashed_password == user_document["password"]:
        return True
    return False


def login_form():
    with st.form("Student login"):
        username = st.text_input("Enter Username:", max_chars=20).lower()
        password = st.text_input("Enter Password:", type="password", max_chars=16)
        submit_button = st.form_submit_button("Login")
        # On submit, check if new passwords match and then update the password.
        if submit_button:
            if is_valid_password(username, password):
                load_user_profile_information()
                st.session_state.login = True

            else:
                st.error("Username and Password is incorrect")
