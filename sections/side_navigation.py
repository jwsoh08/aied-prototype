import streamlit as st
from streamlit_antd_components import menu, MenuItem

from utils.app_utils import get_function_name


def is_function_disabled(function_name):
    return not st.session_state.func_options.get(function_name, False)


def load_app_side_navigation():
    with st.sidebar:
        if st.session_state.login == False or st.session_state.acknowledgement == False:
            st.image("assets/aied_logo.png")
            st.session_state.option = menu([MenuItem("Users login", icon="people")])

        else:
            # display menu options based on authorisation level
            st.session_state.option = menu(
                [
                    MenuItem(
                        "Home",
                        icon="house",
                        children=[
                            MenuItem(
                                get_function_name("Personal Dashboard"),
                                icon="person-circle",
                                disabled=is_function_disabled("Personal Dashboard"),
                            ),
                        ],
                    ),
                    MenuItem(
                        "SLS AI Prompt Tools",
                        icon="chat-dots",
                        children=[
                            MenuItem(
                                get_function_name(
                                    "Short Answer FA Analyser", "Short Answer FA"
                                ),
                                icon="person-circle",
                                disabled=is_function_disabled(
                                    "Short Answer FA Analyser"
                                ),
                            ),
                            MenuItem(
                                get_function_name("AC Co-Pilot", "Authoring Copilot"),
                                icon="person-circle",
                                disabled=is_function_disabled("AC Co-Pilot"),
                            ),
                        ],
                    ),
                    MenuItem(
                        "ChatBots, RAG & Prompts",
                        icon="person-fill-gear",
                        children=[
                            MenuItem(
                                get_function_name("AI Chatbot"),
                                icon="chat-dots",
                                disabled=is_function_disabled("AI Chatbot"),
                            ),
                            MenuItem(
                                get_function_name(
                                    "KB management", "KB (RAG) Management"
                                ),
                                icon="database-fill-up",
                                disabled=is_function_disabled("KB management"),
                            ),
                            MenuItem(
                                get_function_name("Prompt Management"),
                                icon="wrench",
                                disabled=is_function_disabled("Prompt Management"),
                            ),
                        ],
                    ),
                    MenuItem(
                        "Organisation Settings",
                        icon="buildings",
                        children=[
                            MenuItem(
                                get_function_name(
                                    "Organisation Management", "Org Management"
                                ),
                                icon="building-gear",
                                disabled=is_function_disabled(
                                    "Organisation Management"
                                ),
                            ),
                        ],
                    ),
                    MenuItem(type="divider"),
                    MenuItem("Profile Settings", icon="gear"),
                    MenuItem("Application Info", icon="info-circle"),
                    MenuItem("Application & Prompt change logs", icon="substack"),
                    MenuItem("Logout", icon="box-arrow-right"),
                ],
                index=1,
                format_func="title",
                open_all=True,
            )
