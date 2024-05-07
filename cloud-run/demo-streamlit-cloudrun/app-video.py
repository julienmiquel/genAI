
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

# #Insert the script in the head tag of the static template inside your virtual environement
# GA_JS = """
# <!-- Global site tag (gtag.js) - Google Analytics -->
# <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
# <script>
#     window.dataLayer = window.dataLayer || [];
#     function gtag(){dataLayer.push(arguments);}
#     gtag('js', new Date());

#     gtag('config', 'G-7KGHD03GV1');
# </script>
# """

# a=os.path.dirname(st.__file__)+'/static/index.html'
# with open(a, 'r') as f:
#     data=f.read()
#     if len(re.findall('UA-', data))==0:
#         with open(a, 'w') as ff:
#             newdata=re.sub('<head>','<head>'+code,data)
#             ff.write(newdata)

import streamlit as st
import streamlit_analytics


#streamlit_analytics.track(firestore_key_file="firebase-key.json", firestore_collection_name="ia-video")

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

def inject_ga():
    """Add this in your streamlit app.py
    see https://github.com/streamlit/streamlit/issues/969
    """
    # new tag method
    GA_ID = "google_analytics"
    # NOTE: you should add id="google_analytics" value in the GA script
    # https://developers.google.com/analytics/devguides/collection/analyticsjs
    GA_JS = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-7KGHD03GV1');
</script>


"""
    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    # logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="lxml")

    if not soup.find(id=GA_ID):  # if cannot find tag
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # recover from backup
        else:
            shutil.copy(index_path, bck_index)  # keep a backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)

inject_ga()

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


st.set_page_config(page_title="Google Cloud AI (Gemini) - Automatic Video transcript and summary", layout="wide")
#st.title("Automatic Video Transcript and Summary")



chatbot = False

@st.cache_resource
def load_models():
    try:
        text_model_pro = GenerativeModel("gemini-1.5-pro-preview-0409")
    except:
        print("ERROR  GenerativeModel(gemini-pro)")
        text_model_pro = None
    return text_model_pro, None, None, None

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
import os

print(os.path.dirname(st.__file__))
print("init page")


header = st.header("Automatic Video Transcript and Summary power by Google Cloud AI (Gemini)", divider="rainbow",)
# header.markdown(
#     """
#         <!-- Global site tag (gtag.js) - Google Analytics -->
#         <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
#         <script>
#             window.dataLayer = window.dataLayer || [];
#             function gtag(){dataLayer.push(arguments);}
#             gtag('js', new Date());
#             gtag('config', 'G-7KGHD03GV1');
#         </script> 
        
#         <h2 id="automatic-video-transcript-and-summary-power-by-google-cloud-ai-gemini"><div data-testid="StyledLinkIconContainer" class="st-emotion-cache-zt5igj e1nzilvr4"><a href="#automatic-video-transcript-and-summary-power-by-google-cloud-ai-gemini" class="st-emotion-cache-eczf16 e1nzilvr3"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg></a><span class="st-emotion-cache-10trblm e1nzilvr1">Automatic Video Transcript and Summary power by Google Cloud AI (Gemini)</span></div></h2>
#         <hr data-testid="stHeadingDivider" color="linear-gradient(to right, #ff6c6c, #ffbd45, #3dd56d, #3d9df3, #9a5dff)" class="st-emotion-cache-16jumkr e1nzilvr0">
        
#     """, unsafe_allow_html=True
# )
text_model_pro, multimodal_model_pro, image_model, image2text_model = load_models()

#story_data = cache_data()


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

import streamlit.components.v1 as components


