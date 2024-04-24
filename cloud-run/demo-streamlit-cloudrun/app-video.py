import random
import time
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

st.set_page_config(layout="wide")

chatbot = False

@st.cache_resource
def load_models():
    try:
        text_model_pro = GenerativeModel("gemini-pro")
    except:
        print("ERROR  GenerativeModel(gemini-pro)")
        text_model_pro = None

    try:
        multimodal_model_pro = GenerativeModel("gemini-pro-vision")
    except:
        print("ERROR      GenerativeModel(gemini-pro-vision)")
        multimodal_model_pro = None
    try:
        image_model = ImageGenerationModel.from_pretrained("imagegeneration@005")
    except:
        print("ERROR     ImageGenerationModel.from_pretrained(imagegeneration@005)")
        image_model = None

    try:
        
        image2text_model = ImageTextModel.from_pretrained("imagetext@001")
    except:
        print("ERROR     ImageTextModel.from_pretrained(imagetext@001)")
        image2text_model = None

    return text_model_pro, multimodal_model_pro, image_model, image2text_model


@st.cache_data(persist=True)
def cache_data():
    from data import Story
    story = Story()
    return story

def get_gemini_pro_text_response(
    model: GenerativeModel,
    contents: str,
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


import data as data

print("init page")

st.header("Vertex AI Demo", divider="rainbow",)
text_model_pro, multimodal_model_pro, image_model, image2text_model = load_models()

story_data = cache_data()



@st.cache_data(persist=True)
def loadData():
     
    youtube_url_default = st.session_state.get("youtube_url_default", "https://www.youtube.com/watch?v=aZ3bX2v3uwo")
    # character_type_value = st.session_state.get("character_type", "Cat")
    # character_persona_value = st.session_state.get("character_persona", "Mitten is a very friendly cat.")
    # character_location_value = st.session_state.get("character_location", "Andromeda Galaxy")
    # story_premise_value = st.session_state.get("story_premise", ["Love", "Adventure"])
    return youtube_url_default #, character_type_value, character_persona_value, character_location_value, story_premise_value

def saveData(youtube_url_default#, character_type_value,character_persona_value,character_location_value,story_premise_value,story_premise_value
             ):
        st.session_state["youtube_url_default"] = youtube_url_default
        print("SaveData : "+youtube_url_default)

def submit():
    #st.session_state["youtube_url_default"] = youtube_url_default
    print("Save : "+st.session_state["youtube_url_default"])




youtube_url_default = loadData()
youtube_url =  st.text_input("youtube_url", value=youtube_url_default, )
bt_run_yt_transcript =st.button(
    "Export transcript from youtube video and summarize it using Gemini LLM", key="bt_run_yt_transcript"
)
video_id = youtube_url.split('v=')[-1]
st.components.v1.iframe(f"https://www.youtube.com/embed/{video_id}" , width=1000, height=500, scrolling=False) 

if bt_run_yt_transcript and youtube_url:
 
    transcripts = yt.get_transcript(youtube_url)

    text = ""
    for transcript in transcripts:
        text += transcript["text"] + "  "

    with st.expander("Transcript of youtube video", expanded=True):
        st.write(text)

    config_llm = {
        "temperature": 0.0,
        "max_output_tokens": 2048,
        "top_k" : 40,
        "top_p" : 1.0
    }

    with st.spinner("Generating summary with Gemini"):

        response_summary = get_gemini_pro_text_response_prompt(
            text_model_pro,
            "Summarize this youtube video:\n" + text,
            generation_config=config_llm,
        )
        if response_summary:
            with st.expander("Summary of youtube video", expanded=True):        
                st.write("# Summary of youtube video\n" + response_summary)
        




####

# Streamed response emulator
def response_generator():

    import langchainAgent as chat
    
    bot_response = chat.agent_chain.stream(prompt)
    if bot_response:
        yield bot_response
    else:
        return

  

if chatbot == True:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Comment puis-je vous aider ?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = response_generator()
            try:
                response = st.write_stream(stream)
            except:
                print()
        try:
        # Add assistant response to chat history        
            st.session_state.messages.append({"role": "assistant", "content": response})
        except:
            print()

    # # Initialize chat history
    # if "messages" not in st.session_state:
    #     st.session_state.messages = []

    # # Display chat messages from history on app rerun
    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])

    # # React to user input
    # if prompt := st.chat_input("What is up?"):
    #     # Display user message in chat message container
    #     st.chat_message("user").markdown(prompt)
    #     # Add user message to chat history
    #     st.session_state.messages.append({"role": "user", "content": prompt})

    #     response = f"Echo: {prompt}"
    #     # Display assistant response in chat message container
    #     with st.chat_message("assistant"):
    #         st.markdown(response)
    #     # Add assistant response to chat history
    #     st.session_state.messages.append({"role": "assistant", "content": response})
