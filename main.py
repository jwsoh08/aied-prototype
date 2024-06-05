import os
import streamlit as st

from utils.app_utils import initialise_app
from sections.side_navigation import load_app_side_navigation
from sections.main_content import load_app_main_content


def main():
    print("running main()")
    try:
        st.title("AIED Prototype")
        st.write("--------------")

        initialise_app()
        load_app_side_navigation()
        load_app_main_content()

        if os.environ["ENVIRONMENT"] == "DEVELOPMENT":
            st.warning("In development mode")
            st.write(st.session_state)

    except Exception as e:
        st.exception(e)


if __name__ == "__main__":
    main()
