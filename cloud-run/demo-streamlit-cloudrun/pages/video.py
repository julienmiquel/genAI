import json
import io
import pathlib
import random
import shutil
import time
from bs4 import BeautifulSoup
import streamlit as st
from vertexai.vision_models import ImageTextModel

from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Image,
    Part,
)
import vertexai
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Part,
)
from vertexai.preview.vision_models import (
    Image, 
    ImageGenerationModel
)

import youtubeAPI as yt
import gcs as gcs
import config as config

vertexai.init(project=config.PROJECT_ID, location=config.REGION)


import streamlit as st
import streamlit_analytics


from google.cloud import firestore

#Add a new user to the database
# db = firestore.Client()
# doc_ref = db.collection('users').document('alovelace')
# doc_ref.set({
#     'first': 'Ada',
#     'last': 'Lovelace',
#     'born': 1815
# })

# # Then query to list all users
# users_ref = db.collection('users')

# for doc in users_ref.stream():
#     print('{} => {}'.format(doc.id, doc.to_dict()))

# or pass the same args to `start_tracking` AND `stop_tracking`

# import streamlit.components.v1 as components

# from jinja2 import Template
#  # Load the Jinja2 template
# with open("static/index.html", "r") as template_file:
#     template_content = template_file.read()
#     jinja_template = Template(template_content)

# rendered_html = jinja_template.render()

# # Display the HTML in Streamlit app
# components.html(rendered_html, height=000, scrolling=False)


import header as header
header.header("Automatic Video Transcript and Summary power by Google Cloud AI (Gemini)")

import app_sidebar
language_code_gemini, multimodal_model_name_gemini =  app_sidebar.get_sidebar_config()


@st.cache_resource
def load_models(multimodal_model_name_gemini):
    try:
        text_model_pro = GenerativeModel(multimodal_model_name_gemini)
    except:
        print("ERROR  GenerativeModel(gemini-pro)")
        text_model_pro = None
    return text_model_pro


@st.cache_data(persist=True)
def cache_data():
    from data import Story
    story = Story()
    return story

def get_gemini_pro_text_response(
    model: GenerativeModel,
    prompt: str,
    generation_config: GenerationConfig,
    stream: bool = True,
):
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

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

