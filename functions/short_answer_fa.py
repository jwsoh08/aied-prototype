from datetime import datetime
import json

import streamlit as st
import streamlit_antd_components as sac
import pandas as pd

from openai import OpenAI
import anthropic

from utils.secrets_reader import return_openai_key, return_claude_key

from config.settings import SAFA_CONFIG, SAFA_MODEL_LIST, RUBRICS, CLASS_LEVELS_SINGAPORE, SUBJECTS_SINGAPORE
from constants import SA, AD


def clear_question_cache():
	st.session_state.pass_level = 0
	st.session_state.pass_subject = 0
	st.session_state.question_prompt = "Enter your question"
	st.session_state.suggested_answer_prompt = "Enter your suggested answer"
	st.session_state.rubrics_prompt = RUBRICS
	st.session_state.total_marks_prompt = 0
	st.session_state.student_answer_prompt = "Enter your student's answer"
	st.session_state.seed_number = 1
      

def create_rubric_interface():
	# Set the starting ID for dimensions
	dimension_id_start = 21000

	# Set the title for the page
	st.title("Rubrics Creator")

	# Initialize a form for the rubric
	with st.container(border=True):
		title = st.text_input(":red[Title]")

		st.divider()
		
		# Get the number of band descriptors and criterions from the user
		c1, c2 = st.columns([1,1])
		with c1:
			number_of_band_descriptors = st.number_input(":green[Number of Band Descriptors]", min_value=1, value=3, step=1)
		with c2:
			number_of_criterions = st.number_input(":blue[Number of Criterions]", min_value=1, value=1, step=1)
		
		st.divider()
		# Placeholder for storing band descriptor inputs
		band_descriptors = []

		# Collect band descriptor titles
		band_descriptors_cols = st.columns(number_of_band_descriptors)
		for k, single_col in enumerate(band_descriptors_cols):
			with single_col:
				band_descriptor = st.text_input(f":green[Band Descriptor {k+1}]", value=f"Band {k+1}", key=f"band_descriptor_{k+1}")
				band_descriptors.append(band_descriptor)

		# Initialize list to hold all dimension data
		dimensions_data = []

		# Loop to create input fields for each criterion
		for i in range(number_of_criterions):
			with st.expander(f":blue[Criterion {i + 1}]"):
				criterion = st.text_input(f":blue[Enter criterion {i + 1} to be assessed]", key=f"dimension_{i+1}_criteria")

				# Initialize variables to hold descriptions and marks for each criterion
				descriptions = []

				# Create a new column for each descriptor
				descriptor_cols = st.columns(number_of_band_descriptors)

				# Dynamic input fields for descriptions and their marks within each criterion
				for j, descriptor_col in enumerate(descriptor_cols):
					with descriptor_col:
						mark = st.number_input(f"Mark Range for band {j+1}", min_value=0, step=1, key=f"dimension_{i+1}_mark_{j+1}")
						description = st.text_area(f"Description for band {j+1}", key=f"dimension_{i+1}_description_{j+1}")

						# Check if the current descriptor is the last one
						if j == len(descriptor_cols) - 1:
							descriptions.append(f"– up to {mark} – {description}.")
						else:
							descriptions.append(f"– up to {mark} – {description},")
						
						total_marks = mark  # Set total_marks to the current mark, which will end up being the last one's mark


 
 				# Add dimension data to dimensions_data list
				dimensions_data.append({
					"id": dimension_id_start + i,
					"criteria": criterion,
					"descriptions": descriptions,
					"total_marks": total_marks
	 
				})
	
		# Button to submit form
		submitted = st.button("Submit Rubric")
		if submitted:
			st.write("Rubric Submitted!")
			# Process and display the input data
			total_marks = 0
			rubrics_output = ""
			for dimension in dimensions_data:
				dimension_output = f"Id for this dimension: {dimension['id']}. Dimension Criteria: {dimension['criteria']}" + " ".join(dimension['descriptions']) + f" Maximum mark for this dimension: {dimension['total_marks']}.  "
				rubrics_output += dimension_output
				total_marks += dimension['total_marks']
			return rubrics_output, total_marks
	return "", 0


def parse_claude_json_data(data):
	try:
		# Navigate through the nested structure to find the relevant information
		for content_item in getattr(data, 'content', []):
			if isinstance(content_item, dict) and content_item.get('type') == 'tool_use':
				input_data = content_item.get('input', {})
				marks = input_data.get('answer_scheme_marks')
				feedback = input_data.get('general_feedback')
				return marks, feedback
		# Return None if the required information is not found
		return None, None
	except json.JSONDecodeError:
		st.error("Invalid JSON format.")
		return None, None
	except Exception as e:
		st.error(f"An error occurred: {e}")
		return None, None


def prompt_template(prompt_design, level, subject, question, suggested_answer, student_answer, final_rubrics, total_marks):
	# Provide a default value for Rubrics if final_rubrics is None
	if final_rubrics is None:
		final_rubrics = ""
	
	# Now, Rubrics is always included in variables, so it won't raise KeyError
	variables = {
		"Model answer": suggested_answer, 
		"Level": level, 
		"Subject": subject, 
		"Question": question, 
		"Student's response": student_answer, 
		"Marks": total_marks, 
		"Rubrics marking": final_rubrics
	}
	
	return prompt_design.format(**variables)