youtube_url_default = loadData()
youtube_url =  st.text_input("YouTube video url", value=youtube_url_default, )
bt_run_yt_transcript =st.button(
    "Export transcript from youtube video and summarize it using Gemini LLM", key="bt_run_yt_transcript"
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

# bt_run_yt_download =st.button(
#     "Download youtube video and summarize it using Gemini multimodal LLM", key="bt_run_yt_download"
# )

# if bt_run_yt_download and video_id:
#     from pytube import YouTube
#     YouTube(f'https://youtu.be/{video_id}').streams.first().download(filename=f"{video_id}.mp4")
    
#     #open media file  
#     with io.open(f"{video_id}.mp4", 'rb') as f:
#         f.seek(0)
#         media_data = f.read()
    
#     #upload media file to gcs    
#     gcs_uri_input = gcs.write_bytes_to_gcs(config.BUCKET, "datasets/youtube/video/" + f"{video_id}.mp4",  media_data, "binary/octet-stream")
#     st.write(gcs_uri_input)



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





# bootstrap 4 collapse example
# st.components.v1.html("""
# <!-- Google tag (gtag.js) -->
# <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
# <script>
#   window.dataLayer = window.dataLayer || [];
#   function gtag(){dataLayer.push(arguments);}
#   gtag('js', new Date());

#   gtag('config', 'G-7KGHD03GV1');
                      
# </script>
                      
# """)
# script = """ 
# <script type="module">
#   // Import the functions you need from the SDKs you need
  
#   import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-app.js";
#   import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-analytics.js";
#   // TODO: Add SDKs for Firebase products that you want to use
#   // https://firebase.google.com/docs/web/setup#available-libraries

#   // Your web app's Firebase configuration
#   // For Firebase JS SDK v7.20.0 and later, measurementId is optional
#   const firebaseConfig = {
#     apiKey: "AIzaSyBlicYGLYyFhhNLd35wE2JrDVUM4va3thw",
#     authDomain: "ml-demo-384110.firebaseapp.com",
#     databaseURL: "https://ml-demo-384110-default-rtdb.europe-west1.firebasedatabase.app",
#     projectId: "ml-demo-384110",
#     storageBucket: "ml-demo-384110.appspot.com",
#     messagingSenderId: "1008225662928",
#     appId: "1:1008225662928:web:25b205cbca00004af96bd5",
#     measurementId: "G-DSQBJJBYB2"
#   };

#   // Initialize Firebase
#   const app = initializeApp(firebaseConfig);
#   const analytics = getAnalytics(app);

#   </script>
# """ 

# script2 = """
# </script>        
#         <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
#         <script>
#             window.dataLayer = window.dataLayer || [];
#             function gtag(){dataLayer.push(arguments);}
#             gtag('js', new Date());
#             gtag('config', 'G-7KGHD03GV1');
#         </script>
#         """

# st.markdown(script2, unsafe_allow_html=True, allow_javascript=True, allow_html=True)

st.markdown("> **Build with** ❤️  by  **[\@julienmiquel](mailto:julienmiquel@google.com)**")

# st.markdown(script2, unsafe_allow_html=True)
# def inject_ga():

#     st.markdown(
#     """
#         <!-- Global site tag (gtag.js) - Google Analytics -->
#         <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
#         <script>
#             window.dataLayer = window.dataLayer || [];
#             function gtag(){dataLayer.push(arguments);}
#             gtag('js', new Date());
#             gtag('config', 'G-7KGHD03GV1');
#         </script>
#     """, unsafe_allow_html=True)

#     GA_ID = "google_analytics"


#     GA_JS = """
#     <!-- Global site tag (gtag.js) - Google Analytics -->
#     <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
#     <script>
#         window.dataLayer = window.dataLayer || [];
#         function gtag(){dataLayer.push(arguments);}
#         gtag('js', new Date());

#         gtag('config', 'G-7KGHD03GV1');
#     </script>
#     """
#  # Insert the script in the head tag of the static template inside your virtual
#     index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
#     #logging.info(f'editing {index_path}')
#     soup = BeautifulSoup(index_path.read_text(), features="html.parser")
#     if not soup.find(id=GA_ID): 
#         bck_index = index_path.with_suffix('.bck')
#         if bck_index.exists():
#             shutil.copy(bck_index, index_path)  
#         else:
#             shutil.copy(index_path, bck_index)  
#         html = str(soup)
#         new_html = html.replace('<head>', '<head>\n' + GA_JS)
#         index_path.write_text(new_html)

# try:
#     inject_ga()
# except Exception as e:
#     print(e)
#     pass

#streamlit_analytics.stop_tracking(firestore_key_file="firebase-key.json", firestore_collection_name="ia-video")