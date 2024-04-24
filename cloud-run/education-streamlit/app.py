import streamlit as st
import base64
import json
from io import StringIO ## for Python 3

import glob
import os
import re
import warnings

from tenacity import retry, stop_after_attempt, wait_random_exponential

import numpy as np
import pandas as pd
import textract
from PyPDF2 import PdfReader
from tenacity import retry, stop_after_attempt, wait_random_exponential
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel

warnings.filterwarnings("ignore")

import vertexai
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Part,
)

from vertexai.language_models import TextEmbeddingModel, TextGenerationModel

import gcs as gcs
import config as config

vertexai.init(project=config.PROJECT_ID, location=config.REGION)

st.set_page_config(layout="wide")

@st.cache_resource
def load_models():
    text_model_pro = GenerativeModel("gemini-pro")
    #text_model_pro = TextGenerationModel.from_pretrained("text-bison@001")

    multimodal_model_pro = GenerativeModel("gemini-pro-vision")
    return text_model_pro, multimodal_model_pro

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def text_generation_model_with_backoff(model, **kwargs):
    return model.predict(**kwargs).text


def get_gemini_pro_text_response(
    model: GenerativeModel,
    prompt: str,
    generation_config: GenerationConfig,
    stream: bool = True,
):
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }


    print("GENERATE")
    print(prompt)
    responses = model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=stream,
    )

    final_response = []
    for response in responses:
        try:
            # st.write(response.text)
            final_response.append(response.text)
        except IndexError:
            # st.write(response)
            final_response.append("")
            continue
    return " ".join(final_response)


def get_gemini_pro_vision_response(
    model, prompt_list, generation_config={}, stream: bool = True
):
    generation_config = {"temperature": 0.1, "max_output_tokens": 2048}
    responses = model.generate_content(
        prompt_list, generation_config=generation_config, stream=stream
    )
    final_response = []
    for response in responses:
        try:
            final_response.append(response.text)
        except IndexError:
            pass
    return "".join(final_response)


st.header("Aide aux devoirs", divider="rainbow",)
text_model_pro, multimodal_model_pro = load_models()

tab1, tab2,  = st.tabs(
    ["Aide pour apprendre une leçon", "Récompense", ]
)

df_questions = pd.DataFrame()
leçon = ""
response_questions = None
lecon_summary = ""
bt_verifier_reponses = None

@st.cache_data(persist=True)
def convert_df(response_questions):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    csvStringIO = StringIO(response_questions)
    df_questions = pd.read_csv(csvStringIO, sep="|")
    df_questions = df_questions.reset_index()  # make sure indexes pair with number of rows

    return df_questions


import json
import re

class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)



with tab1:
    st.write("Aide pour apprendre tes leçons")
    st.subheader("Intégre tes documents ici ")
    tab_text, tab_pdf,  = st.tabs(
    ["Texte simple", "PDF", ]
)
    with tab_text:
        print("refresh tab 1")

        leçon = st.text_area('copie/colle ici ta leçon', leçon, height = 600 )


        config = {
            "temperature": 0.05,
            "max_output_tokens": 2048,
        }

        prompt = f"""Write a bullet point summary in markown format with an higlligts of important words of this child lesson in FRENCH based on the following knowledge: \n
        lesson: {leçon} \n
        SUMMARY:
        """


        bt_summary      = st.button('Génére le résumé et les questions')
        #bt_questions    = st.button('Génére les questions')
        
        if leçon and (bt_summary==True):
            with st.spinner("Génération du résumé"):

                response = get_gemini_pro_text_response(
                    text_model_pro,
                    prompt = prompt,
                    generation_config=config,
                )

                lecon_summary = response
                if response:
                    st.write("Résumé du cours:")
                    st.markdown(response)
                
            with st.spinner("Génération des questions"):
                
                prompt_q = f"""Generate question to validate knowledge and the associate answers in an csv array of string splitted by "|" (headers: question, answer) in utf-8 of this child lesson in FRENCH based on the following knowledge: \n
                            Question need to be answerable with a simple word or small phrase
                            lesson: {lecon_summary} \n
                            CSV:
                            """                        
                response_questions = get_gemini_pro_text_response(
                    text_model_pro,
                    prompt = prompt_q,
                    generation_config=config,
                )
        

                if response_questions and lecon_summary : #and bt_questions:
                    st.write("Réponds aux questions de cours:")
                    st.write(response_questions)                    
                    #qa = str(response_questions)#.encode('utf-8') #.decode('unicode_escape')
                    # csvStringIO = StringIO(response_questions)
                    # df_questions = pd.read_csv(csvStringIO, sep=";")[:3]
                    df_questions = convert_df(response_questions)
                    st.dataframe(df_questions)
                    
                    df_questions.reset_index()  

        if df_questions != None :
            answers = []
            idx = 0
            for index, row in df_questions.iterrows():
                if len(row) >2:
                    if row[1]   and row[2] and isinstance(row[1], str)  and isinstance(row[2], str) :
                        idx = idx + 1

                        
                        question = row[1]
                        print(question)
                        #st.write(question) 
                        
                        answer = ""
                        answer = st.text_input(str(question), key = str(f"question - {idx}"))
                        
                        answers.append(answer)
                    else:
                        print("skip")
                    #, row[1])
            bt_verifier_reponses =st.button("vérifier mes réponses")
            
                    #qr_list = json.loads(qa)
                    # for question in qr_list:
                    #     st.write(question.question)
                    #     st.input_text(question.anwser)
        
        if bt_verifier_reponses and leçon and df_questions:
            for answer in answers:
                if answer.value:
                    print(answer.value)

            
                # if response_questions:
                #     st.write("Réponds aux questions de cours:")
                    
                    

    with tab_pdf:
        uploaded_files = st.file_uploader(label="Choisi tes leçons sous format pdf", type="pdf", accept_multiple_files=True,)

        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                # To read file as bytes:
                base64_pdf = base64.b64encode(uploaded_file.read()).decode("utf-8")

                file_data = uploaded_file.getvalue()
                
                pdf_display = (
                    f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                    'width="800" height="1000" type="application/pdf"></iframe>'
                    )
                st.markdown(pdf_display, unsafe_allow_html=True)

                #gcs.write_bytes_to_gcs("ml-demo-eu", "datasets/pdf/input/" + file_data,  file_data)
        
 
 

with tab2:
    st.write("Recompense")
    st.subheader("Tu as bien gagné une récompense ")
