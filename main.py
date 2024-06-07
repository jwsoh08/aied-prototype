import os
import streamlit as st
import streamlit_antd_components as sac

from utils.app_utils import initialise_app
from sections.side_navigation import load_app_side_navigation
from sections.main_content import load_app_main_content


def main():
    print("running main()")
    try:
        st.title("AIED Prototype")
        sac.divider(label='COTF', icon='house', align='center')

        initialise_app()
        load_app_side_navigation()
        load_app_main_content()

        # Assuming we only operate in dev and prod
        if os.getenv("ENVIRONMENT", "PRODUCTION") == "DEVELOPMENT":
            st.warning("In development mode")
            st.write(st.session_state)

    except Exception as e:
        st.exception(e)


if __name__ == "__main__":
    main()
