MENU_FUNCTIONS = {
    "Personal Dashboard": "An interface tailored for individual users to view and manage their personal activities and settings.",
    "AI Chatbot": "A virtual assistant powered by AI to interact and answer queries in real-time.",
    "Short Answer FA Analyser": "A system to analyse and provide feedback on short answer questions.",
    "AC Co-Pilot": "A system to test the assistance in generating lesson content for various purposes.",
    "KB management": "A system to manage the knowledge base, including its content, structure, and access permissions.",
    "Prompt Management": "A system to manage the prompt templates, including its content, structure, and access permissions.",
    "Organisation Management": "A platform to oversee and control various aspects of an organization including its structure, roles, and policies.",
}

PROMPT_CONFIG = {
    "SAFA OpenAI Production Prompt": "SAFA OpenAI Production Prompt",
    "SAFA OpenAI Development Prompt 1": "SAFA OpenAI Development Prompt 1",
    "SAFA OpenAI Development Prompt 2": "SAFA OpenAI Development Prompt 2",
    "SAFA OpenAI Development Prompt 3": "SAFA OpenAI Development Prompt 3",
    "SAFA OpenAI Tools Production": "SAFA OpenAI Production Tools Format Prompt",
    "SAFA OpenAI Tools Development Format 1": "SAFA OpenAI Tools Format Prompt 1",
    "SAFA OpenAI Tools Development Format 2": "SAFA OpenAI Tools Format Prompt 2",
    "SAFA OpenAI Tools Development Format 3": "SAFA OpenAI Tools Format Prompt 3",
    "SAFA Claude Tools Production": "SAFA Claude Production Tools Format Prompt",
    "SAFA Claude Tools Development Format 1": "SAFA Claude Tools Format Prompt 1",
    "SAFA Claude Tools Development Format 2": "SAFA Claude Tools Format Prompt 2",
    "SAFA Claude Tools Development Format 3": "SAFA Claude Tools Format Prompt 3",
    "AC OpenAI Section Production Prompt": "AC OpenAI S Production prompt",
    "AC OpenAI Section Development Prompt 1": "AC OpenAI S Development Prompt 1",
    "AC OpenAI Section Development Prompt 2": "AC OpenAI S Development Prompt 2",
    "AC OpenAI Activity Production Prompt": "AC OpenAI A Production prompt",
    "AC OpenAI Activity Development Prompt 1": "AC OpenAI A Development Prompt 1",
    "AC OpenAI Activity Development Prompt 2": "AC OpenAI A Development Prompt 2",
    "AC OpenAI Component Production Prompt": "AC OpenAI D Production prompt",
    "AC OpenAI Component Development Prompt 1": "AC OpenAI C Development Prompt 1",
    "AC OpenAI Component Development Prompt 2": "AC OpenAI C Development Prompt 2",
    "AC OpenAI Tools Section Production Prompt": "AC OpenAI S Tools Production Prompt",
    "AC OpenAI Tools Section Development Prompt 1": "AC OpenAI S Tools Development Prompt 1",
    "AC OpenAI Tools Activity Production Prompt": "AC OpenAI A Tools Production Prompt",
    "AC OpenAI Tools Activity Development Prompt 1": "AC OpenAI A Tools Development Prompt 1",
    "AC OpenAI Tools Component Production Prompt": "AC OpenAI C Tools Production Prompt",
    "AC OpenAI Tools Component Development Prompt 1": "AC OpenAI C Tools Development Prompt 1",
    "AC Claude Section Production Prompt": "AC Claude S production prompt",
    "AC Claude Section Development Prompt 1": "AC Claude S Development Prompt 1",
    "AC Claude Section Development Prompt 2": "AC Claude S Development Prompt 2",
    "AC Claude Activity Production Prompt": "AC Claude A production prompt",
    "AC Claude Activity Development Prompt 1": "AC Claude A Development Prompt 1",
    "AC Claude Activity Development Prompt 2": "AC Claude A Development Prompt 2",
    "AC Claude Component Production Prompt": "AC Claude C production prompt",
    "AC Claude Component Development Prompt 1": "AC Claude C Development Prompt 1",
    "AC Claude Component Development Prompt 2": "AC Claude C Development Prompt 2",
    "AC Claude Section Example Prompt": "AC Claude S Example Prompt",
    "AC Claude Activity Example Prompt": "AC Claude A Example Prompt",
    "AC Claude Component Example Prompt": "AC Claude C Example Prompt",
    "Chatbot": "You are a helpful assistant",
}