def get_gemini_pro_text_response_prompt(
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

def get_image_2_text_response(
    model, source_bytes, language="en"
):
    from PIL import Image as PIL_image
    from vertexai.vision_models import Image

    source_image = Image(source_bytes)
    captions = model.get_captions(
        image=source_image,
        # Optional:
        number_of_results=2,
        language=language,
    )
    return captions

config_llm = {
    "temperature": 0.0,
    "max_output_tokens": 2048,
    "top_k" : 40,
    "top_p" : 1.0
}


import data as data
import os

print(os.path.dirname(st.__file__))
print("init page")


multimodal_model_pro = load_models(multimodal_model_name_gemini)


@st.cache_data(persist=True)
def loadData():
     
    youtube_url_default = st.session_state.get("youtube_url_default", "https://www.youtube.com/watch?v=aZ3bX2v3uwo")

    return youtube_url_default #, character_type_value, character_persona_value, character_location_value, story_premise_value

def saveData(youtube_url_default#, character_type_value,character_persona_value,character_location_value,story_premise_value,story_premise_value
             ):
        st.session_state["youtube_url_default"] = youtube_url_default
        print("SaveData : "+youtube_url_default)

def submit():
    print("Save : "+st.session_state["youtube_url_default"])


youtube_url_default = loadData()
youtube_url =  st.text_input("YouTube video url", value=youtube_url_default, )

col1, col2, col3 = st.columns([8, 0.5, 8], gap="small")
with col1:
    bt_run_yt_transcript =st.button(
        "Export transcript from youtube video and summarize it using Gemini LLM", key="bt_run_yt_transcript"
    )    

with col2:
    st.write("or")

with col3:    
    bt_run_yt_download =st.button(
    "Download youtube video and summarize it using Gemini multimodal", key="bt_run_yt_download"
    )

try:    
    print(youtube_url)
    video_id = youtube_url.split('v=')[-1]
    print(video_id)
    video_id = video_id.split('&')[0]
    print(video_id)

except:
    pass

st.components.v1.iframe(f"https://www.youtube.com/embed/{video_id}" , width=1000, height=500, scrolling=False) 



if bt_run_yt_download and video_id:
    from pytube import YouTube
    
    from pytube.innertube import _default_clients

    _default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]    
    ytvideo = YouTube(f'https://youtu.be/{video_id}')
    
    
    local_video_file = f"{ytvideo.author}-{ytvideo.title}-{video_id}.mp4"
    local_desc_file = f"{ytvideo.author}-{ytvideo.title}-{video_id}.json"

    local_video_file = local_video_file.replace(" ", "_").replace(":", "_").replace("/", "_").replace("\\", "_").replace("|", "_")
    local_desc_file = local_desc_file.replace(" ", "_").replace(":", "_").replace("/", "_").replace("\\", "_").replace("|", "_")



    ytvideo.streams.first().download(filename=local_video_file)
    
    #open media file  
    with io.open(local_video_file, 'rb') as f:
        f.seek(0)
        media_data = f.read()
    
    #upload media file to gcs    
    gcs_uri_input = gcs.write_bytes_to_gcs(config.BUCKET, "datasets/youtube/video/" + f"{local_video_file}",  media_data, "binary/octet-stream")
    st.write(gcs_uri_input)

    # gcs_uri_input_signed = gcs.generate_download_signed_url(gcs_uri_input)
    # st.video(gcs_uri_input_signed)



    video_highlights_url = (
    "https://storage.googleapis.com/" + gcs_uri_input.split("gs://")[1]
    )
    if video_highlights_url:
        video_highlights_img = Part.from_uri(
            gcs_uri_input, mime_type="video/mp4"
        )
        # st.video(gcs_uri_input_signed)

        with st.spinner("Generating video transcript using Gemini in real-time..."):
            prompt = f"Summarize this youtube video. Answer in {language_code_gemini}." 

            import gemini as gemini
            results = gemini.generate_transcript_from_audio(video_highlights_img, language_code_gemini, multimodal_model_name_gemini)
            #st.write_stream(results[0])
            
            with st.expander(f"Transcript generated in real-time by gemini {multimodal_model_name_gemini}", expanded=True):
                for result in results:
                    if result[0] is not None:
                        st.write(result[0])                    

                    if result[1] is not None:
                        generated_transcript = result[1]
                        
        with st.expander(f"Transcript generated in real-time by gemini {multimodal_model_name_gemini}", expanded=True):
            #st.markdown(generated_transcript)
            st.markdown("```json:\n" + generated_transcript.replace(",",",\n") + "\n```")

            # response = get_gemini_pro_vision_response(
            # multimodal_model_pro, [prompt, video_highlights_img]
            # )
            # st.markdown(response)
            # st.markdown("\n\n\n")

        with st.spinner("Generating summary with Gemini"):
            prompt_summary = f"Summarize this youtube video. Use the language code to answer {language_code_gemini}. <Transcript>{generated_transcript}</Transcript>"
            with st.expander("Prompt", expanded=False):
                st.write(prompt_summary)

            response_summary = get_gemini_pro_text_response_prompt(
                multimodal_model_pro,
                prompt_summary,
                generation_config=config_llm,
            )
            if response_summary:
                with st.expander(f"Summary of youtube video in {language_code_gemini}", expanded=True):                        
                    st.markdown("# Summary of youtube video")
                    st.markdown(response_summary)

            # try:
            #     generated_transcript_json = json.load(generated_transcript)
            # except Exception as e:
            #     print(e)            
            #     generated_transcript_json =None

            with open(local_desc_file, 'w') as f:
                json.dump({
                    "author": ytvideo.author,
                    "title": ytvideo.title,
                    "description": ytvideo.description,
                    "summary": response_summary,
                    #"transcript": generated_transcript_json,                                        
                }, f, indent=4)
        


if bt_run_yt_transcript and youtube_url:
 
    transcripts = yt.get_transcript(youtube_url)

    text = ""
    if transcripts:
        for transcript in transcripts:
            text += transcript["text"] + "  "

        with st.expander("Transcript of youtube video", expanded=True):
            st.write(text)



        with st.spinner("Generating summary with Gemini"):

            response_summary = get_gemini_pro_text_response_prompt(
                multimodal_model_pro,
                f"Summarize this youtube video. Answer in {language_code_gemini}. <Transcript> {text} </Transcript>" ,
                generation_config=config_llm,
            )
            if response_summary:
                with st.expander(f"Summary of youtube video in {language_code_gemini}", expanded=True):        
                    st.write("# Summary of youtube video\n" + response_summary)
            
    else:
        st.write("No transcripts found")





from app_footer import footer
footer(st)
