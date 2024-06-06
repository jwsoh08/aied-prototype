import os
from datetime import datetime
import streamlit as st
import streamlit_antd_components as sac

from pymongo import MongoClient
import pandas as pd
from Markdown2docx import Markdown2docx
from openai import OpenAI

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory

import google.generativeai as genai
import anthropic

from database.mongodb import initialise_rag_collection, fetch_serialized_faiss
from database.sqlite3 import insert_into_data_table
from utils.app_utils import load_chatbot_session_states
from utils.secrets_reader import (
    SecretsRetriever,
    return_google_key,
    return_claude_key,
    return_cohere_key,
)

from components.forms import ai_chatbot_settings
from config.settings import CHATBOT_MODEL_LIST
from constants import SA, AD


def claude_bot(bot_name, c_model, memory_flag, rag_flag):
    client = anthropic.Anthropic(api_key=return_claude_key())
    greetings_str = f"Hi, I am Claude {bot_name}"
    help_str = "How can I help you today?"
    # Check if st.session_state.msg exists, and if not, initialize with greeting and help messages
    if "msg" not in st.session_state:
        st.session_state.msg = [
            {"role": "assistant", "content": greetings_str},
            {"role": "assistant", "content": help_str},
        ]
    elif st.session_state.msg == []:
        st.session_state.msg = [
            {"role": "assistant", "content": greetings_str},
            {"role": "assistant", "content": help_str},
        ]

    messages = st.container(border=True)
    # showing the history of the chatbots
    for message in st.session_state.msg:
        with messages.chat_message(message["role"]):
            st.markdown(message["content"])
    # chat bot input

    try:
        if prompt := st.chat_input("Enter your query"):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with messages.chat_message("user"):
                st.markdown(prompt)
            with messages.chat_message("assistant"):
                prompt_template = prompt_template_function(
                    prompt, memory_flag, rag_flag
                )
                with client.messages.stream(
                    max_tokens=1024,
                    system=prompt_template,
                    messages=[{"role": "user", "content": prompt}],
                    model=c_model,
                ) as stream:

                    response = st.write_stream(stream.text_stream)
            st.session_state.msg.append({"role": "assistant", "content": response})
            if memory_flag:
                st.session_state["memory"].save_context(
                    {"input": prompt}, {"output": response}
                )
                # Insert data into the table
            now = datetime.now()  # Using ISO format for date
            response_str = str(response)
            prompt_str = str(prompt)
            # Now concatenate and calculate the length as intended.
            num_tokens = len(response_str + prompt_str) * 1.3
            # st.write(num_tokens)
            insert_into_data_table(
                now.strftime("%d/%m/%Y %H:%M:%S"),
                response_str,
                prompt_str,
                num_tokens,
                bot_name,
            )
            if st.session_state.download_response_flag == True:
                st.session_state.chat_response = add_response(response)

    except Exception as e:
        st.exception(e)


def gemini_bot(bot_name, c_model, memory_flag, rag_flag):
    genai.configure(api_key=return_google_key())
    greetings_str = f"Hi, I am Gemini {bot_name}"
    help_str = "How can I help you today?"
    # Check if st.session_state.msg exists, and if not, initialize with greeting and help messages
    if "msg" not in st.session_state:
        st.session_state.msg = [
            {"role": "assistant", "content": greetings_str},
            {"role": "assistant", "content": help_str},
        ]
    elif st.session_state.msg == []:
        st.session_state.msg = [
            {"role": "assistant", "content": greetings_str},
            {"role": "assistant", "content": help_str},
        ]

    messages = st.container(border=True)
    # showing the history of the chatbots
    for message in st.session_state.msg:
        with messages.chat_message(message["role"]):
            st.markdown(message["content"])

    try:
        if prompt := st.chat_input("Enter your query"):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with messages.chat_message("user"):
                st.markdown(prompt)
            with messages.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                # response =
                chat_model = genai.GenerativeModel(c_model)
                prompt_template = prompt_template_function(
                    prompt, memory_flag, rag_flag
                )
                prompt = (prompt_template + "\n This is the user query" + prompt,)
                response_stream = chat_model.generate_content(prompt, stream=True)
                for response_object in response_stream:
                    # Check if response_object has a 'text' attribute
                    if hasattr(response_object, "text"):
                        # Append the text to full_response
                        full_response += response_object.text

                        # Update the placeholder with the current state of full_response
                    message_placeholder.markdown(full_response + "▌")

                # Final update to the placeholder after streaming is complete
                message_placeholder.markdown(full_response)

            st.session_state.msg.append({"role": "assistant", "content": full_response})
            if memory_flag:
                st.session_state["memory"].save_context(
                    {"input": prompt}, {"output": full_response}
                )
            # Insert data into the table
            now = datetime.now()  # Using ISO format for date
            full_response_str = str(full_response)
            prompt_str = str(prompt)

            # Now concatenate and calculate the length as intended.
            num_tokens = len(full_response_str + prompt_str) * 1.3
            # st.write(num_tokens)
            insert_into_data_table(
                now.strftime("%d/%m/%Y %H:%M:%S"),
                full_response_str,
                prompt_str,
                num_tokens,
                bot_name,
            )
            if st.session_state.download_response_flag == True:
                st.session_state.chat_response = add_response(full_response)

    except Exception as e:
        st.exception(e)


