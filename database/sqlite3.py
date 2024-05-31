import sqlite3
import os


def get_app_config_condition(condition):
    cwd = os.getcwd()
    WORKING_DIRECTORY = os.path.join(cwd, "database")
    WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, "sqlite3.db")
    conn = sqlite3.connect(WORKING_DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT value 
            FROM app_config_table
            WHERE condition = ?;
        """,
            (condition,),
        )

        result = cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        conn.close()


def insert_condition_record_in_app_config(condition, value):
    cwd = os.getcwd()
    WORKING_DIRECTORY = os.path.join(cwd, "database")
    WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, "sqlite3.db")
    conn = sqlite3.connect(WORKING_DATABASE)
    cursor = conn.cursor()

    # Insert data into Data_Table using preloaded session state value
    cursor.execute(
        """
		INSERT INTO app_config_table (condition, value)
		VALUES (?, ?)
	""",
        (condition, value),
    )

    conn.commit()


def is_app_config_condition_true(condition):
    cwd = os.getcwd()
    WORKING_DIRECTORY = os.path.join(cwd, "database")
    WORKING_DATABASE = os.path.join(WORKING_DIRECTORY, "sqlite3.db")
    conn = sqlite3.connect(WORKING_DATABASE)
    cursor = conn.cursor()
    """Checks if a given condition and its value exist in the app_config_table."""
    try:
        query_result = conn.execute(
            """
			SELECT EXISTS (
				SELECT 1 FROM app_config_table WHERE condition = ? AND value = ?
			);
		""",
            (condition, True),
        ).fetchone()

        if query_result is not None:
            # print(query_result[0])
            return query_result[0] == 1
        else:
            # Handle the case where query_result is None
            conn.close()
            return False
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred: {e}")
        conn.close()
        return False


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
