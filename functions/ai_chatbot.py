import os
import streamlit as st

from pymongo import MongoClient
import pandas as pd

from database.mongodb import initialise_rag_collection

from utils.app_utils import load_chatbot_session_states
from utils.secrets_reader import SecretsRetriever

from components.forms import ai_chatbot_settings
from config.settings import CHATBOT_MODEL_LIST
from constants import SA, AD


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


def load_rag():
    if "index_button" not in st.session_state:
        st.session_state.index_button = 0

    secrets_retriever = SecretsRetriever()
    os.environ["OPENAI_API_KEY"] = secrets_retriever.get_secret("openai_api_key")
    st.write(f"#### Currently Loaded KB (RAG): {st.session_state.current_kb_model}")

    initialise_rag_collection()

    # Fetch all RAGs for the current user
    if st.toggle("Load Personal RAG"):
        display_rag_documents_as_dataframe(st.session_state.user["id"])
        rag_list = list_rags_for_owner(st.session_state.rag_collection, st.session_state.user["id"])
        if rag_list == []:
            st.error("No RAGs found.")
        else:
            rag_name = st.selectbox("Select RAG", ["-"] + rag_list)
    #         d1, d2, d3 = st.columns([2, 2, 3])
    #         with d1:
    #             if st.button("Load RAG", on_click=index_button):
    #                 if rag_name != "-":
    #                     # Fetch the serialized FAISS object from the database
    #                     serialized_faiss = fetch_serialized_faiss(
    #                         st.session_state.rag_collection,
    #                         rag_name,
    #                         st.session_state.user["id"],
    #                     )
    #                     # Unserialize the FAISS object
    #                     # faiss_obj = unserialize_faiss_object(serialized_faiss)
    #                     embeddings_instance = OpenAIEmbeddings()
    #                     faiss_obj = FAISS.deserialize_from_bytes(
    #                         embeddings=embeddings_instance, serialized=serialized_faiss
    #                     )

    #                     if faiss_obj is not None:
    #                         # Proceed with using the deserialized FAISS index
    #                         print("FAISS index deserialized successfully.")
    #                     else:
    #                         print("Failed to deserialize FAISS index.")
    #                     # Return the FAISS object
    #                     st.session_state.vs = faiss_obj
    #                     st.session_state.current_kb_model = rag_name
    #                     st.rerun()
    #                 else:
    #                     st.warning("Please select a RAG to load.")
    #         with d2:
    #             if st.session_state.vs is not None:
    #                 if st.button("Unload RAG"):
    #                     st.session_state.vs = None
    #                     st.session_state.current_kb_model = ""
    #                     st.rerun()
    #                 # return faiss_obj, rag_name
    # else:
    #     if st.session_state.user["profile_id"] == SA:
    #         sch_names = sa_select_school()
    #         school = st.selectbox(
    #             "Select School", ["Select School"] + sch_names, key="rag_school"
    #         )
    #         st.write("School RAG Display")
    #         display_documents_as_dataframe(school)
    #         if school != "Select School" and school != None:
    #             rag_list = list_rags_for_owner(st.session_state.rag_collection, school)
    #             share_list = list_rags_for_shareable(
    #                 st.session_state.rag_collection, school
    #             )
    #             rag_list = share_list + rag_list
    #             if rag_list == []:
    #                 st.error("No RAGs found.")
    #             else:
    #                 rag_name = st.selectbox(
    #                     "Select RAG",
    #                     ["-"] + rag_list,
    #                     index=st.session_state.index_button,
    #                 )
    #                 e1, e2, e3 = st.columns([2, 2, 3])
    #                 with e1:
    #                     if st.button("Load RAG", on_click=index_button):
    #                         if rag_name != "-":
    #                             # Fetch the serialized FAISS object from the database
    #                             if rag_name in share_list:
    #                                 serialized_faiss = fetch_shared_serialized_faiss(
    #                                     st.session_state.rag_collection, rag_name
    #                                 )
    #                             else:
    #                                 serialized_faiss = fetch_serialized_faiss(
    #                                     st.session_state.rag_collection,
    #                                     rag_name,
    #                                     school,
    #                                 )
    #                             # st.write(serialized_faiss)
    #                             embeddings_instance = OpenAIEmbeddings()
    #                             faiss_obj = FAISS.deserialize_from_bytes(
    #                                 embeddings=embeddings_instance,
    #                                 serialized=serialized_faiss,
    #                             )
    #                             if faiss_obj is not None:
    #                                 # Proceed with using the deserialized FAISS index
    #                                 print("FAISS index deserialized successfully.")
    #                             else:
    #                                 print("Failed to deserialize FAISS index.")
    #                             # Return the FAISS object
    #                             st.session_state.vs = faiss_obj
    #                             st.session_state.current_kb_model = rag_name
    #                             st.rerun()
    #                         else:
    #                             st.warning("Please select a RAG to load.")
    #                 with e2:
    #                     if st.session_state.vs is not None:
    #                         if st.button("Unload RAG"):
    #                             st.session_state.vs = None
    #                             st.session_state.current_kb_model = ""
    #                             st.rerun()
    # else:  # student or teacher
    #     st.write("School RAG Display")
    #     display_documents_as_dataframe(st.session_state.user["school_id"])
    #     rag_list = list_rags_for_owner(
    #         st.session_state.rag_collection, st.session_state.user["school_id"]
    #     )
    #     share_list = list_rags_for_shareable(
    #         st.session_state.rag_collection, st.session_state.user["school_id"]
    #     )
    #     rag_list = share_list + rag_list
    #     if rag_list == []:
    #         st.error("No RAGs found.")
    #     else:
    #         rag_name = st.selectbox(
    #             "Select RAG", ["-"] + rag_list, index=st.session_state.index_button
    #         )
    #         f1, f2, f3 = st.columns([2, 2, 3])
    #         with f1:
    #             if st.button("Load RAG", on_click=index_button):
    #                 if rag_name != "-":
    #                     # Fetch the serialized FAISS object from the database
    #                     if rag_name in share_list:
    #                         serialized_faiss = fetch_shared_serialized_faiss(
    #                             st.session_state.rag_collection, rag_name
    #                         )
    #                     else:
    #                         serialized_faiss = fetch_serialized_faiss(
    #                             st.session_state.rag_collection,
    #                             rag_name,
    #                             st.session_state.user["school_id"],
    #                         )
    #                     # st.write(serialized_faiss)
    #                     embeddings_instance = OpenAIEmbeddings()
    #                     faiss_obj = FAISS.deserialize_from_bytes(
    #                         embeddings=embeddings_instance,
    #                         serialized=serialized_faiss,
    #                     )
    #                     if faiss_obj is not None:
    #                         # Proceed with using the deserialized FAISS index
    #                         print("FAISS index deserialized successfully.")
    #                     else:
    #                         print("Failed to deserialize FAISS index.")

    #                     st.session_state.vs = faiss_obj
    #                     st.session_state.current_kb_model = rag_name
    #                     st.rerun()
    #                     # Return the FAISS object
    #                 else:
    #                     st.warning("Please select a RAG to load.")
    #         with f2:
    #             if st.session_state.vs is not None:
    #                 if st.button("Unload RAG"):
    #                     st.session_state.vs = None
    #                     st.session_state.current_kb_model = ""
    #                     st.rerun()


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

    # with st.expander("Download Chatbot Responses"):
    #     st.session_state.download_response_flag = st.checkbox("Enable Download Responses")
