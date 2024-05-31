import streamlit as st
from streamlit_antd_components import menu, MenuItem


def load_app_side_navigation():
    with st.sidebar:
        if st.session_state.login == False:
            st.image("assets/aied_logo.png")
            st.session_state.option = menu([MenuItem("Users login", icon="people")])

        else:
            st.write("You should see some navigation options here based on what is authorised for the logged in user.")
            

    # 			#can do a test if user is school is something show a different logo and set a different API key
    # 			if st.session_state.user['profile_id'] == SA: #super admin login feature
    # 				# Initialize the session state for function options
    # 				initialize_session_state(MENU_FUNCS, False)

    # 			else:
    # 				#if user has not acknowledged the use of AI, then the user cannot access the application
    # 				if st.session_state.acknowledgement == False:
    # 					initialize_session_state(MENU_FUNCS, True)
    # 				else:
    # 					#setting the menu options for the user
    # 					set_function_access_for_user()
    # 			#menu options for the application
    # 			st.session_state.option = sac.menu([
    # 				sac.MenuItem('Home', icon='house', children=[
    # 					sac.MenuItem(return_function_name('Personal Dashboard'), icon='person-circle', disabled=is_function_disabled('Personal Dashboard')),
    # 				]),
    # 				#Menu for COTF
    # 				#Menu for Metacognition
    # 				sac.MenuItem('SLS AI Prompt Tools', icon='chat-dots', children=[
    # 					sac.MenuItem(return_function_name('Short Answer FA Analyser', "Short Answer FA"), icon='person-circle', disabled=is_function_disabled('Short Answer FA Analyser')),
    # 					sac.MenuItem(return_function_name('AC Co-Pilot', 'Authoring Copilot'), icon='person-circle', disabled=is_function_disabled('AC Co-Pilot')),
    # 				]),
    # 				#Menu for SLS GenAI bulk testing
    # 					#Menu for Short Answer FA
    # 					#Menu for Authoring Copilot
    # 				#Menu for SLS Proof of Concept tesing

    # 				sac.MenuItem('ChatBots, RAG & Prompts', icon='person-fill-gear', children=[
    # 					sac.MenuItem(return_function_name('AI Chatbot'), icon='chat-dots', disabled=is_function_disabled('AI Chatbot')),
    # 					sac.MenuItem(return_function_name('KB management', 'KB (RAG) Management'), icon='database-fill-up',disabled=is_function_disabled('KB management')),
    # 					sac.MenuItem(return_function_name('Prompt Management'), icon='wrench', disabled=is_function_disabled('Prompt Management')),
    # 				]),
    # 				sac.MenuItem('Organisation Settings', icon='buildings', children=[
    # 					sac.MenuItem(return_function_name( 'Organisation Management','Org Management'), icon='building-gear', disabled=is_function_disabled('Organisation Management')),
    # 				]),
    # 				sac.MenuItem(type='divider'),
    # 				sac.MenuItem('Profile Settings', icon='gear'),
    # 				sac.MenuItem('Application Info', icon='info-circle'),
    # 				sac.MenuItem('Application & Prompt change logs', icon='substack'),
    # 				sac.MenuItem('Logout', icon='box-arrow-right'),
    # 			], index=1, format_func='title', open_all=True)
