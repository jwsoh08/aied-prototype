import sqlite3
import streamlit as st
import os
import configparser
import ast
from pymongo import MongoClient
from datetime import datetime, timedelta

from utils.secrets_reader import SecretsRetriever

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
SQL_DB = config_handler.get_value('DATABASE', 'SQL_DB')
CHANGES = config_handler.get_value('Prompt_Design_Templates', 'CHANGES')
SA = config_handler.get_value('constants', 'SA')
# def app_prompt_log_change():
# 	tab1, tab2, tab3 = st.tabs(["#### ShortAnsFA", "#### ACP", "#### Prompt Testing App"])
# 	cwd = os.getcwd()
# 	WORKING_DIRECTORY = os.path.join(cwd, "database")
# 	if not os.path.exists(WORKING_DIRECTORY):
# 		os.makedirs(WORKING_DIRECTORY)
# 	WORKING_DATABASE = os.path.join(WORKING_DIRECTORY , SQL_DB)
	
# 	conn = sqlite3.connect(WORKING_DATABASE)
# 	cursor = conn.cursor()

# 	with tab1:
# 		st.write("#### :blue[Short Answer Feedback Assistant (ShortAnsFA) Prompt Version Changes]")

# 		# Retrieve data from change_log_table for ShortAnsFA
# 		cursor.execute('''
# 			SELECT date, prompt, changes
# 			FROM change_log_table
# 			WHERE app_feature LIKE 'SAFA%'
# 			ORDER BY date DESC
# 		''')
# 		safa_changes = cursor.fetchall()

# 		if safa_changes:
# 			last_change = safa_changes[0]
# 			col1, col2, col3 = st.columns([1,3,1])
# 			with col1:
# 				st.write("### Date")
# 				date = st.container(height= 500, border=True)
# 				# date.write("Date")
# 				date.write(f"#### {last_change[0]}")
# 			with col2:
# 				st.write("### Prompt Change")
# 				prompt = st.container(height= 500, border=True)
# 				# prompt.write("Prompt Change")
# 				prompt.code(last_change[1])
# 			with col3:
# 				st.write("### Changes")
# 				changes = st.container(height= 500, border=True)
# 				# changes.write("Changes")
# 				changes.write(last_change[2])


# 			with st.expander("Previous Prompt Changes"):
# 				for change in safa_changes[1:]:
# 					col1, col2, col3 = st.columns([1,3,1])
# 					with col1:
# 						st.write("### Date")
# 						date = st.container(height= 500, border=True)
# 						# date.write("Date")
# 						date.write(f"#### {change[0]}")
# 					with col2:
# 						st.write("### Prompt Change")
# 						prompt = st.container(height= 500, border=True)
# 						# prompt.write("Prompt Change")
# 						prompt.code(change[1])
# 					with col3:
# 						st.write("### Changes")
# 						changes = st.container(height= 500, border=True)
# 						# changes.write("Changes")
# 						changes.write(change[2])

# 	with tab2:
# 		st.write("#### :green[Authoring CoPilot (ACP) Prompt Version Changes]")

# 		# Retrieve data from change_log_table for ACP
# 		cursor.execute('''
# 			SELECT date, prompt, changes
# 			FROM change_log_table
# 			WHERE app_feature LIKE 'ACP%'
# 			ORDER BY date DESC
# 		''')
# 		acp_changes = cursor.fetchall()

# 		if acp_changes:
# 			last_change = acp_changes[0]
# 			col1, col2, col3 = st.columns(3)
# 			col1.write("Date")
# 			col2.write("Prompt Change")
# 			col3.write("Changes")
# 			col1.write(last_change[0])
# 			col2.write(last_change[1])
# 			col3.write(last_change[2])

# 			with st.expander("Previous Prompt Changes"):
# 				col1, col2, col3 = st.columns(3)
# 				col1.write("Date")
# 				col2.write("Prompt Change")
# 				col3.write("Changes")
# 				for change in acp_changes[1:]:
# 					col1.write(change[0])
# 					col2.write(change[1])
# 					col3.write(change[2])




