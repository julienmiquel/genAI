import streamlit as st
import config

def get_sidebar_config():
    with st.sidebar:
        language_code_gemini =  st.text_input("language_code_gemini", value="fr-FR", )
        multimodal_model_name_gemini =  st.selectbox("multimodal_model_name_gemini",options=[config.GEMINI_MULTIMODAL_MODEL_NAME, "gemini-1.5-pro-001", "gemini-experimental","gemini-1.5-pro-preview-0409"],key= config.GEMINI_MULTIMODAL_MODEL_NAME)
    return language_code_gemini, multimodal_model_name_gemini