APP_CONFIG = {
    "openai_key": "YOUR API KEY",
    "cohere_key": "YOUR API KEY",
    "google_key": "YOUR API KEY",
    "claude_key": "YOUR API KEY",
    "groq_key": "YOUR API KEY",
    "serp_key": "YOUR API KEY",
    "deepgram_key": "YOUR API KEY",
    "assistant_id_1": "YOUR API KEY",
    "assistant_id_2": "YOUR API KEY",
    "assistant_id_3": "YOUR API	KEY",
    "default_temp": 0.1,
    "default_frequency_penalty": 0.0,
    "default_presence_penalty": 0.0,
    "default_k_memory": 4,
    "default_top_p": 0.0,
    "default_seed_num": 0.0,
    "default_max_tokens": 4000,
    "default_llm_model": "gpt-4o",
    "default_password": "p@ssword",
}

SAFA_CONFIG = {
    "default_temp": 0.1,
    "default_frequency_penalty": 0.0,
    "default_presence_penalty": 0.0,
    "default_top_p": 0.0,
    "default_max_tokens": 4000,
    "default_llm_model": "gpt-4o",
}

SAFA_PROMPT_OPTIONS = {
		"SAFA OpenAI Production Prompt": "st.session_state.safa_openai_production_prompt",
		"SAFA OpenAI Development Prompt 1": "st.session_state.safa_openai_development_prompt_1",
		"SAFA OpenAI Development Prompt 2": "st.session_state.safa_openai_development_prompt_2",
		"SAFA OpenAI Development Prompt 3": "st.session_state.safa_openai_development_prompt_3",
		"SAFA Claude Development Prompt 1": "st.session_state.safa_claude_development_prompt_1",	
	}

CHATBOT_MODEL_LIST = [
    "gpt-3.5-turbo-0125",
    "claude-3-haiku-20240307",
    "gemini-pro",
    "gpt-3.5-turbo-1106",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "gpt-4-turbo-preview",
    "gpt-4o",
]

ACP_CONFIG = {
    "default_temp": 0.7,
    "default_frequency_penalty": 0.0,
    "default_presence_penalty": 0.0,
    "default_top_p": 0.0,
    "default_max_tokens": 4000,
    "default_llm_model": "claude-3-haiku-20240307",
}

CLASS_LEVELS_SINGAPORE = [
    "Primary 1",
    "Primary 2",
    "Primary 3",
    "Primary 4",
    "Primary 5",
    "Primary 6",
    "Secondary 1",
    "Secondary 2",
    "Secondary 3",
    "Secondary 4",
    "Secondary 5",
    "Junior College 1",
    "Junior College 2",
]

SUBJECTS_SINGAPORE = [
    "English Language",
    "Chinese",
    "Malay",
    "Tamil",
    "Mathematics",
    "Science",
    "Social Studies",
    "Physical Education (PE)",
    "Art",
    "Music",
    "Character and Citizenship Education (CCE)",
    "Design and Technology",
    "Food and Consumer Education (FCE)",
    "Computer Studies",
    "Additional Mathematics (Secondary)",
    "Literature (Secondary)",
    "History (Secondary)",
    "Geography (Secondary)",
    "Physics (Secondary)",
    "Chemistry (Secondary)",
    "Biology (Secondary)",
    "Economics (JC)",
    "Accounting (JC)",
    "General Paper (JC)",
    "Mathematics (JC)",
    "Further Mathematics (JC)",
    "Physics (JC)",
    "Chemistry (JC)",
    "Biology (JC)",
    "History (JC)",
    "Geography (JC)",
    "Art (JC)",
    "Music (JC)",
    "Theatre Studies and Drama (JC)",
]


AC_MODEL_LIST = [
    "claude-3-haiku-20240307",
    "gpt-3.5-turbo-0125",
    "gpt-4o",
    "gpt-3.5-turbo-1106",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
]

SAFA_MODEL_LIST = ["gpt-4o","gpt-3.5-turbo-0125",  "claude-3-haiku-20240307", "gpt-3.5-turbo-1106", "claude-3-opus-20240229", "claude-3-sonnet-20240229"]

RUBRICS = """
            Id for this dimension: 21478.Dimension Criteria: Relevance to question – up to 1 – The point has little relevance to the question., up to 3 – The point is largely relevant to the question. Maximum mark for this dimension:3.
		    Id for this dimension: 21479.Dimension Criteria: Depth of Answer. – up to 1 – No examples or illustration., up to 3 – Some examples to full range of examples. Maximum mark for this dimension:3.
        """
