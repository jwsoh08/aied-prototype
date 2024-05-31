import sqlite3
import os


def initialise_sqlite_db():
    cwd = os.getcwd()
    WORKING_DIRECTORY = os.path.join(cwd, "database")
    if not os.path.exists(WORKING_DIRECTORY):
        os.makedirs(WORKING_DIRECTORY)
    WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, "sqlite3.db")

    conn = sqlite3.connect(WORKING_DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
	CREATE TABLE IF NOT EXISTS Data_Table (
		data_id INTEGER PRIMARY KEY AUTOINCREMENT,
		date TEXT,
		user_id TEXT NOT NULL,
		profile_id TEXT NOT NULL,
		school_id TEXT NOT NULL,
		chatbot_ans TEXT,
		user_prompt TEXT,
		function_name TEXT,
		tokens INTEGER
	)
	
	"""
    )

    cursor.execute(
        """
	CREATE TABLE IF NOT EXISTS app_config_table (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		condition TEXT,
		value TEXT
	)
	"""
    )

    cursor.execute(
        """
	CREATE TABLE IF NOT EXISTS change_log_table (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		date TEXT,
		app_feature TEXT,
		prompt TEXT,
		changes TEXT
	
	)
	"""
    )

    conn.commit()
    conn.close()