def tool_function():
	st.write(":red[Functional tools for JSON function calling:]")

	if "j_tools_format" not in st.session_state:
		st.session_state.j_tools_format = st.session_state.safa_openai_tools_production

	# Create a mapping between format names and their corresponding session state values
	SAFA_TOOLS_OPTIONS = {
		# "Production Tools": st.session_state.tools_production,
		# "Development Format 1": st.session_state.tools_format_1,
		# "Development Format 2": st.session_state.tools_format_2,
  		# "Development Format 3": st.session_state.tools_format_3,
	
		"SAFA OpenAI Tools Production": st.session_state.safa_openai_tools_production,
		"SAFA OpenAI Tools Development Format 1": st.session_state.safa_openai_tools_development_format_1,
		"SAFA OpenAI Tools Development Format 2": st.session_state.safa_openai_tools_development_format_2,
		"SAFA OpenAI Tools Development Format 3": st.session_state.safa_openai_tools_development_format_3,
  		"SAFA Claude Tools Development Format 1": st.session_state.safa_claude_tools_development_format_1,
	}

	
	# Let the user select a tools format by name
	selected_format_name = st.selectbox("Select your functional tools format: (JSON)", tuple(SAFA_TOOLS_OPTIONS.keys()))

	# Set the j_tools_format to the corresponding session state value based on the selected name
	st.session_state.j_tools_format = SAFA_TOOLS_OPTIONS[selected_format_name]
	# Display the selected tools format in a text area for editing
	#st.markdown(j_tools_format, unsafe_allow_html=True)
	if st.session_state.user["profile_id"] == SA or st.session_state.user["profile_id"] == AD:
		if st.button(":red[Click here to edit the JSON function tools content]"):
			tool_dialog()
	with st.expander("Click to show the function tools JSON format"):
		st.code(st.session_state.j_tools_format, language="json")
	#st.code(j_tools_format, language="json")
	st.divider()
	return st.session_state.j_tools_format


def check_column_values(df, required_columns):
	 # Convert required columns to lowercase
	required_columns = [col.lower() for col in required_columns]
	
	missing_columns = [col for col in required_columns if col not in df.columns]
	if missing_columns:
		st.error(f"Missing columns: {', '.join(missing_columns)}")
		return False
	else:
		st.session_state.prompt_df = df.dropna(subset=[col for col in required_columns if col != 'rubrics'])
		return True
	

def short_answer_fa_interface(json_call):
	question = None
	suggested_answer = ""
	total_marks = None
	rubrics_total_marks = 0
	student_answer = None
 
	if "prompt_design" not in st.session_state:
		st.session_state.prompt_design = None
	
	c1, c2, c3 = st.columns([1,1,1])
	with c1:
		pass_level = st.selectbox("Select your level:", options=CLASS_LEVELS_SINGAPORE, index=st.session_state.pass_level)
	with c2:
		pass_subject = st.selectbox("Selecte your subject:", options=SUBJECTS_SINGAPORE, index=st.session_state.pass_subject)
	question = st.text_area("Enter your Question:", value=st.session_state.question_prompt, max_chars=5000, height=100)
	suggested_answer = st.text_area("Enter your Suggested Answer:", value=st.session_state.suggested_answer_prompt, max_chars=5000, height=200)
	total_marks = 0
	st.divider()
	if st.checkbox("## :blue[Add Rubrics]", value=True):
		# calling the rubrics function
		#rubrics = """\nDimension: Grammar – 3 to 5 – Grammar does not have mistakes or minor mistakes, Maximum mark for this dimension: 5. Id for this dimension: 21056.\nDimension: Completeness – 3 to 4 – Answer has expressed details, Maximum mark for this dimension: 4. Id for this dimension: 21057.\n\n"""
		st.session_state.rubrics_prompt, rubrics_total_marks = create_rubric_interface()
		if st.session_state.user["profile_id"] == SA or st.session_state.user["profile_id"] == AD:
			#st.write(st.session_state.rubrics_prompt)
			# if st.button(":red[Click here to Edit/Paste the Rubrics]"):
			# 	rubrics_dialog()
			with st.popover(":red[Edit Rubrics]"):
				st.session_state.rubrics_prompt = st.text_area("Rubrics", value=st.session_state.rubrics_prompt, max_chars=5000, height=200)
		st.code(st.session_state.rubrics_prompt, line_numbers=True, language='html')
		#st.write("Total Marks from Rubrics:", total_marks)
	st.divider()
	total_marks = st.number_input("Enter the total marks for this question:", value=rubrics_total_marks, max_value=100, step=1)
	student_answer = st.text_area("Enter your Student's response:", value=st.session_state.student_answer_prompt, max_chars=10000, height=300)
	st.divider()
	if st.button("Clear and reset above text fields"):
		clear_question_cache()
	st.divider()
	# Create a mapping between prompt names and their corresponding session state values
	SAFA_PROMPT_OPTIONS = {
		"SAFA OpenAI Production Prompt": st.session_state.safa_openai_production_prompt,
		"SAFA OpenAI Development Prompt 1": st.session_state.safa_openai_development_prompt_1,
		"SAFA OpenAI Development Prompt 2": st.session_state.safa_openai_development_prompt_2,
		"SAFA OpenAI Development Prompt 3": st.session_state.safa_openai_development_prompt_3,
		"SAFA Claude Development Prompt 1": st.session_state.safa_claude_development_prompt_1,

		
	}

	# Let the user select a prompt by name
	selected_prompt_name = st.selectbox("Select your prompt design:", tuple(SAFA_PROMPT_OPTIONS.keys()))

	# Set the select_prompt to the corresponding session state value based on the selected name
	select_prompt = SAFA_PROMPT_OPTIONS[selected_prompt_name]

	# Display the selected prompt
	with st.expander("Click to show the blank prompt templates"):
		st.code(select_prompt, language='html')
	# select_prompt = st.selectbox("Select your prompt design:", (st.session_state.production_prompt, st.session_state.development_prompt_1, st.session_state.development_prompt_2, st.session_state.development_prompt_3, st.session_state.development_prompt_4, ))
	# st.write(select_prompt)
	st.divider()

	if suggested_answer == None:
		suggested_answer = ""
	
	if question and total_marks:
		st.session_state.prompt_design = prompt_template(select_prompt, pass_level, pass_subject, question, suggested_answer, student_answer, st.session_state.rubrics_prompt, total_marks)
		if st.session_state.user["profile_id"] == SA or st.session_state.user["profile_id"] == AD:
			if st.button(":red[Click here to edit the Prompt Design content]"):
				prompt_dialog()
		st.code(st.session_state.prompt_design, line_numbers=True, language='html')
	else:
		st.error("Content prompt cannot be generated without the question, student answer and total marks")

	st.divider()
	st.session_state.j_tools_format = tool_function()

	if json_call:
		if st.button("Submit Content Prompt for JSON call", key = 1):
			if not st.session_state.prompt_design:
				st.error("Content prompt cannot be empty")
				return False
			else:
				st.session_state.pass_level = CLASS_LEVELS_SINGAPORE.index(pass_level)
				st.session_state.pass_subject = SUBJECTS_SINGAPORE.index(pass_subject)
				st.session_state.question_prompt = question
				st.session_state.suggested_answer_prompt = suggested_answer
				#st.session_state.rubrics_prompt = final_rubrics
				st.session_state.total_marks_prompt = total_marks
				st.session_state.student_answer_prompt = student_answer
				#print("Prompt Design:", prompt_design)
				return st.session_state.rubrics_prompt, st.session_state.prompt_design
	else:
		if st.button("Submit Content Prompt for API call", key = 2):
			if not st.session_state.prompt_design:
				st.error("Content prompt cannot be empty")
				return False
			else:
				st.session_state.pass_level = CLASS_LEVELS_SINGAPORE.index(pass_level)
				st.session_state.pass_subject = SUBJECTS_SINGAPORE.index(pass_subject)
				st.session_state.question_prompt = question
				st.session_state.suggested_answer_prompt = suggested_answer
				#st.session_state.rubrics_prompt = final_rubrics
				st.session_state.total_marks_prompt = total_marks
				st.session_state.student_answer_prompt = student_answer
				#print("Prompt Design:", prompt_design)
				return st.session_state.rubrics_prompt, st.session_state.prompt_design