# 	with tab3:
# 		st.write("#### :red[Prompt Testing Tool Version Changes]")

# 		# Retrieve data from change_log_table for Prompt Testing App
# 		cursor.execute('''
# 			SELECT date, app_feature, changes
# 			FROM change_log_table
# 			WHERE app_feature NOT LIKE 'SAFA%' AND app_feature NOT LIKE 'ACP%'
# 			ORDER BY date DESC
# 		''')
# 		app_changes = cursor.fetchall()

# 		if app_changes:
# 			last_change = app_changes[0]
# 			st.write(f"Last change: {last_change[0]}")
# 			st.write(f"Feature Version: {last_change[1]}")
# 			st.write(f"Changes: {last_change[2]}")

# 			with st.expander("Previous App Changes"):
# 				for change in app_changes[1:]:
# 					st.write(f"Date: {change[0]}")
# 					st.write(f"Feature Version: {change[1]}")
# 					st.write(f"Changes: {change[2]}")
@st.experimental_dialog("Update App Change")
def update_app_version():
	key_changes = st.text_area("Key Changes/Improvements", value=CHANGES, key='app_new_prompt', height=400)
	version = st.text_area("Version Number", key='app_new_changes', height=200)
	if st.button(f"Confirmed Update Log Change for Prompt Testing Tool"):
		prompt_change("Prompt Testing Tool",key_changes, version)
		st.success("App Log Change Updated Successfully")
		st.rerun()


def get_last_prompt_change():
	safa_date_change = None
	acp_date_change = None
	app_date_change = None
	cwd = os.getcwd()
	WORKING_DIRECTORY = os.path.join(cwd, "database")
	if not os.path.exists(WORKING_DIRECTORY):
		os.makedirs(WORKING_DIRECTORY)
	WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, SQL_DB)
	conn = sqlite3.connect(WORKING_DATABASE)
	cursor = conn.cursor()
	cursor.execute('''
		SELECT date, prompt, changes 
		FROM change_log_table
		WHERE app_feature LIKE 'SAFA%'
		ORDER BY date DESC
	''')
	safa_changes = cursor.fetchall()
	if safa_changes:
		safa_date_change = safa_changes[0][0]
	cursor.execute('''
			SELECT date, prompt, changes
			FROM change_log_table
			WHERE app_feature LIKE 'ACP%'
			ORDER BY date DESC
		''')
	acp_changes = cursor.fetchall()
	if acp_changes:
		acp_date_change = acp_changes[0][0]
	
	cursor.execute('''
			SELECT date, app_feature, changes
			FROM change_log_table
			WHERE app_feature NOT LIKE 'SAFA%' AND app_feature NOT LIKE 'ACP%'
			ORDER BY date DESC
		''')
	app_changes = cursor.fetchall()
	if app_changes:
		app_date_change = app_changes[0][0]
	conn.close()
	return safa_date_change, acp_date_change, app_date_change
	


