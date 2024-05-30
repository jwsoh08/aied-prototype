import streamlit as st

from utils.start_app import load_app_session_states


def main():
    st.title("AIED Prototype")
    st.write("--------------")

    load_app_session_states()

    with st.sidebar:
        if st.session_state.login == False:
            #     create_sql_db()
            #     initialise_admin_account()
            #     check_if_empty()

            #     value = get_condition_value(PC)
            #     if value == None:
            #         # check if settings have been reset and retrieve the latest settings
            #         pass
            #     # if check_condition_value(ACP, "app_settings") == False:
            st.image("assets/aied_logo.png")
            #     st.session_state.option = menu([MenuItem("Users login", icon="people")])

        else:
            st.write("login")


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

# 	if st.session_state.option == 'Users login':
# 			col1, col2 = st.columns([3,4])
# 			placeholder = st.empty()
# 			with placeholder:
# 				with col1:
# 					#can make login faster - optimise code here
# 					if login_function() == True:
# 						#start_time = time.time()
# 						safa, acp, pt = get_last_prompt_change()
# 						st.session_state.log_msg = check_update_dates(safa, acp, pt)
# 						load_user_profile()
# 						st.session_state.login = True
# 						# if st.session_state.user['profile_id'] != SA:
# 						initialize_session_state(MENU_FUNCS, True)
# 						if st.session_state.acknowledgement == False:
# 							gen_ai_use()

# 				with col2:
# 					pass

# 	#Personal Dashboard
# 	elif st.session_state.option == 'Personal Dashboard':
# 		if st.session_state.school_sa_selected == "" and st.session_state.user['profile_id'] == SA:
# 			select_sa_school()

# 		st.subheader(f":green[{st.session_state.option}]")
# 		class_dash()
# 		load_templates_class()
# 	#workshop_activities

# 	elif st.session_state.option == 'AI Chatbot':
# 		st.subheader(f":green[{st.session_state.option}]")
# 		load_chatbot_session_states()
# 		main_chatbot_functions()
# 	elif st.session_state.option == 'Authoring Copilot':
# 		st.subheader(f":green[{st.session_state.option}]")
# 		ac_co_pilot()
# 	elif st.session_state.option == 'Short Answer FA':
# 		st.subheader(f":green[{st.session_state.option}]")
# 		prompt_analyser()
# 	elif st.session_state.option == "KB (RAG) Management":
# 		st.subheader(f":green[{st.session_state.option}]")
# 		rag_creator_mongodb()
# 	elif st.session_state.option == 'Prompt Management':
# 		st.subheader(f":green[Personal Prompt Management]")
# 		set_prompt_settings()
# 		st.divider()
# 		manage_prompt_templates()
# 	#Organisation Tools
# 	elif st.session_state.option == "Org Management":
# 		if st.session_state.user['profile_id'] == SA or st.session_state.user['profile_id'] == AD:
# 			create_flag = True
# 			if st.session_state.user['profile_id'] == SA:
# 				create_flag = False
# 			steps_options = sac.steps(
# 								items=[
# 									sac.StepsItem(title='Create new school', disabled=create_flag),
# 									sac.StepsItem(title='Manage Users'),
# 									sac.StepsItem(title='Manage School'),
# 									sac.StepsItem(title='Function Access'),
# 									sac.StepsItem(title='User Assignments'),
# 									sac.StepsItem(title='App configuration'),
# 								]
# 							)
# 			if steps_options == "Create new school":
# 				create_school()
# 			elif steps_options == "Manage School":
# 				manage_organisation()
# 			elif steps_options == "Manage Users":
# 				setup_users()
# 			elif steps_options == "Function Access":
# 				manage_app_access()
# 				st.divider()
# 				sa_delete_profile_from_school()
# 			elif steps_options == "User Assignments":

# 				#select teachers or students
# 				action = st.selectbox("Select action", ["Select", "Manage Teachers", "Manage Students"])
# 				if action == "Manage Teachers":
# 					manage_teachers_school()
# 				elif action == "Manage Students":
# 					manage_students_school()
# 			elif steps_options == "App configuration":
# 				set_app_settings()
# 				st.divider()
# 				delete_app_settings()
# 				st.divider()
# 				delete_prompt_settings()
# 				st.divider()
# 				propagate_prompts()
# 				st.divider()
# 				propagate_user_prompts()
# 				st.divider()
# 				propagate_settings()

# 			else:
# 				st.subheader(f":red[This option is accessible only to administrators only]")
# 			pass

# 	elif st.session_state.option == "Profile Settings":
# 		st.subheader(f":green[{st.session_state.option}]")
# 		#direct_vectorstore_function()
# 		col1, col2 = st.columns([1,2])
# 		with col1:
# 			st.write("#### :green[Change password]")
# 			password_settings(st.session_state.user["id"])
# 		with col2:
# 			if st.session_state.user['profile_id'] == SA:
# 				st.write("#### :green[Change School Admin Profile]")
# 				load_sa_app_settings()
# 	elif st.session_state.option == 'Application & Prompt change logs':
# 		st.subheader(f":green[{st.session_state.option}]")
# 		st.divider()
# 		app_prompt_log_change()


# 	elif st.session_state.option == 'Application Info':
# 		st.subheader(f":green[{st.session_state.option}]")

# 		if st.session_state.acknowledgement == False:
# 			gen_ai_use()
# 		else:
# 			st.write("##### :blue[You have acknowledged on the terms and conditions of using this application]")
# 			st.write("####")
# 			st.write(ACK)

# 	elif st.session_state.option == 'Logout':
# 		# if "msg" in st.session_state and st.session_state.msg != []:
# 		# 	store_summary_chatbot_response()
# 		for key in st.session_state.keys():
# 			del st.session_state[key]
# 		st.rerun()
# except Exception as e:
# 	st.exception(e)

if __name__ == "__main__":
    main()