def parse_claude_json_rubrics_data(data):
	#print(data)
	try:
		content_list = getattr(data, 'content', [])
		if content_list:
			tool_use_block = content_list[0]
			if isinstance(tool_use_block, dict) and tool_use_block.get('type') == 'tool_use':
				input_data = tool_use_block.get('input', {})
				marks = input_data.get('answer_scheme_marks')
				feedback = input_data.get('general_feedback')
				rubrics = input_data.get('rubrics', [])
				return marks, feedback, rubrics
	except Exception as e:
		st.error(f"No information available to display. Error: {e}")
	return None, None, None


def parse_json_rubrics_data(data):
	try:
		for choice in getattr(data, 'choices', []):
			for tool_call in getattr(choice.message, 'tool_calls', []):
				if getattr(tool_call.function, 'name', '') == 'get_marks_feedback_and_rubrics':
					arguments = json.loads(getattr(tool_call.function, 'arguments', '{}'))
					marks = arguments.get('marks') if 'marks' in arguments else arguments.get('answer_scheme_marks')
					feedback = arguments.get('feedback') if 'feedback' in arguments else arguments.get('general_feedback')
					rubrics = arguments.get('rubrics')
					return marks, feedback, rubrics
	except:
		st.error("No information available to display.")
	return None, None, None


def parse_json_data(data):
	try:
		# Navigate through the nested structure to find the relevant information
		for choice in getattr(data, 'choices', []):
			for tool_call in getattr(choice.message, 'tool_calls', []):
				function = getattr(tool_call, 'function', {})
				if getattr(function, 'name', '') == 'get_marks_feedback_and_rubrics':
					# Parsing the 'arguments' attribute from the function
					arguments = json.loads(getattr(function, 'arguments', '{}'))
					marks = arguments.get('marks') if 'marks' in arguments else arguments.get('answer_scheme_marks')
					feedback = arguments.get('feedback') if 'feedback' in arguments else arguments.get('general_feedback')
					return marks, feedback

		# Return None if the required information is not found
		return None, None
	except json.JSONDecodeError:
		st.error("Invalid JSON format.")
		return None, None
	except Exception as e:
		st.error(f"An error occurred: {e}")
		return None, None