def openai_bot(bot_name, c_model, memory_flag, rag_flag):
    secrets_retriever = SecretsRetriever()
    client = OpenAI(
        api_key=secrets_retriever.get_secret("openai_api_key"),
    )

    full_response = ""
    greetings_str = f"Hi, I am {bot_name}"
    help_str = "How can I help you today?"
    # Check if st.session_state.msg exists, and if not, initialize with greeting and help messages
    if "msg" not in st.session_state:
        st.session_state.msg = [
            {"role": "assistant", "content": greetings_str},
            {"role": "assistant", "content": help_str},
        ]
    elif st.session_state.msg == []:
        st.session_state.msg = [
            {"role": "assistant", "content": greetings_str},
            {"role": "assistant", "content": help_str},
        ]
    messages = st.container(border=True)
    # showing the history of the chatbots
    for message in st.session_state.msg:
        with messages.chat_message(message["role"]):
            st.markdown(message["content"])
    # chat bot input
    try:
        if prompt := st.chat_input("Enter your query"):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with messages.chat_message("user"):
                st.markdown(prompt)
            with messages.chat_message("assistant"):
                prompt_template = prompt_template_function(
                    prompt, memory_flag, rag_flag
                )
                stream = client.chat.completions.create(
                    model=c_model,
                    messages=[
                        {"role": "system", "content": prompt_template},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=float(st.session_state.default_temp),
                    stream=True,
                )
                response = st.write_stream(stream)
            st.session_state.msg.append({"role": "assistant", "content": response})
            if memory_flag:
                st.session_state["memory"].save_context(
                    {"input": prompt}, {"output": response}
                )
            # Insert data into the table
            now = datetime.now()  # Using ISO format for date
            num_tokens = len(full_response + prompt) * 1.3
            insert_into_data_table(
                now.strftime("%d/%m/%Y %H:%M:%S"),
                response,
                prompt,
                num_tokens,
                bot_name,
            )
            if st.session_state.download_response_flag == True:
                st.session_state.chat_response = add_response(response)

    except Exception as e:
        st.exception(e)


def cohere_bot(bot_name, c_model, memory_flag, rag_flag):
    pass
    # co = cohere.Client(return_cohere_key())
    # greetings_str = f"Hi, I am Cohere {bot_name}"
    # help_str = "How can I help you today?"
    # # Check if st.session_state.msg exists, and if not, initialize with greeting and help messages
    # if "msg" not in st.session_state:
    #     st.session_state.msg = [
    #         {"role": "assistant", "content": greetings_str},
    #         {"role": "assistant", "content": help_str},
    #     ]
    # elif st.session_state.msg == []:
    #     st.session_state.msg = [
    #         {"role": "assistant", "content": greetings_str},
    #         {"role": "assistant", "content": help_str},
    #     ]

    # messages = st.container(border=True)

    # for message in st.session_state.msg:
    #     with messages.chat_message(message["role"]):
    #         st.markdown(message["content"])

    # try:
    #     if prompt := st.chat_input("Enter your query"):
    #         st.session_state.msg.append({"role": "user", "content": prompt})
    #         with messages.chat_message("user"):
    #             st.markdown(prompt)
    #         with messages.chat_message("assistant"):
    #             message_placeholder = st.empty()
    #             full_response = ""
    #             prompt_msg = (
    #                 prompt_template_function(prompt, memory_flag, rag_flag)
    #                 + "\n This is the user query"
    #                 + prompt
    #             )
    #             # if response and response.generations:
    #             # for response in co.chat(prompt=faq + "\n" + prompt, max_tokens=1000, stream = True):
    #             response_stream = co.chat_stream(message=prompt_msg, max_tokens=1000)

    #             for response_object in response_stream:
    #                 # Check if response_object has a 'text' attribute
    #                 if hasattr(response_object, "text"):
    #                     # Append the text to full_response
    #                     full_response += response_object.text

    #                     # Update the placeholder with the current state of full_response
    #                 message_placeholder.markdown(full_response + "▌")

    #             # Final update to the placeholder after streaming is complete
    #             message_placeholder.markdown(full_response)
    #         st.session_state.msg.append({"role": "assistant", "content": full_response})
    #         if memory_flag:
    #             st.session_state["memory"].save_context(
    #                 {"input": prompt}, {"output": full_response}
    #             )
    #             # Insert data into the table
    #         now = datetime.now()  # Using ISO format for date
    #         num_tokens = len(full_response + prompt) * 1.3
    #         # st.write(num_tokens)
    #         insert_into_data_table(
    #             now.strftime("%d/%m/%Y %H:%M:%S"),
    #             full_response,
    #             prompt,
    #             num_tokens,
    #             bot_name,
    #         )
    #         if st.session_state.download_response_flag == True:
    #             st.session_state.chat_response = add_response(full_response)

    # except Exception as e:
    #     st.exception(e)


def add_response(response):
    opt = sac.buttons(
        [sac.ButtonsItem(label="Save Response", color="#40826D")],
        format_func="title",
        index=None,
        size="small",
    )

    if add_response:
        st.session_state.data_doc = st.session_state.data_doc + "\n\n" + response

    return opt


def prompt_template_function(prompt, memory_flag, rag_flag):
    # check if there is kb loaded
    if st.session_state.vs:
        docs = st.session_state.vs.similarity_search(query=prompt, k=4)
        resource = docs[0].page_content
        source = docs[0].metadata
        st.session_state.rag_response = resource, source
    else:
        resource = ""
        source = ""

    if memory_flag:
        if "memory" not in st.session_state:
            st.session_state.memory = ConversationBufferWindowMemory(
                k=st.session_state.default_k_memory
            )
        mem = st.session_state.memory.load_memory_variables({})

    if rag_flag and memory_flag:  # rag and memory only
        prompt_template = (
            st.session_state.chatbot
            + f"""
							Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. 
							Search Result:
							{resource}
							{source}
							History of conversation:
							{mem}
							You must quote the source of the Search Result if you are using the search result as part of the answer"""
        )

        return prompt_template

    elif rag_flag and not memory_flag:  # rag kb only
        prompt_template = (
            st.session_state.chatbot
            + f"""
						Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. 
						Search Result:
						{resource}
						{source}
						You must quote the source of the Search Result if you are using the search result as part of the answer"""
        )
        return prompt_template

    elif not rag_flag and memory_flag:  # memory only
        prompt_template = (
            st.session_state.chatbot
            + f""" 
						History of conversation:
						{mem}"""
        )
        return prompt_template
    else:  # base bot nothing
        return st.session_state.chatbot


def response_download():
    docx_name = "crp" + st.session_state.user["id"] + ".docx"
    docx_path = os.path.join("chatbot_response", docx_name)

    if os.path.exists(docx_path):
        # Provide the docx for download via Streamlit
        with open(docx_path, "rb") as docx_file:
            docx_bytes = docx_file.read()
            st.success("File is ready for downloading")
            st.download_button(
                label="Download document as DOCX",
                data=docx_bytes,
                file_name=docx_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        os.remove(docx_path)
        st.session_state.button_text = "Reset"
    else:
        st.warning("There is no lesson plan available for download.")


def complete_my_lesson():
    plan_action = sac.buttons(
        [
            sac.ButtonsItem(label="Preview Responses", icon="eye", color="#00BFFF"),
            sac.ButtonsItem(
                label="Download Responses",
                icon="file-earmark-arrow-down",
                color="#40826D",
            ),
            sac.ButtonsItem(
                label="Clear Responses", icon="file-earmark-arrow-down", color="#FF7F50"
            ),
        ],
        index=None,
        format_func="title",
        size="small",
    )

    if plan_action == "Preview Responses":
        st.write(st.session_state.data_doc)

    elif plan_action == "Download Responses":
        st.write("Downloading your lesson plan")
        md_filename = "crp" + st.session_state.user["id"] + ".md"
        md_filepath = os.path.join("chatbot_response", md_filename)
        if not os.path.exists("chatbot_response"):
            os.makedirs("chatbot_response")
        with open(md_filepath, "w", encoding="utf-8") as file:
            file.write(st.session_state.data_doc)
        # Convert the markdown file to a docx
        base_filepath = os.path.join(
            "chatbot_response", "crp" + st.session_state.user["id"]
        )
        project = Markdown2docx(base_filepath)
        project.eat_soup()
        project.save()  # Assuming it saves the file with the same name but a .docx extension
        response_download()
    elif plan_action == "Clear Responses":
        if st.checkbox("Clear Responses"):
            st.session_state.data_doc = ""
            st.success("Responses cleared")


def fetch_shared_serialized_faiss(db_collection, rag_name):
    document = db_collection.find_one({"name": rag_name})
    if document:
        return document["rag_data"]
    else:
        return None


def list_rags_for_shareable(db_collection, school):
    query = {"sharing": True, "school": school}
    documents = db_collection.find(query)
    rag_names = [doc["name"] for doc in documents]
    return rag_names


def sa_select_school():
    documents = st.session_state.s_collection.find({}, {"sch_name": 1, "_id": 0})
    sch_names = [doc["sch_name"] for doc in documents]
    if not sch_names:
        st.error("No schools found. Please add a school first.")
        return []
    return sch_names


def display_rag_documents_as_dataframe(school):
    documents_owner_school = st.session_state.rag_collection.find({"owner": school})
    documents_sharing_true = st.session_state.rag_collection.find(
        {"sharing": True, "school": school}
    )
    combined_docs_list = []
    for doc in documents_owner_school:
        doc.pop("_id", None)
        doc.pop("rag_data", None)
        combined_docs_list.append(doc)

    for doc in documents_sharing_true:
        if doc not in combined_docs_list:
            doc.pop("_id", None)
            doc.pop("rag_data", None)
            combined_docs_list.append(doc)

    df = pd.DataFrame(combined_docs_list)
    st.dataframe(df)


def list_rags_for_owner(db_collection, owner):
    documents = db_collection.find({"owner": owner})
    rag_names = [doc["name"] for doc in documents]
    return rag_names


def set_index_button():
    st.session_state.index_button = 0


def load_rag():
    if "index_button" not in st.session_state:
        set_index_button()

    secrets_retriever = SecretsRetriever()
    os.environ["OPENAI_API_KEY"] = secrets_retriever.get_secret("openai_api_key")
    st.write(f"#### Currently Loaded KB (RAG): {st.session_state.current_kb_model}")

    initialise_rag_collection()

    # Fetch all RAGs for the current user
    if st.toggle("Load Personal RAG"):
        display_rag_documents_as_dataframe(st.session_state.user["id"])
        rag_list = list_rags_for_owner(
            st.session_state.rag_collection, st.session_state.user["id"]
        )
        if rag_list == []:
            st.error("No RAGs found.")
        else:
            rag_name = st.selectbox("Select RAG", ["-"] + rag_list)
            d1, d2, d3 = st.columns([2, 2, 3])
            with d1:
                if st.button("Load RAG", on_click=set_index_button):
                    if rag_name != "-":
                        serialized_faiss = fetch_serialized_faiss(
                            st.session_state.rag_collection,
                            rag_name,
                            st.session_state.user["id"],
                        )
                        embeddings_instance = OpenAIEmbeddings()
                        faiss_obj = FAISS.deserialize_from_bytes(
                            embeddings=embeddings_instance, serialized=serialized_faiss
                        )
                        st.session_state.vs = faiss_obj
                        st.session_state.current_kb_model = rag_name
                        st.rerun()
                    else:
                        st.warning("Please select a RAG to load.")

            with d2:
                if st.session_state.vs is not None:
                    if st.button("Unload RAG"):
                        st.session_state.vs = None
                        st.session_state.current_kb_model = ""
                        st.rerun()
    else:
        if st.session_state.user["profile_id"] == SA:
            sch_names = sa_select_school()
            school = st.selectbox(
                "Select School", ["Select School"] + sch_names, key="rag_school"
            )
            st.write("School RAG Display")
            display_rag_documents_as_dataframe(school)
            if school != "Select School" and school != None:
                rag_list = list_rags_for_owner(st.session_state.rag_collection, school)
                share_list = list_rags_for_shareable(
                    st.session_state.rag_collection, school
                )
                rag_list = share_list + rag_list
                if rag_list == []:
                    st.error("No RAGs found.")
                else:
                    rag_name = st.selectbox(
                        "Select RAG",
                        ["-"] + rag_list,
                        index=st.session_state.index_button,
                    )
                    e1, e2, e3 = st.columns([2, 2, 3])
                    with e1:
                        if st.button("Load RAG", on_click=set_index_button):
                            if rag_name != "-":
                                # Fetch the serialized FAISS object from the database
                                if rag_name in share_list:
                                    serialized_faiss = fetch_shared_serialized_faiss(
                                        st.session_state.rag_collection, rag_name
                                    )
                                else:
                                    serialized_faiss = fetch_serialized_faiss(
                                        st.session_state.rag_collection,
                                        rag_name,
                                        school,
                                    )
                                embeddings_instance = OpenAIEmbeddings()
                                faiss_obj = FAISS.deserialize_from_bytes(
                                    embeddings=embeddings_instance,
                                    serialized=serialized_faiss,
                                )

                                st.session_state.vs = faiss_obj
                                st.session_state.current_kb_model = rag_name
                                st.rerun()
                            else:
                                st.warning("Please select a RAG to load.")
                    with e2:
                        if st.session_state.vs is not None:
                            if st.button("Unload RAG"):
                                st.session_state.vs = None
                                st.session_state.current_kb_model = ""
                                st.rerun()
        else:  # student or teacher
            st.write("School RAG Display")
            display_rag_documents_as_dataframe(st.session_state.user["school_id"])
            rag_list = list_rags_for_owner(
                st.session_state.rag_collection, st.session_state.user["school_id"]
            )
            share_list = list_rags_for_shareable(
                st.session_state.rag_collection, st.session_state.user["school_id"]
            )
            rag_list = share_list + rag_list
            if rag_list == []:
                st.error("No RAGs found.")
            else:
                rag_name = st.selectbox(
                    "Select RAG", ["-"] + rag_list, index=st.session_state.index_button
                )
                f1, f2, f3 = st.columns([2, 2, 3])
                with f1:
                    if st.button("Load RAG", on_click=set_index_button):
                        if rag_name != "-":
                            # Fetch the serialized FAISS object from the database
                            if rag_name in share_list:
                                serialized_faiss = fetch_shared_serialized_faiss(
                                    st.session_state.rag_collection, rag_name
                                )
                            else:
                                serialized_faiss = fetch_serialized_faiss(
                                    st.session_state.rag_collection,
                                    rag_name,
                                    st.session_state.user["school_id"],
                                )

                            embeddings_instance = OpenAIEmbeddings()
                            faiss_obj = FAISS.deserialize_from_bytes(
                                embeddings=embeddings_instance,
                                serialized=serialized_faiss,
                            )

                            st.session_state.vs = faiss_obj
                            st.session_state.current_kb_model = rag_name
                            st.rerun()

                        else:
                            st.warning("Please select a RAG to load.")
                with f2:
                    if st.session_state.vs is not None:
                        if st.button("Unload RAG"):
                            st.session_state.vs = None
                            st.session_state.current_kb_model = ""
                            st.rerun()


def main_chatbot_functions():
    # check if prompt_template is in session state the default is the chatbot_key
    # check the school settings for chatbot settings
    with st.expander("Chatbot Settings"):
        c1, c2 = st.columns([1, 1])
    # 	with c2:
    # 		memory = True
    # 		rag = True
    # 		enable_vision = True
    # 		show_rag = True
    # 		chat_bot = "-"
    # 		if st.session_state.user['profile_id'] == SA or st.session_state.user['profile_id'] == AD:
    # 			if st.checkbox("Enable Chatbot Settings"):
    # 				bot_settings()
    # 			memory = st.checkbox("Memory Enabled", value=True)
    # 			rag = st.checkbox("RAG Enabled", value=True)
    # 			enable_vision = st.checkbox("Enable Image Analysis", value=True)
    # 			show_rag = st.checkbox("Show RAG", value=True)
    # 			chat_bot = st.selectbox("OpenAI model", ["-"] + CHATBOT_MODEL_LIST)
    # 	with c1:
    # 		if rag:
    # 			load_rag()
    # with st.expander("Download Chatbot Responses"):
    # 	st.session_state.download_response_flag = st.checkbox("Enable Download Responses")
    # 	complete_my_lesson()

    # b1, b2 = st.columns([2,1])
    # with b1:

    # 	if chat_bot == "-":
    # 		chat_bot = st.session_state.default_llm_model
    # 	if chat_bot.startswith("gpt"):
    # 		openai_bot(CHATBOT, chat_bot, memory, rag)
    # 	elif chat_bot.startswith("gemini"):
    # 		gemini_bot(CHATBOT, chat_bot, memory, rag)
    # 	elif chat_bot.startswith("claude"):
    # 		claude_bot(CHATBOT, chat_bot, memory, rag)
    # 	# elif chat_bot.startswith("cohere"):
    # 	# 	cohere_bot(CHATBOT, chat_bot, memory, rag)
    # with b2:
    # 	if st.button("Clear Chat"):
    # 		# if "msg" in st.session_state and st.session_state.msg != []:
    # 		# 	store_summary_chatbot_response()
    # 		clear_session_states()
    # 		st.rerun()
    # 	if enable_vision:
    # 		with st.container(border=True):
    # 			if "memory" not in st.session_state:
    # 				st.session_state.memory = ConversationBufferWindowMemory(k=st.session_state.default_k_memory)
    # 			detect_file_upload()
    # 			i_prompt = st.text_area("Enter a prompt for the image", value="From the image, I would like to know about this topic...", height=150)
    # 			if st.button("Analyse Image"):
    # 				if st.session_state.voice_image_file_exist:
    # 					with st.spinner("Analysing image..."):
    # 						# Analyse the image
    # 						if chat_bot.startswith("gpt"):
    # 							response = analyse_image_chat_openai(st.session_state.voice_image_file_exist[0], i_prompt)
    # 						elif chat_bot.startswith("claude"):
    # 							response = analyse_image_chat_anthropic(chat_bot, i_prompt)
    # 						else: #default cohere and gemini use free image analysis
    # 							response = analyse_image_chat_gemini(st.session_state.voice_image_file_exist[0], i_prompt)
    # 						st.session_state.msg.append({"role": "assistant", "content": response})
    # 						if memory:
    # 							st.session_state["memory"].save_context({"input": i_prompt},{"output": response})
    # 						st.rerun()
    # 				else:
    # 					st.error("Please upload an image first")

    # 	if show_rag:
    # 		with st.container(border=True):
    # 			if rag:
    # 				st.write("RAG Results")
    # 				if st.session_state.rag_response == None  or st.session_state.rag_response == "":
    # 					resource = ""
    # 					source = ""
    # 				else:
    # 					resource, source = st.session_state.rag_response
    # 				st.write("Resource: ", resource)
    # 				st.write("Source : ", source)
    # 			else:
    # 				st.write("RAG is not enabled")


def ai_chatbot():
    st.subheader(f":green[{st.session_state.option}]")
    load_chatbot_session_states()

    with st.expander("Chatbot Settings"):
        col_1, col_2 = st.columns([1, 1])

        memory = True
        rag = True
        enable_vision = True
        show_rag = True
        chat_bot = "-"

        with col_1:
            if rag:
                load_rag()

        with col_2:

            if (
                st.session_state.user["profile_id"] == SA
                or st.session_state.user["profile_id"] == AD
            ):
                if st.checkbox("Enable Chatbot Settings"):
                    ai_chatbot_settings()
                # other chat bot settings
                memory = st.checkbox("Memory Enabled", value=True)
                rag = st.checkbox("RAG Enabled", value=True)
                enable_vision = st.checkbox("Enable Image Analysis", value=True)
                show_rag = st.checkbox("Show RAG", value=True)
                chat_bot = st.selectbox("OpenAI model", ["-"] + CHATBOT_MODEL_LIST)

    with st.expander("Download Chatbot Responses"):
        st.session_state.download_response_flag = st.checkbox(
            "Enable Download Responses"
        )
        complete_my_lesson()
    b1, b2 = st.columns([2, 1])
    with b1:
        if chat_bot == "-":
            chat_bot = st.session_state.default_llm_model
        if chat_bot.startswith("gpt"):
            openai_bot("AI Chatbot", chat_bot, memory, rag)
        elif chat_bot.startswith("gemini"):
            gemini_bot("AI Chatbot", chat_bot, memory, rag)
        elif chat_bot.startswith("claude"):
            claude_bot("AI Chatbot", chat_bot, memory, rag)
        # elif chat_bot.startswith("cohere"):
        # 	cohere_bot(CHATBOT, chat_bot, memory, rag)
