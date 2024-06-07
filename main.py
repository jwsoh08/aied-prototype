#No need SQLite
import streamlit as st
from streamlit_antd_components import menu, MenuItem
import streamlit_antd_components as sac
from basecode2.app_management import load_app_settings, load_sa_app_settings, propagate_prompts, propagate_settings, propagate_user_prompts
from basecode2.authenticate import login_function
from basecode2.personal_prompt import set_prompt_settings, manage_prompt_templates, load_templates_class
from basecode2.rag_mongodb import rag_creator_mongodb
from basecode2.app_management import set_app_settings, delete_app_settings, delete_prompt_settings
from basecode2.prompt_log_changes import app_prompt_log_change, check_if_empty, get_last_prompt_change, check_update_dates
from basecode2.org_module import (
	setup_users, 
	manage_app_access, 
	manage_organisation, 
	initialise_admin_account, 
	create_school, 
	load_user_profile, 
	set_function_access_for_user, 
	sa_delete_profile_from_school,
	manage_students_school,
	manage_teachers_school,
	)
from basecode2.sqlite_db import create_sql_db, insert_condition_value, check_condition_value, get_condition_value
from basecode2.chatbot import main_chatbot_functions
from basecode2.pwd_module import password_settings
from basecode2.class_dash import class_dash
from aied_functions.safa_functions import prompt_analyser
from aied_functions.ac_copilot import ac_co_pilot

import configparser
import ast
import ssl
import time

from utils.secrets_reader import SecretsRetriever
			  
try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	pass
else:
	ssl._create_default_https_context = _create_unverified_https_context

class ConfigHandler:
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')

	def get_value(self, section, key):
		value = self.config.get(section, key)
		try:
			# Convert string value to a Python data structure
			return ast.literal_eval(value)
		except (SyntaxError, ValueError):
			# If not a data structure, return the plain string
			return value

# Initialization
config_handler = ConfigHandler()

# Setting Streamlit configurations
st.set_page_config(layout="wide")

MENU_FUNCS = config_handler.get_value('menu_lists', 'MENU_FUNCS')
SA = config_handler.get_value('constants', 'SA')
AD = config_handler.get_value('constants', 'AD')
PC = config_handler.get_value('constants', 'PC')
ACK = config_handler.get_value('application_agreement', 'ACK')
PROTOTYPE = config_handler.get_value('constants', 'PROTOTYPE')
PROMPT_CONFIG = config_handler.get_value('menu_lists', 'PROMPT_CONFIG')
APP_CONFIG = config_handler.get_value('menu_lists', 'APP_CONFIG')


#function for menu options
def is_function_disabled(function_name):
	return st.session_state.func_options.get(function_name, True)

#change option name in the st.sidebar	
def return_function_name(function_name, default_name = ""):
	if st.session_state.func_options.get(function_name, True):
		return "-"
	else:
		if default_name == "":
			return function_name
		else:
			return default_name
		
#set the menu options for the user where SA is all visible and other users are not 
def initialize_session_state( menu_funcs, default_value):
	st.session_state.func_options = {key: default_value for key in menu_funcs.keys()}


def load_app_session_states():
	if "school_sa_selected" not in st.session_state:
		st.session_state.school_sa_selected = ""
	if "func_options" not in st.session_state:
		st.session_state.func_options = {}
		initialize_session_state(MENU_FUNCS, True)
	
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
  

#Base chabot settings and chatbot session states
def load_chatbot_session_states():
	if "msg" not in st.session_state:
		st.session_state.msg = []
	
	if "memoryless" not in st.session_state:
		st.session_state.memoryless = False

	if "chatbot" not in st.session_state:
		st.session_state.chatbot = "You are a helpful assistant"
	
	#Vectorstore aka RAG KB 
	if "vs" not in st.session_state:
		st.session_state.vs = None

	if "current_kb_model" not in st.session_state:
		st.session_state.current_kb_model = ""

	if "button_text" not in st.session_state:
		st.session_state.button_text = "Cancel"

	if "data_doc" not in st.session_state:
		st.session_state.data_doc = ""
		
	if "download_response_flag" not in st.session_state:
		st.session_state.download_response_flag = False
	
	if "chat_response" not in st.session_state:
		st.session_state.chat_response = ""

	if "rag_response" not in st.session_state:
		st.session_state.rag_response = None
  