def api_call(full_prompt, model):
	client = OpenAI(
		# defaults to os.environ.get("OPENAI_API_KEY")
		api_key=return_openai_key()	
	)
	#openai.api_key = return_openai_key()
	#os.environ["OPENAI_API_KEY"] = return_openai_key()
	st.title("Api Call")
	#MODEL = "gpt-3.5-turbo"
	#print(type(full_prompt))
	#full_prompt = str(full_prompt)
	with st.status("Calling the OpenAI API..."):
		start_time = datetime.now()
		if st.session_state.use_seed:
			response = client.chat.completions.create(
				model=model,
				messages=[
					{"role": "user", "content": full_prompt},
				],
				temperature=st.session_state.default_temp, #settings option
				presence_penalty=st.session_state.default_presence_penalty, #settings option
				frequency_penalty=st.session_state.default_frequency_penalty, #settings option
				top_p = st.session_state.default_top_p, #settings option
				seed = st.session_state.default_seed_number, #settings option
			)
		else:
			response = client.chat.completions.create(
				model=model,
				messages=[
					{"role": "user", "content": full_prompt},
				],
				temperature=st.session_state.default_temp, #settings option
				presence_penalty=st.session_state.default_presence_penalty, #settings option
				frequency_penalty=st.session_state.default_frequency_penalty, #settings option
				top_p = st.session_state.default_top_p, #settings option
			)
		st.markdown("**This is the extracted response:**")
		st.write(response.choices[0].message.content)
		completion_tokens = response.usage.completion_tokens
		prompt_tokens = response.usage.prompt_tokens
		total_tokens = response.usage.total_tokens
		end_time = datetime.now()  # Capture the end time after processing
		duration = (end_time - start_time).total_seconds()  # Calculate duration in seconds
		if st.session_state.use_seed:
			st.write(f"Seed Number: {st.session_state.default_seed_number}")
		else:
			st.write("Seed Number: None")
		st.write(f"Completion Tokens: {completion_tokens}")
		st.write(f"Prompt Tokens: {prompt_tokens}")
		st.write(f"Total Tokens: {total_tokens}")
		st.write(f"Processing time: {duration} seconds")


def claude_api_call_json(full_prompt, model, tools, rubrics):
	#full_prompt = str(full_prompt)
	#print("Claude",full_prompt)
	start_time = datetime.now()
	client = anthropic.Anthropic(api_key=return_claude_key())
	#openai.api_key = return_openai_key()
	#os.environ["OPENAI_API_KEY"] = return_openai_key()
	st.subheader("Api Call with JSON")
	#MODEL = "gpt-3.5-turbo"
	with st.status("Calling the Claude API..."):
		response = client.beta.tools.messages.create(
		model=model,
		max_tokens=st.session_state.default_max_tokens,
		top_p=st.session_state.default_top_p,
		temperature=st.session_state.default_temp,
		tools = tools,
		messages=[
			{
				"role": "user", 
				"content": [
							{"type" : "text", "text": full_prompt},
							{"type": "text", "text": "Use 'get_marks_feedback_and_rubrics' to extract marks, feedback and rubrics."},
						],	
			},
			],
		) #.content[0].text
		end_time = datetime.now()  # Capture the end time after processing
		duration = (end_time - start_time).total_seconds()  # Calculate duration in seconds	
		st.markdown("**This is the extracted response:**")
		st.write(response)

		if rubrics != None:
			marks, feedback, rubrics = parse_claude_json_rubrics_data(response)
			if marks is not None and feedback is not None and rubrics is not None:
				
				c1, c2, c3 = st.columns([2,1,3])
				
				with c1:
					st.subheader('Feedback')
					st.write(feedback)
				
				with c2:
					st.subheader('Marks')
					st.write(marks)

				with c3:
					st.subheader('Rubrics Feedback')
					d1, d2, d3 = st.columns([1,1,4])
					for rubric in rubrics:
						with d1:
							st.write(f"Dimension: {rubric['dimensionId']}")
						with d2:	
							st.write(f"Marks: {rubric['dimension_marks']}")
						with d3:
							st.write(f"Feedback: {rubric['rubrics_feedback']}")
			else:
				st.write('No data available to display.')
		else: #no rubrics
			marks, feedback = parse_claude_json_data(response)
			if marks is not None and feedback is not None:
				e1, e2 = st.columns([1,3])
				with e1:
					st.subheader('Marks')
					st.write(marks)
				with e2:
					st.subheader('Feedback')
					st.write(feedback)
				pass

		# completion_tokens = response.usage.completion_tokens
		# prompt_tokens = response.usage.prompt_tokens
		# total_tokens = response.usage.total_tokens
		st.divider()
		input_tokens = response.usage.input_tokens
		output_tokens = response.usage.output_tokens
		st.write(f"Input Tokens: {input_tokens}, Output Tokens: {output_tokens}")