def app_prompt_log_change():
	
	tab1, tab2, tab3 = st.tabs(["###### ShortAnsFA", "###### ACP", "###### Prompt Testing App"])
	cwd = os.getcwd()
	WORKING_DIRECTORY = os.path.join(cwd, "database")
	if not os.path.exists(WORKING_DIRECTORY):
		os.makedirs(WORKING_DIRECTORY)
	WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, SQL_DB)
	conn = sqlite3.connect(WORKING_DATABASE)
	cursor = conn.cursor()

	def display_changes(changes, title):
		if changes:
			last_change = changes[0]
			col1, col2, col3 = st.columns([1, 3, 1])

			with col1:
				st.write("##### Date")
				date = st.container(height=500, border=True)
				date.write(f"###### {last_change[0]}")

			with col2:
				st.write("##### Prompt Change")
				prompt = st.container(height=500, border=True)
				prompt.code(last_change[1])

			with col3:
				st.write("##### Changes")
				changes_container = st.container(height=500, border=True)
				changes_container.write(last_change[2])

			with st.expander("Previous Prompt Changes"):
				for change in changes[1:]:
					col1, col2, col3 = st.columns([1, 3, 1])

					with col1:
						st.write("##### Date")
						date = st.container(height=500, border=True)
						date.write(f"###### {change[0]}")

					with col2:
						st.write("##### Prompt Change")
						prompt = st.container(height=500, border=True)
						prompt.code(change[1])

					with col3:
						st.write("##### Changes")
						changes_container = st.container(height=500, border=True)
						changes_container.write(change[2])

	with tab1:
		st.write("#### :blue[Short Answer Feedback Assistant (ShortAnsFA) Prompt Version Changes]")
		cursor.execute('''
			SELECT date, prompt, changes 
			FROM change_log_table
			WHERE app_feature LIKE 'SAFA%'
			ORDER BY date DESC
		''')
		safa_changes = cursor.fetchall()
		st.divider()
		display_changes(safa_changes, "ShortAnsFA")

	with tab2:
		st.write("#### :green[Authoring CoPilot (ACP) Prompt Version Changes]")
		cursor.execute('''
			SELECT date, prompt, changes
			FROM change_log_table
			WHERE app_feature LIKE 'ACP%'
			ORDER BY date DESC
		''')
		acp_changes = cursor.fetchall()
		st.divider()
		display_changes(acp_changes, "ACP")

	with tab3:
		st.write("#### :red[Prompt Testing Tool Version Changes]")
		if st.button("Update App Change") and st.session_state.user['profile_id'] == SA:
			update_app_version()
		cursor.execute('''
			SELECT date, app_feature, changes
			FROM change_log_table
			WHERE app_feature NOT LIKE 'SAFA%' AND app_feature NOT LIKE 'ACP%'
			ORDER BY date DESC
		''')
		app_changes = cursor.fetchall()
		st.divider()

		if app_changes:
			last_change = app_changes[0]
			col1, col2, col3 = st.columns([1, 1, 2])

			with col1:
				st.write("##### Date")
				date = st.container(height=500, border=True)
				date.write(f"###### {last_change[0]}")

			with col2:
				st.write("##### Updates and Improvements")
				feature = st.container(height=500, border=True)
				feature.write(f"###### {last_change[1]}")

			with col3:
				st.write("##### Version Change")
				changes_container = st.container(height=500, border=True)
				changes_container.write(last_change[2])

			with st.expander("Previous App Changes"):
				for change in app_changes[1:]:
					col1, col2, col3 = st.columns([1, 1, 2])

					with col1:
						st.write("##### Date")
						date = st.container(height=500, border=True)
						date.write(f"###### {change[0]}")

					with col2:
						st.write("##### Updates and Improvements")
						feature = st.container(height=500, border=True)
						feature.write(f"###### {change[1]}")

					with col3:
						st.write("##### Version Change")
						changes_container = st.container(height=500, border=True)
						changes_container.write(change[2])


def prompt_change(app_feature, prompt, changes):
	#update table from mongodb if table is empty
	prompt_doc = {}
	if "log_collection" not in st.session_state:
		st.session_state.log_collection = None
		
	if "URI" in st.secrets["MONGO"]:
		MONGO_URI = st.secrets["MONGO"]["URI"]
		DATABASE_NAME = st.secrets["MONGO"]["DATABASE"]
	else:
		secret_retriever = SecretsRetriever()
		MONGO_URI = secret_retriever("mongo_uri")
		DATABASE_NAME = secret_retriever("mongo_database")

	client = MongoClient(MONGO_URI, tls=True,tlsAllowInvalidCertificates=True)
	db = client[DATABASE_NAME]
	st.session_state.log_collection = db["log_change"]
	#implement the log change in mongo db
 
	prompt_doc = {
		"date": datetime.now(),
		"app_feature": app_feature,  # Using user_id for incremental numbering
		"prompt_version": prompt,  # Store prompts or version of the app
		"changes": changes,
	}
	
	# Insert the user document into MongoDB
	st.session_state.log_collection.insert_one(prompt_doc)
 
	cwd = os.getcwd()
	WORKING_DIRECTORY = os.path.join(cwd, "database")
	if not os.path.exists(WORKING_DIRECTORY):
		os.makedirs(WORKING_DIRECTORY)
	WORKING_DATABASE = os.path.join(WORKING_DIRECTORY , SQL_DB)
	
	conn = sqlite3.connect(WORKING_DATABASE)
	cursor = conn.cursor()

	now = datetime.now()

	# Insert data into Data_Table using preloaded session state value
	cursor.execute('''
		INSERT INTO change_log_table (date, app_feature, prompt, changes)
		VALUES (?, ?, ?, ?)
	''', (now,app_feature, prompt, changes))

	conn.commit()
	pass