@st.experimental_dialog("Terms and Conditions of Use")
def gen_ai_use():
	st.write(ACK)
	st.info(st.session_state.log_msg)
	if st.button("I acknowledge the above information"):
		st.session_state.acknowledgement = True
		set_function_access_for_user()
		load_app_settings("prompt_templates", PROMPT_CONFIG)
		load_app_settings("app_settings", APP_CONFIG)
		st.session_state.option = 'Personal Dashboard'
		st.rerun()

@st.experimental_dialog("Select Super Admin School")
def select_sa_school():	
	if st.session_state.user['profile_id'] == SA:
		load_sa_app_settings()
	if st.session_state.school_sa_selected != "":
		st.rerun()		

def load_safa_session_states():
	#initialize session state for JSON Tools in Short Answer
	if "tools" not in st.session_state:
		st.session_state.tools = []


def main():
	try:
		secret_retriever = SecretsRetriever()
		app_title = secret_retriever.get_secret("default_title")
		
		st.title(app_title)
		sac.divider(label='ETD & ITD Framework', icon='house', align='center')
		#initialize session state options for side menubar for the application
		if "options" not in st.session_state:
			st.session_state.options = False
			load_app_session_states()
			
		with st.sidebar: #options for sidebar
			if st.session_state.login == False:
				#initialize the application settings
				create_sql_db()
				initialise_admin_account()
				check_if_empty()
    
				value = get_condition_value(PC)
				if value == None:
					#check if settings have been reset and retrieve the latest settings
					pass
				#if check_condition_value(ACP, "app_settings") == False:
				st.image("app_logo/aied.png")
				st.session_state.option = menu([MenuItem('Users login', icon='people')])
			else:
				#can do a test if user is school is something show a different logo and set a different API key
				if st.session_state.user['profile_id'] == SA: #super admin login feature
					# Initialize the session state for function options	
					initialize_session_state(MENU_FUNCS, False)
					
				else:
					#if user has not acknowledged the use of AI, then the user cannot access the application
					if st.session_state.acknowledgement == False:
						initialize_session_state(MENU_FUNCS, True)
					else:
						#setting the menu options for the user
						set_function_access_for_user()
				#menu options for the application	
				st.session_state.option = sac.menu([
					sac.MenuItem('Home', icon='house', children=[
						sac.MenuItem(return_function_name('Personal Dashboard'), icon='person-circle', disabled=is_function_disabled('Personal Dashboard')),
					]),
					#Menu for COTF
					#Menu for Metacognition
					sac.MenuItem('SLS AI Prompt Tools', icon='chat-dots', children=[
						sac.MenuItem(return_function_name('Short Answer FA Analyser', "Short Answer FA"), icon='person-circle', disabled=is_function_disabled('Short Answer FA Analyser')),
						sac.MenuItem(return_function_name('AC Co-Pilot', 'Authoring Copilot'), icon='person-circle', disabled=is_function_disabled('AC Co-Pilot')),
					]),
					#Menu for SLS GenAI bulk testing
						#Menu for Short Answer FA
						#Menu for Authoring Copilot
					#Menu for SLS Proof of Concept tesing
			
					sac.MenuItem('ChatBots, RAG & Prompts', icon='person-fill-gear', children=[
						sac.MenuItem(return_function_name('AI Chatbot'), icon='chat-dots', disabled=is_function_disabled('AI Chatbot')),
						sac.MenuItem(return_function_name('KB management', 'KB (RAG) Management'), icon='database-fill-up',disabled=is_function_disabled('KB management')),
						sac.MenuItem(return_function_name('Prompt Management'), icon='wrench', disabled=is_function_disabled('Prompt Management')),						
					]),
					sac.MenuItem('Organisation Settings', icon='buildings', children=[
						sac.MenuItem(return_function_name( 'Organisation Management','Org Management'), icon='building-gear', disabled=is_function_disabled('Organisation Management')),
					]),
					sac.MenuItem(type='divider'),
					sac.MenuItem('Profile Settings', icon='gear'),
					sac.MenuItem('Application Info', icon='info-circle'),
					sac.MenuItem('Application & Prompt change logs', icon='substack'),
					sac.MenuItem('Logout', icon='box-arrow-right'),
				], index=1, format_func='title', open_all=True)
		
		if st.session_state.option == 'Users login':
				col1, col2 = st.columns([3,4])
				placeholder = st.empty()
				with placeholder:
					with col1:
						#can make login faster - optimise code here
						if login_function() == True:
							#start_time = time.time()
							safa, acp, pt = get_last_prompt_change()
							st.session_state.log_msg = check_update_dates(safa, acp, pt)
							load_user_profile()
							st.session_state.login = True
							# if st.session_state.user['profile_id'] != SA:
							initialize_session_state(MENU_FUNCS, True)
							if st.session_state.acknowledgement == False:
								gen_ai_use()

					with col2:
						pass
		
		#Personal Dashboard
		elif st.session_state.option == 'Personal Dashboard':
			if st.session_state.school_sa_selected == "" and st.session_state.user['profile_id'] == SA:
				select_sa_school()
			
			st.subheader(f":green[{st.session_state.option}]")
			class_dash()
			load_templates_class()
		#workshop_activities
			
		elif st.session_state.option == 'AI Chatbot':
			st.subheader(f":green[{st.session_state.option}]")
			load_chatbot_session_states()
			main_chatbot_functions()
		elif st.session_state.option == 'Authoring Copilot':
			st.subheader(f":green[{st.session_state.option}]")
			ac_co_pilot()
		elif st.session_state.option == 'Short Answer FA':
			st.subheader(f":green[{st.session_state.option}]")
			prompt_analyser()
		elif st.session_state.option == "KB (RAG) Management":
			st.subheader(f":green[{st.session_state.option}]") 
			rag_creator_mongodb()
		elif st.session_state.option == 'Prompt Management':
			st.subheader(f":green[Personal Prompt Management]")
			set_prompt_settings()
			st.divider()
			manage_prompt_templates()	
		#Organisation Tools
		elif st.session_state.option == "Org Management":
			if st.session_state.user['profile_id'] == SA or st.session_state.user['profile_id'] == AD:
				create_flag = True
				if st.session_state.user['profile_id'] == SA:
					create_flag = False
				steps_options = sac.steps(
									items=[
										sac.StepsItem(title='Create new school', disabled=create_flag),
										sac.StepsItem(title='Manage Users'),
										sac.StepsItem(title='Manage School'),
										sac.StepsItem(title='Function Access'),
										sac.StepsItem(title='User Assignments'),
										sac.StepsItem(title='App configuration'),
									]
								)
				if steps_options == "Create new school":
					create_school()
				elif steps_options == "Manage School":
					manage_organisation()
				elif steps_options == "Manage Users":
					setup_users()
				elif steps_options == "Function Access":
					manage_app_access()
					st.divider()
					sa_delete_profile_from_school()
				elif steps_options == "User Assignments":
	
					#select teachers or students
					action = st.selectbox("Select action", ["Select", "Manage Teachers", "Manage Students"])
					if action == "Manage Teachers":
						manage_teachers_school()
					elif action == "Manage Students":
						manage_students_school()
				elif steps_options == "App configuration":
					set_app_settings()
					st.divider()
					delete_app_settings()
					st.divider()
					delete_prompt_settings()
					st.divider()
					propagate_prompts()
					st.divider()
					propagate_user_prompts()
					st.divider()
					propagate_settings()

				else:
					st.subheader(f":red[This option is accessible only to administrators only]")	
				pass

		elif st.session_state.option == "Profile Settings":
			st.subheader(f":green[{st.session_state.option}]") 
			#direct_vectorstore_function()
			col1, col2 = st.columns([1,2])
			with col1:
				st.write("#### :green[Change password]")
				password_settings(st.session_state.user["id"])
			with col2:
				if st.session_state.user['profile_id'] == SA:
					st.write("#### :green[Change School Admin Profile]")
					load_sa_app_settings()
		elif st.session_state.option == 'Application & Prompt change logs':
			st.subheader(f":green[{st.session_state.option}]")
			st.divider()
			app_prompt_log_change()


		elif st.session_state.option == 'Application Info':
			st.subheader(f":green[{st.session_state.option}]") 
			
			if st.session_state.acknowledgement == False:
				gen_ai_use()
			else:
				st.write("##### :blue[You have acknowledged on the terms and conditions of using this application]")
				st.write("####")
				st.write(ACK)

		elif st.session_state.option == 'Logout':
			# if "msg" in st.session_state and st.session_state.msg != []:
			# 	store_summary_chatbot_response()
			for key in st.session_state.keys():
				del st.session_state[key]
			st.rerun()			
	except Exception as e:
		st.exception(e)

if __name__ == "__main__":
	main()