def api_call_json(full_prompt, model, tools, rubrics):
	#full_prompt = str(full_prompt)
	#print("OpenAI:",full_prompt)
	print("rubrics", rubrics)
	start_time = datetime.now()
	client = OpenAI(
		# defaults to os.environ.get("OPENAI_API_KEY")
		api_key=return_openai_key()	
	)
	#openai.api_key = return_openai_key()
	#os.environ["OPENAI_API_KEY"] = return_openai_key()
	st.subheader("Api Call with JSON")
	#MODEL = "gpt-3.5-turbo"
	with st.status("Calling the OpenAI API..."):
		if st.session_state.use_seed:
			response = client.chat.completions.create(
				model=model,
				messages=[
				#{"role": "system", "content": "You are a helpful assistant designed to output JSON."}, #system prompt
				{"role": "user", "content": full_prompt},
				],
				#response_format={ "type": "json_object" }, #response format
				tools = tools,
				tool_choice = {"type": "function", "function": {"name": "get_marks_feedback_and_rubrics"}},
				temperature=st.session_state.default_temp, #settings option
				presence_penalty=st.session_state.default_presence_penalty, #settings option
				frequency_penalty=st.session_state.default_frequency_penalty, #settings option
				top_p = st.session_state.default_top_p, #settings option
				seed = st.session_state.default_seed_number, #settings option
				max_tokens=st.session_state.default_max_tokens, #settings option
			)
		else:
			response = client.chat.completions.create(
				model=model,
				messages=[
				#{"role": "system", "content": "You are a helpful assistant designed to output JSON."}, #system prompt
				{"role": "user", "content": full_prompt},
				],
				#response_format={ "type": "json_object" }, #response format
				tools = tools,
				tool_choice = {"type": "function", "function": {"name": "get_marks_feedback_and_rubrics"}},
				temperature=st.session_state.default_temp, #settings option
				presence_penalty=st.session_state.default_presence_penalty, #settings option
				frequency_penalty=st.session_state.default_frequency_penalty, #settings option
				top_p = st.session_state.default_top_p, #settings option
				max_tokens=st.session_state.default_max_tokens, #settings option
			)
		end_time = datetime.now()  # Capture the end time after processing
		duration = (end_time - start_time).total_seconds()  # Calculate duration in seconds	
		st.markdown("**This is the extracted response:**")
		st.write(response)

		if rubrics != None:
			print("Rubrics:", rubrics)
			marks, feedback, rubrics = parse_json_rubrics_data(response)
			if marks is not None and feedback is not None and rubrics is not None:
				
				c1, c2, c3 = st.columns([2,1,3])
				
				with c1:
					st.subheader('Feedback')
					st.write(feedback)
				
				with c2:
					st.subheader('Marks')
					st.write(marks)

				with c3:
					st.subheader('Rubrics Feedback')
					d1, d2, d3 = st.columns([1,1,4])
					for rubric in rubrics:
						with d1:
							st.write(f"Dimension: {rubric['dimensionId']}")
						with d2:	
							st.write(f"Marks: {rubric['dimension_marks']}")
						with d3:
							st.write(f"Feedback: {rubric['rubrics_feedback']}")
			else:
				st.write('No data available to display.')
		else: #no rubrics
			marks, feedback = parse_json_data(response)
			if marks is not None and feedback is not None:
				e1, e2 = st.columns([1,3])
				with e1:
					st.subheader('Marks')
					st.write(marks)
				with e2:
					st.subheader('Feedback')
					st.write(feedback)
				pass

		completion_tokens = response.usage.completion_tokens
		prompt_tokens = response.usage.prompt_tokens
		total_tokens = response.usage.total_tokens
		st.divider()
		if st.session_state.use_seed:
			st.write(f"Seed Number: {st.session_state.default_seed_number}")
		else:
			st.write("Seed Number: None")
		st.write(f"Completion Tokens: {completion_tokens}")
		st.write(f"Prompt Tokens: {prompt_tokens}")
		st.write(f"Total Tokens: {total_tokens}")
		st.write(f"Processing time: {duration} seconds")


def api_batch_call_json(full_prompt, model, tools, rubrics):
	#openai.api_key = return_openai_key()
	#os.environ["OPENAI_API_KEY"] = return_openai_key()
	#st.title("Api Call with JSON")
	#full_prompt = str(full_prompt)
	start_time = datetime.now()
	client = OpenAI(
		# defaults to os.environ.get("OPENAI_API_KEY")
		api_key=return_openai_key()	
	)

	if st.session_state.use_seed:
		response = client.chat.completions.create(
			model=model,
			messages=[
				#{"role": "system", "content": "You are a helpful assistant designed to output JSON."}, #system prompt
				{"role": "user", "content": full_prompt},
			],
			#response_format={ "type": "json_object" }, #response format
			tools=tools,
			tool_choice={"type": "function", "function": {"name": "get_marks_feedback_and_rubrics"}},
			temperature=st.session_state.default_temp,
			presence_penalty=st.session_state.default_presence_penalty,
			frequency_penalty=st.session_state.default_frequency_penalty,
			top_p=st.session_state.default_top_p,
			max_tokens=st.session_state.default_max_tokens,
			seed=st.session_state.default_seed_number,
		)
	else:
		response = client.chat.completions.create(
			model=model,
			messages=[
				#{"role": "system", "content": "You are a helpful assistant designed to output JSON."}, #system prompt
				{"role": "user", "content": full_prompt},
			],
			#response_format={ "type": "json_object" }, #response format
			tools=tools,
			tool_choice={"type": "function", "function": {"name": "get_marks_feedback_and_rubrics"}},
			temperature=st.session_state.default_temp,
			presence_penalty=st.session_state.default_presence_penalty,
			frequency_penalty=st.session_state.default_frequency_penalty,
			top_p=st.session_state.default_top_p,
			max_tokens=st.session_state.default_max_tokens,
		)

	# Initialize variables with NA or None
	marks = feedback = extracted_rubrics = 'NA'
	completion_tokens = prompt_tokens = total_tokens = 0

	# Extract response data
	if response:  # Check if response is valid
		end_time = datetime.now()  # Capture the end time after processing
		duration = (end_time - start_time).total_seconds()  # Calculate duration in seconds
		if rubrics is not None:
			marks, feedback, extracted_rubrics = parse_json_rubrics_data(response)
		else:
			marks, feedback = parse_json_data(response)
		
		# Ensure extracted_rubrics is always a list
		# if not isinstance(extracted_rubrics, list):
		# 	extracted_rubrics = [extracted_rubrics] if extracted_rubrics else []  

		# Check for token counts
		if hasattr(response.usage, 'completion_tokens'):
			completion_tokens = response.usage.completion_tokens
		if hasattr(response.usage, 'prompt_tokens'):
			prompt_tokens = response.usage.prompt_tokens
		if hasattr(response.usage, 'total_tokens'):
			total_tokens = response.usage.total_tokens
	
	response_str = str(response)

	return response_str, marks, feedback, extracted_rubrics, completion_tokens, prompt_tokens, total_tokens, duration