def check_if_empty():
	# Update table from MongoDB if table is empty
	if "log_collection" not in st.session_state:
		st.session_state.log_collection = None

	if "URI" in st.secrets["MONGO"]:
		MONGO_URI = st.secrets["MONGO"]["URI"]
		DATABASE_NAME = st.secrets["MONGO"]["DATABASE"]
	else:
		secret_retriever = SecretsRetriever()
		MONGO_URI = secret_retriever("mongo_uri")
		DATABASE_NAME = secret_retriever("mongo_database")

	client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
	db = client[DATABASE_NAME]
	st.session_state.log_collection = db["log_change"]

	# Implement the log change in MongoDB
	cwd = os.getcwd()
	WORKING_DIRECTORY = os.path.join(cwd, "database")
	if not os.path.exists(WORKING_DIRECTORY):
		os.makedirs(WORKING_DIRECTORY)
	WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, SQL_DB)
	conn = sqlite3.connect(WORKING_DATABASE)
	cursor = conn.cursor()

	# Check if the SQLite table is empty
	cursor.execute("SELECT COUNT(*) FROM change_log_table")
	count = cursor.fetchone()[0]

	if count == 0:
		# If the SQLite table is empty, extract data from MongoDB and insert into SQLite
		documents = st.session_state.log_collection.find()
		for doc in documents:
			now = doc["date"]
			app_feature = doc["app_feature"]
			prompt = doc["prompt_version"]
			changes = doc["changes"]

			cursor.execute('''
				INSERT INTO change_log_table (date, app_feature, prompt, changes)
				VALUES (?, ?, ?, ?)
			''', (now, app_feature, prompt, changes))

	conn.commit()
	conn.close()
	pass



def check_update_dates(safa_date_change, acp_date_change, app_date_change):
	current_date = datetime.now()
	two_weeks_ago = current_date - timedelta(weeks=2)
	update_message = ""

	if safa_date_change is not None:
		try:
			safa_date = datetime.strptime(safa_date_change, "%Y-%m-%d %H:%M:%S.%f")
			p_safa_date = safa_date.strftime("%Y-%m-%d")
			if safa_date > two_weeks_ago:
				print("Passed")
				update_message += f"Note the prompt changes for the following: \n 1. ShortAnsFA on {p_safa_date}\n"
		except (ValueError, TypeError):
			pass

	if acp_date_change is not None:
		try:
			acp_date = datetime.strptime(acp_date_change, "%Y-%m-%d %H:%M:%S.%f")
			p_acp_date = acp_date.strftime("%Y-%m-%d")
			print(acp_date)
			if acp_date > two_weeks_ago:
				if update_message:
					update_message += f"2. Authoring CoPilot on {acp_date}\n"
				else:
					update_message += f"Note the prompt changes for following: \n 1. Authoring CoPilot on {p_acp_date}\n"
		except (ValueError, TypeError):
			pass

	if app_date_change is not None:
		try:
			app_date = datetime.strptime(app_date_change, "%Y-%m-%d %H:%M:%S.%f")
			p_app_date = app_date.strftime("%Y-%m-%d")
			print(app_date)
			if app_date > two_weeks_ago:
				update_message += f"\nThe prompt testing tool has been updated on {p_app_date}.\n\n"
		except (ValueError, TypeError):
			pass

	if update_message:
		update_message += "\n\nPlease go to the Application & Prompt Change logs in the side menu to get more details"
	else:
		update_message = "No log or app updates within the last 2 weeks"

	return update_message