# def parse_json_rubrics_data(data):
# 	# Assuming data is an instance of ChatCompletion with an attribute 'choices' that is a list
# 	try:
# 		for choice in getattr(data, 'choices', []):
# 			# Assuming message is an attribute of choice which is an instance with an attribute 'tool_calls'
# 			for tool_call in getattr(choice.message, 'tool_calls', []):
# 				# Assuming function is an attribute of tool_call which is an instance with an attribute 'name'
# 				if getattr(tool_call.function, 'name', '') == 'get_marks_feedback_and_rubrics':
# 					# Now, assuming arguments is a JSON string stored in an attribute of function
# 					arguments = json.loads(getattr(tool_call.function, 'arguments', '{}'))
# 					marks = arguments.get('marks')
# 					feedback = arguments.get('feedback')
# 					rubrics = arguments.get('rubrics')
# 					return marks, feedback, rubrics
# 	except:
# 		st.error("No information available to display.")
# 		return None, None, None


def batch_call(model, df, json_call):
	st.divider()
	st.subheader("Please select your content prompt:")
	# Create a mapping between prompt names and their corresponding session state values
	SAFA_PROMPT_OPTIONS = {
		# "Production Prompt": st.session_state.production_prompt,
		# "Development Prompt 1": st.session_state.development_prompt_1,
		# "Development Prompt 2": st.session_state.development_prompt_2,
		# "Development Prompt 3": st.session_state.development_prompt_3,

		"SAFA OpenAI Production Prompt": st.session_state.safa_openai_production_prompt,
		"SAFA OpenAI Development Prompt 1": st.session_state.safa_openai_development_prompt_1,
		"SAFA OpenAI Development Prompt 2": st.session_state.safa_openai_development_prompt_2,
		"SAFA OpenAI Development Prompt 3": st.session_state.safa_openai_development_prompt_3,
		"SAFA Claude Development Prompt 1": st.session_state.safa_claude_development_prompt_1,
	}

	# Let the user select a prompt by name
	selected_prompt_name = st.selectbox("Select your prompt design:", tuple(SAFA_PROMPT_OPTIONS.keys()))

	# Set the select_prompt to the corresponding session state value based on the selected name
	select_prompt = SAFA_PROMPT_OPTIONS[selected_prompt_name]
	with st.expander("Click to show the blank prompt templates"):
		st.code(select_prompt, language='html')
	# Display the selected prompt
	#st.write(select_prompt)
	# select_prompt = st.selectbox("Select your prompt design:", (st.session_state.production_prompt, st.session_state.development_prompt_1, st.session_state.development_prompt_2, st.session_state.development_prompt_3, st.session_state.development_prompt_4, ))
	# st.write(select_prompt)
	
	if json_call:
		st.divider()
		st.session_state.j_tools_format = tool_function()
		tools = json.loads(st.session_state.j_tools_format)
	
	if st.button("Execute Batch Call"):
		with st.status("Batch processing Prompts with OpenAI API..."):
			progress_bar = st.progress(0)
			total_rows = len(df)
			result_rows = []
			for index, row in df.iterrows():
				# Update the progress bar
				progress = (index + 1) / total_rows
				progress_bar.progress(min(progress, 1.0))
				subject = row['subject']
				level = row['level']
				question = row['question']
				suggested_answer = row['suggested_answer'] if pd.notna(row['suggested_answer']) else ""
				student_answer = row['student_answer'] if pd.notna(row['student_answer']) else ""
				total_marks = row['total_marks'] if pd.notna(row['total_marks']) else ""
				final_rubrics = row['rubrics'] if pd.notna(row['rubrics']) else None

				if question and suggested_answer and total_marks:
					complete_prompt = prompt_template(select_prompt, level, subject, question, suggested_answer, student_answer, final_rubrics, total_marks)

				if json_call:
					if complete_prompt:
				
						#api_call_json(complete_prompt, model, tools, final_rubrics)
						# if model.startswith("claude"):
						# 	response, completion_tokens, prompt_tokens, total_tokens, duration = claude_api_batch_call_json(complete_prompt, model, tools, final_rubrics)
						# else:
						response, marks, feedback, rubrics, completion_tokens, prompt_tokens, total_tokens, duration = api_batch_call_json(complete_prompt, model, tools, final_rubrics)
						rubrics_str = json.dumps(rubrics) if isinstance(rubrics, (list, dict)) else str(rubrics)
						
						row['generated_feedback'] = feedback
						row['generated_marks'] = marks
						row['rubrics_feedback'] = rubrics_str
						row['duration'] = duration
						if st.session_state.use_seed:
							row['seed_number'] = st.session_state.default_seed_number
						else:
							row['seed_number'] = None
						row['completion_tokens'] = completion_tokens
						row['prompt_tokens'] = prompt_tokens
						row['total_tokens'] = total_tokens
						# Including session state values in the row
						row['session_temp'] = st.session_state.default_temp
						row['session_presence_penalty'] = st.session_state.default_presence_penalty
						row['session_frequency_penalty'] = st.session_state.default_frequency_penalty
						row['session_top_p'] = st.session_state.default_top_p
						row['session_max_tokens'] = st.session_state.default_max_tokens
						row['generated_response'] = response
						result_rows.append(row)
					
			updated_df = pd.DataFrame(result_rows)
			st.session_state.prompt_df = updated_df


def upload_csv():
	# Upload CSV file using st.file_uploader
	uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
	if "api_key" not in st.session_state:
		st.session_state.api_key = return_openai_key()
	#st.session_state.prompt_history = []
	if "prompt_df" not in st.session_state:
		st.session_state.prompt_df = None

	if uploaded_file is not None:
		try:
			df = pd.read_csv(uploaded_file)

			# Check if the number of rows is greater than 300
			if len(df) > 300:
				# Truncate the DataFrame to 300 rows
				df = df.head(300)

				# Display a warning
				st.warning("The uploaded CSV file contains more than 300 rows. It has been truncated to the first 300 rows.")

			st.session_state.prompt_df = df

		except Exception as e:
			st.write("There was an error processing the CSV file.")
			st.write(e)

	# Check if the DataFrame exists before calling st.data_editor
	if st.session_state.prompt_df is not None:
		st.session_state.prompt_df.columns = st.session_state.prompt_df.columns.str.lower()
		st.session_state.prompt_df = st.data_editor(st.session_state.prompt_df, num_rows="dynamic", height=500)
		return True
	else:
		return False


def chatbot_settings():
    if "seed_number" not in st.session_state:
        st.session_state.default_seed_number = 1
    if "use_seed" not in st.session_state:
        st.session_state.use_seed = False
    if st.checkbox("Revert to ShortAns FA default settings"):
        st.session_state.default_temp = SAFA_CONFIG["default_temp"]
        st.session_state.default_presence_penalty = SAFA_CONFIG[
            "default_presence_penalty"
        ]
        st.session_state.default_frequency_penalty = SAFA_CONFIG[
            "default_frequency_penalty"
        ]
        st.session_state.default_top_p = SAFA_CONFIG["default_top_p"]
        st.session_state.default_max_tokens = SAFA_CONFIG["default_max_tokens"]
        st.session_state.default_seed_number = 1

    temp = st.number_input(
        "Temperature",
        value=st.session_state.default_temp,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    )
    presence_penalty = st.number_input(
        "Presence Penalty (OpenAI LLM)",
        value=st.session_state.default_presence_penalty,
        min_value=-2.0,
        max_value=2.0,
        step=0.1,
    )
    frequency_penalty = st.number_input(
        "Frequency Penalty (OpenAI LLM)",
        value=st.session_state.default_frequency_penalty,
        min_value=-2.0,
        max_value=2.0,
        step=0.1,
    )
    top_p = st.number_input(
        "Top P",
        value=st.session_state.default_top_p,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    )
    max_tokens = st.number_input(
        "Max Tokens",
        value=st.session_state.default_max_tokens,
        min_value=0,
        max_value=4000,
        step=10,
    )
    if st.checkbox("Use Seed Number"):
        st.session_state.use_seed = True
        seed_number = st.number_input(
            "Seed Number (OpenAI LLM)",
            value=st.session_state.default_seed_number,
            min_value=0,
            max_value=100000,
            step=1,
        )
    else:
        st.session_state.use_seed = False
        seed_number = 1

    if st.button("Update Chatbot Settings", key=3):
        st.session_state.default_temp = temp
        st.session_state.default_presence_penalty = presence_penalty
        st.session_state.default_frequency_penalty = frequency_penalty
        st.session_state.default_top_p = top_p
        st.session_state.default_max_tokens = max_tokens
        st.session_state.default_seed_number = seed_number
        st.session_state.change_default = True


def leniency_settings():
    # Leniency settings: low, medium, high
    leniency_options = ["Low", "Medium", "High", "Other Settings"]

    # Determine the index of the current leniency based on st.session_state.default_temp
    if st.session_state.default_temp == 0.0:
        current_index = 0
    elif st.session_state.default_temp == 0.1:
        current_index = 1
    elif st.session_state.default_temp == 0.2:
        current_index = 2
    else:
        current_index = 3

    leniency = st.selectbox("Select Leniency", leniency_options, index=current_index)

    if leniency == "Low":
        st.session_state.default_temp = 0.0
    elif leniency == "Medium":
        st.session_state.default_temp = 0.1
    elif leniency == "High":
        # Double check with SLS team for the high leniency
        st.session_state.default_temp = 0.2


@st.experimental_dialog("Update the ShortAns FA Prompt")
def prompt_dialog():
	prompt_design = st.text_area("Prompt Design", value=st.session_state.prompt_design, max_chars=5000, height=500)
	if st.button("Update the prompt"):
		st.session_state.prompt_design = prompt_design
		st.rerun()


@st.experimental_dialog("Update the Function Tools")
def tool_dialog():
	func_tool = st.text_area("Function Tools", value=st.session_state.j_tools_format, max_chars=5000, height=500)
	if st.button("Update the prompt"):
		st.session_state.j_tools_format = func_tool
		st.rerun()



def prompt_analyser():
    if "pass_level" not in st.session_state:
        st.session_state.pass_level = 0
    if "pass_subject" not in st.session_state:
        st.session_state.pass_subject = 0
    if "question_prompt" not in st.session_state:
        st.session_state.question_prompt = "Enter your question"
    if "suggested_answer_prompt" not in st.session_state:
        st.session_state.suggested_answer_prompt = "Enter your suggested answer"
    if "rubrics_prompt" not in st.session_state:
        st.session_state.rubrics_prompt = RUBRICS
    if "total_marks_prompt" not in st.session_state:
        st.session_state.total_marks_prompt = 2
    if "student_answer_prompt" not in st.session_state:
        st.session_state.student_answer_prompt = "Enter your student's answer"
    if "change_default_SAFA" not in st.session_state:
        st.session_state.change_default_SAFA = False
        st.session_state.default_temp = SAFA_CONFIG["default_temp"]
        st.session_state.default_presence_penalty = SAFA_CONFIG[
            "default_presence_penalty"
        ]
        st.session_state.default_frequency_penalty = SAFA_CONFIG[
            "default_frequency_penalty"
        ]
        st.session_state.default_top_p = SAFA_CONFIG["default_top_p"]
        st.session_state.default_max_tokens = SAFA_CONFIG["default_max_tokens"]
        st.session_state.default_seed_number = 1
        st.session_state.default_llm_model = SAFA_CONFIG["default_llm_model"]

    options = sac.chip(
        items=[
            sac.ChipItem(label="Single API call (Text)", icon="body-text"),
            sac.ChipItem(label="Single API call (JSON)", icon="code-slash"),
            # sac.ChipItem(label='Mass API call (Text)', icon='body-text'),
            sac.ChipItem(label="Mass API call (JSON)", icon="code-slash"),
        ],
        index=[0],
        format_func="title",
        radius="sm",
        size="sm",
        align="left",
        variant="light",
    )

    # Assume that `options` returns the label of the selected chip
    selected_option = (
        options  # Update this based on how options are returned from sac.chip
    )
    st.divider()
    a1, a2, a3 = st.columns(3)
    with a1:
        # Find the index of the default model
        default_index = SAFA_MODEL_LIST.index(st.session_state.default_llm_model)
        select_model = st.selectbox(
            "Select a model", SAFA_MODEL_LIST, index=default_index
        )
    with a2:
        leniency_settings()
    with a3:
        pass
    with st.expander("Configure Chatbot parameters"):
        st.warning("This Chabot parameters will overide the leniency settings")
        chatbot_settings()

    if selected_option == "Single API call (Text)":
        st.subheader(":blue[Single API call (Text)]")
        if select_model.startswith("claude"):
            st.warning(
                "This model is not available for this option. Please select another model."
            )
            return

        st.write(":red[Prompt Content creation:]")
        content_prompt = short_answer_fa_interface(False)
        st.divider()
        if content_prompt:
            api_call(content_prompt[1], select_model)
    elif selected_option == "Single API call (JSON)":
        st.subheader(":blue[Single API call (JSON)]")
        # if select_model.startswith("claude"):
        # 	st.warning("This model is not available for this option. Please select another model.")
        # 	return
        st.write(":red[Prompt Content creation:]")
        content_prompt = short_answer_fa_interface(True)
        if content_prompt:
            st.success("Content prompt generated successfully")

        st.divider()
        if content_prompt and st.session_state.j_tools_format:
            tools = json.loads(st.session_state.j_tools_format)
            # st.write(content_prompt[0])
            if select_model.startswith("claude"):
                claude_api_call_json(
                    content_prompt[1], select_model, tools, content_prompt[0]
                )
            else:
                api_call_json(content_prompt[1], select_model, tools, content_prompt[0])
    # elif selected_option == 'Mass API call (Text)': #not in use
    # 	st.write("Mass API call (Text)")
    # 	st.write(":red[Ensure your CSV file has the following columns: subject, level, question, suggested_answer, student_answer, total_marks, rubrics]")
    # 	if upload_csv():
    # 		if st.button("Cancel Upload"):
    # 			st.session_state.prompt_df = None
    # 		pass_test = check_column_values(st.session_state.prompt_df , ['subject', 'level','question', 'suggested_answer', 'student_answer', 'total_marks', 'rubrics'])
    # 		if not pass_test:
    # 			st.error("Please upload a CSV file with the required columns or modify the dataframe")
    # 		if pass_test:
    # 			batch_call(select_model,st.session_state.prompt_df, False)
    # 			st.data_editor(st.session_state.prompt_df)
    elif selected_option == "Mass API call (JSON)":
        if select_model.startswith("claude"):
            st.warning(
                "This model is not available for this option. Please select another model."
            )
            return
        if (
            st.session_state.user["profile_id"] == SA
            or st.session_state.user["profile_id"] == AD
            or st.session_state.user["profile_id"] == "Bulk Tester"
        ):
            st.subheader(":blue[Batch API call (JSON)]")
            st.write(
                ":red[Ensure your CSV file has the following columns: question, suggested_answer, student_answer, total_marks, rubrics]"
            )
            st.write(
                ":red[All the cells in all the columns (except rubrics) must have a content or else the row will be dropped]"
            )
            if upload_csv():
                if st.button("Cancel Upload"):
                    st.session_state.prompt_df = None
                pass_test = check_column_values(
                    st.session_state.prompt_df,
                    [
                        "subject",
                        "level",
                        "question",
                        "suggested_answer",
                        "student_answer",
                        "total_marks",
                        "rubrics",
                    ],
                )
                if not pass_test:
                    st.error(
                        "Please upload a CSV file with the required columns or modify the dataframe"
                    )
                if pass_test:
                    batch_call(select_model, st.session_state.prompt_df, True)
                    st.data_editor(st.session_state.prompt_df)
        else:
            st.warning(
                "You do not have the necessary permissions to access this feature."
            )
            return
