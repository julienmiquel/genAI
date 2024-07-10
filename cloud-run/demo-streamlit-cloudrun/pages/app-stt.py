import datetime
import io
import json
import os
import random
import time
import streamlit as st
from gemini import generate_chaptering_from_audio
from gemini import       generate_transcript_from_audio
import videoedit as videoedit
import utils as utils

from vertexai.vision_models import ImageTextModel
from google.api_core.exceptions import InvalidArgument

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

import gcs as gcs
import config as config

vertexai.init(project=config.PROJECT_ID, location=config.REGION)

st.set_page_config(page_title="Google Cloud AI Demos (Gemini) - STT Gemini Demos", layout="wide")

chatbot = False

@st.cache_data(persist=True)
def cache_index():      
    return 1

@st.cache_resource
def load_models():
    try:
        text_model_pro = GenerativeModel("gemini-pro")
    except:
        print("ERROR  GenerativeModel(gemini-pro)")
        text_model_pro = None

    try:
        multimodal_model_pro = GenerativeModel(config.GEMINI_MULTIMODAL_MODEL_NAME)
    except:
        print(f"ERROR      GenerativeModel({config.GEMINI_MULTIMODAL_MODEL_NAME})")
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


st.header("Vertex AI Demo", divider="rainbow", anchor="vertex")
text_model_pro, multimodal_model_pro, image_model, image2text_model = load_models()

import app_sidebar
language_code_gemini, multimodal_model_name_gemini =  app_sidebar.get_sidebar_config()


def stt_generate_summary(text_to_generate_podcast, prompt_content_balise_start, prompt_content_balise_stop):
    config_llm = {
        "temperature": 0.2,
        "max_output_tokens": 6144,
        "top_p": 1.0,                    
    }
    podcast_summary_prompt = f"""{prompt_content_balise_start}
        {text_to_generate_podcast}
        {prompt_content_balise_stop}
<TASK>
Summarize CONTENT in FRENCH to be read in a podcast.
</TASK>
        """
                    
    text_summary_to_generate_podcast = get_gemini_pro_text_response_prompt(
                        multimodal_model_pro, podcast_summary_prompt,generation_config=config_llm
                    )
    
    
    print(text_summary_to_generate_podcast)
    return podcast_summary_prompt,text_summary_to_generate_podcast

def stt_generate_title( prompt_content_balise_start, prompt_content_balise_stop, text_summary_to_generate_podcast):
    podcast_title_prompt = f"""{prompt_content_balise_start}
        {text_summary_to_generate_podcast}
        {prompt_content_balise_stop}
<TASK>
Create a short title in ENGLISH in one sentence based on this content.
</TASK>
        """

                    # SSML generation
    config_llm = {
                        "temperature": 0.1,
                        "max_output_tokens": 8192,
                        "top_p": 1.0,                    
                    }

    podcast_title = get_gemini_pro_text_response_prompt(
                        multimodal_model_pro, podcast_title_prompt,generation_config=config_llm
                    )
    
    podcast_title = podcast_title.encode('ascii', 'ignore').decode('ascii')
    podcast_title = podcast_title.replace("'", " ").replace(":"," ").replace("//"," ").replace("\\"," ").replace(","," ").replace("  "," ")
    

    return podcast_title


st.subheader("Audio & video - STT Chirp", anchor="STT")
#st.write("Audio & video - STT Chirp")


stt_stream, podcast_all, gemini_stt, stt, video  = st.tabs(
    ["STT Streaming","Podcast every-things", "Gemini as STT", "STT Chirp" , "video - youtube"]
)



with stt_stream:
    wav_audio_data = None
    from st_audiorec import st_audiorec
    wav_audio_data = st_audiorec() # tadaaaa! yes, that's it! :D

    # from audio_recorder_streamlit import audio_recorder
    # wav_audio_data_2 = audio_recorder()

    # recorded_prompt = stt(speech=msgs_to_compare["user_audio"]).text
    # if wav_audio_data:
    #     st.audio(audio_bytes, format="audio/wav")

    # import numpy as np
    # from io import BytesIO
    # import streamlit.components.v1 as components
    # # get parent directory relative to current directory
    # parent_dir = os.path.dirname(os.path.abspath(__file__))
    # # Custom REACT-based component for recording client audio in browser
    # build_dir = os.path.join(parent_dir, "frontend/build")
    # # specify directory and initialize st_audiorec object functionality
    # st_audiorec = components.declare_component("st_audiorec", path=build_dir)

    # # Create an instance of the component: STREAMLIT AUDIO RECORDER
    # raw_audio_data = st_audiorec()  # raw_audio_data: stores all the data returned from the streamlit frontend
    # wav_bytes = None                # wav_bytes: contains the recorded audio in .WAV format after conversion

    # # the frontend returns raw audio data in the form of arraybuffer
    # # (this arraybuffer is derived from web-media API WAV-blob data)

    # if isinstance(raw_audio_data, dict):  # retrieve audio data
    #     with st.spinner('retrieving audio-recording...'):
    #         ind, raw_audio_data = zip(*raw_audio_data['arr'].items())
    #         ind = np.array(ind, dtype=int)  # convert to np array
    #         raw_audio_data = np.array(raw_audio_data)  # convert to np array
    #         sorted_ints = raw_audio_data[ind]
    #         stream = BytesIO(b"".join([int(v).to_bytes(1, "big") for v in sorted_ints]))
    #         transcribe_streaming(stream)
    #         # wav_bytes contains audio data in byte format, ready to be processed further
    #         wav_bytes = stream.read()
    #         wav_audio_data  = wav_bytes

    

    # add some spacing and informative messages
    col_info, col_space = st.columns([0.57, 0.43])
    with col_info:
        st.write('\n')  # add vertical spacer
        st.write('\n')  # add vertical spacer
        st.write('The .wav audio data, as received in the backend Python code,'
                ' will be displayed below this message as soon as it has'
                ' been processed. [This informative message is not part of'
                ' the audio recorder and can be removed easily] 🎈')

    # if wav_audio_data_1 is not None:
    #     wav_audio_data = wav_audio_data_1
    # if wav_audio_data_2 is not None:
    #     wav_audio_data = wav_audio_data_2            
    if wav_audio_data is not None:
        # display audio data as received on the Python side
        col_playback, col_space = st.columns([0.58,0.42])
        with col_playback:
            file_name = f"recording_audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
            gcs_uri_input, gcs_uri_output, mime_type = utils.save_sound_gcs(file_name,wav_audio_data)

            st.audio(wav_audio_data, format=mime_type)
            audio = Part.from_uri(gcs_uri_input, mime_type=mime_type) 
            results = generate_transcript_from_audio(audio, language=language_code_gemini, model=multimodal_model_name_gemini)
            for result in results:
                if result[0] is not None:
                    st.write(result[0])                    

                if result[1] is not None:
                    final_res = result[1]
                
                        
            gcs.write_string_to_bucket(config.BUCKET, f"/datasets/transcript/{file_name}/",final_res)
        

        st.markdown(f"Final result also available here: {gcs_uri_output}")
        st.markdown(f"""```json
{final_res}
```
""")
        json.dump(final_res, open(f"{file_name}.json", "w"))

        st.write("STT done")




with podcast_all:
    st.markdown(
        """Podcast every-things"""
    )
    text_to_generate_podcast =  st.text_area("text_to_generate_podcast", value="" )
    url_to_generate_podcast =  st.text_input("url_to_generate_podcast", value="" )
    #youtube_url_to_generate_podcast =  st.text_input("youtube_url_to_generate_podcast", value="" )

    generate_podcast = st.button(
        "Generate podcast from content", key="generate_podcast"
    )

    # 1) Get text and generate prompt

    #         Use language voice identifier to generate differente voice chunch.
    # Use voice in this list to alternate :

    prompt_task = """<TASK>
You are an SSML generator. You produce very high actor by variate the prosody, pitch, emphasis...        
Transform the following content into a podcast script in FRENCH and respect the SSML format.
The content is suitable for a advanced tech guys on all the topic described between CONTENT tags.
The output is a valide SSML format.
SSML format is The Speech Synthesis Markup Language is an XML application. The root element is speak.
Do not use <voice> tags.

Only generate valide SSML.
Check twice the SSML is valide.
BE SURE TO GENERATE VALIDE SSML.        
    </TASK>"""
    prompt_content_balise_start = "<CONTENT>"
    prompt_content_balise_stop = "</CONTENT>"

    prompt_FORMAT = """<FORMAT> Use the following format:
    fr-FR-Studio-A:text...        fr-FR-Studio-D:text...        fr-FR-Wavenet-A:text...        fr-FR-Wavenet-B:text...
    fr-FR-Wavenet-D:text...        fr-FR-Wavenet-E:text...
        </FORMAT>"""
    
    prompt_FORMAT = """<OUTPUT_FORMAT>
Generate SSML with various French voice:
- 'fr-FR-Studio-A'
- 'fr-FR-Studio-D'
- 'fr-FR-Wavenet-A'
- 'fr-FR-Wavenet-B'
- 'fr-FR-Wavenet-D'
- 'fr-FR-Wavenet-E'

Example of valide SSML format:
<speak>
<say-as interpret-as='currency' language='fr-FR'>42,01 €</say-as>
<say-as interpret-as="verbatim">LLM</say-as>
<say-as interpret-as="characters">LLM</say-as>
<say-as interpret-as="characters">IA</say-as>
<sub alias="World Wide Web Consortium">W3C</sub>
<sub alias="Les Grands Modèles de Langage">LLMs</sub>
<sub alias="Intelligence ">IA</sub>
<say-as interpret-as="cardinal">12345</say-as>
<s><prosody rate="medium" pitch="+2st">Salut  les techos ! Aujourd'hui, on plonge dans l'univers fascinant de l'IA générative et de l'orchestration des modèles de langage.</s></s>
<p>
    <s><prosody rate="fast" pitch="+3st">Yo les développeurs ! Prêts à booster vos projets avec l'IA générative ?</s></s>
    <s>Workflows débarque pour orchestrer vos LLMs et automatiser des  tâches de fou, comme le résumé de documents longs.</s>
    <s>Fini les prises de tête avec les frameworks d'orchestration, Workflows simplifie tout !</s> 
</p>
<emphasis level="moderate">This is an important announcement</emphasis>

Step 1, take a deep breath. <break time="200ms"/>
Step 2, exhale.
Step 3, take a deep breath again. <break strength="weak"/>
Step 4, exhale.

Here are <say-as interpret-as="characters">SSML</say-as> samples.
I can pause <break time="3s"/>.  
I can speak in cardinals. Your number is <say-as interpret-as="cardinal">10</say-as>.
Or I can speak in ordinals. You are <say-as interpret-as="ordinal">10</say-as> in line.
Or I can even speak in digits. The digits for ten are <say-as interpret-as="characters">10</say-as>.
I can also substitute phrases, like the <sub alias="World Wide Web Consortium">W3C</sub>.
Finally, I can speak a paragraph with two sentences.
<p><s>This is sentence one.</s><s>This is sentence two.</s></p>
</speak>

</OUTPUT_FORMAT>"""

        
#
    if url_to_generate_podcast:
        text_to_generate_podcast =None
        #Code to get text from webpage from an url
        from bs4 import BeautifulSoup
        import requests
        response = requests.get(url_to_generate_podcast)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_to_generate_podcast = soup.get_text()
        
        # regex to find mp3 href in text_to_generate_podcast
        import re
        match = re.search(r'href="(.*?)"', text_to_generate_podcast)
        if match:
            mp3_url = match.group(1)
            st.write(f"Found MP3 URL: {mp3_url}")
            print(f"Found MP3 URL: {mp3_url}")
        else:
            print("No MP3 URL found.")
        
        
        with st.expander(f"Text from {url_to_generate_podcast}", expanded=False):
            st.write(text_to_generate_podcast)
            print(text_to_generate_podcast)
        


    # 2) Generate script
    if generate_podcast and text_to_generate_podcast and len(text_to_generate_podcast) > 0:

            with st.spinner("Generating summary using Gemini..."):
                podcast_summary_prompt, text_summary_to_generate_podcast = stt_generate_summary(text_to_generate_podcast, prompt_content_balise_start, prompt_content_balise_stop)
                with st.expander("Summary", expanded=True):    
                    st.markdown(text_summary_to_generate_podcast)

            with st.spinner("Generating podcast title using Gemini..."):                    
            #     podcast_title = stt_generate_title( prompt_content_balise_start, prompt_content_balise_stop, text_summary_to_generate_podcast)
            #     podcast_title = podcast_title.replace("#","").replace("*","")
            #     st.markdown(f"# TITLE : {podcast_title}")
            #     print(podcast_title)
                podcast_title = stt_generate_title( prompt_content_balise_start, prompt_content_balise_stop, text_summary_to_generate_podcast)                            
            st.write(podcast_title)
            print(podcast_title)

            with st.spinner(f"Generating SSML {podcast_title} using Gemini..."):                    
                # SSML generation
                config_llm = {
                                    "temperature": 0.1,
                                    "max_output_tokens": 8192,
                                    "top_p": 1.0,                    
                                }

                podcast_prompt = f"""
            {prompt_content_balise_start}
            {text_summary_to_generate_podcast}
            {prompt_content_balise_stop}
            {prompt_FORMAT}
            {prompt_task}
            """

            #     text_summary_to_generate_podcast = get_gemini_pro_text_response_prompt(
            #         multimodal_model_pro, podcast_prompt,generation_config=config_llm
            #     )
            #     st.write(text_summary_to_generate_podcast)
            #     print(text_summary_to_generate_podcast)

            #     print(podcast_prompt)

            with st.spinner(f"Generating SSML podcast for {podcast_title} using Gemini..."):             
                response_ssml = get_gemini_pro_text_response_prompt(
                    multimodal_model_pro, podcast_prompt,generation_config=config_llm
                )
                ssml = response_ssml.replace("</ ", "</").replace("  ", " ").replace("**", "*").replace("##", "#").replace("fr-FR ","fr-FR").replace("fr- ","fr-").replace("pros ody", "prosody")
                with st.expander("SSML Gen 1", expanded=False):    
                    st.markdown(response_ssml)
                

            # with st.spinner(f"Generating Gen 2"):             

            #     response_ssml = get_gemini_pro_text_response_prompt(
            #                             multimodal_model_pro, 
            #                             f"""PROVIDE valide SSML document and solve error based on this document:
            #                               {response_ssml}""",
            #                             generation_config=config_llm
            #                         )
            #     with st.expander("SSML Gen 2", expanded=False):    
            #         st.markdown(response_ssml)
                                    

    # 3) Generate speech

    
    # if generate_podcast_speech:
            if response_ssml:
                with st.expander("SSML generation", expanded=True):        
                    st.write("# SSML generation" )
                    import text2speech as speech
                    import utils as utils
                    mp3_chunck = []
                    mp3_localFiles = []
                    ssml = response_ssml.replace("</ ", "</").replace("**", "*").replace("##", "#").replace("fr-FR ","fr-FR").replace("fr- ","fr-").replace("pros ody", "prosody")
                    chuncks = utils.extract_speak_content(ssml)                    
                    index = 0
                    podcast_chunck_file = f"podcast_{utils.create_timestamped_name('podcast')}"
                    for chunck in chuncks:                    
                        try:
                            print(80*"-")
                            print(f"chunck: {chunck}")
                            index_speak = f"{chunck}".find("<speak>")
                            if index_speak == -1:
                                chunck = f"<speak>{chunck}</speak>"
                                print("add speak tag")
                                st.markdown(chunck)

                            st.markdown(f"# chunck: {index} ")
                            
                            speech_file = f"{podcast_chunck_file}_{index}.mp3"
                            
                            index = index + 1
                            speech_path = "podcasts/"
                            speech_output=    f"gs://{config.BUCKET}/{speech_path}{speech_file}"
                            mp3_chunck.append(speech_output)
                            
                            print(f"speech_output: {speech_output}")                        

                            with st.spinner("Generating podcast TTS..."):
                                #speech_result = speech.synthesize_long_audio(response, speech_output,language_code="fr-FR", voice_name="fr-FR-Studio-A")
                                # gcs.store_temp_video_from_gcs(config.BUCKET,f"{speech_path}{speech_file}", speech_file)
                                # audio_file = open(speech_file, "rb")
                                # audio_bytes = audio_file.read()                        
                                audio_bytes, speech_file  = speech.synthesize_text(chunck, language_code="fr-FR", voice_name="fr-FR-Wavenet-A", output_file=speech_file)
                                
                                #st.markdown(speech_result)


                                st.audio(audio_bytes, format="audio/mp3")
                                gcs.write_file_to_gcs(config.BUCKET,f"{speech_path}{speech_file}",speech_file)
                                mp3_localFiles.append(speech_file)
                        except InvalidArgument as e :
                            st.markdown(e)                            
                        
                with st.expander("Final podcast", expanded=True):        
                    
                    if len(mp3_localFiles) > 0:
                        
                        complete_filename = f"{podcast_chunck_file}_complete.mp3"
                        complete_filename = videoedit.combine_audio_files(mp3_localFiles, complete_filename)
                        with open(complete_filename, "rb") as audio_file:
                            audio_bytes = audio_file.read()

                            st.audio(audio_bytes, "audio/mp3")
                            gcs.write_file_to_gcs(config.BUCKET,f"{complete_filename}",complete_filename)

                            import pandas as pd
                            import bq 
                            df = pd.DataFrame(columns=["mp3", "title", "text_to_generate_podcast", "source_url"])
                            df["mp3"] = [f"gs://{config.BUCKET}/{complete_filename}"                            ]
                            df["title"] = [stt_generate_title( prompt_content_balise_start, prompt_content_balise_stop, text_to_generate_podcast)                            ]
                            df["text_to_generate_podcast"] = [text_summary_to_generate_podcast]
                            df["source_url"] = [url_to_generate_podcast]
                            df["update_time"] = [datetime.datetime.now()]
                            # if url_to_generate_podcast:
                            #     df["source_url"] = url_to_generate_podcast
                            # else:
                            #     df["source_url"] = ""

                            bq.save_unsafe_bq(df,"podcasts.feed", config.PROJECT_ID, False)
                    else:
                        st.markdown("# No audio generated")



with gemini_stt:
    st.markdown(
        """Gemini as STT"""
    )

    #multimodal_model_name_gemini =  st.text_input("multimodal_model_name_gemini", value=config.GEMINI_MULTIMODAL_MODEL_NAME, )


    uploaded_sound_to_bucket = st.file_uploader("Choose a audio file", type=None)
    if uploaded_sound_to_bucket is not None:
        # To read file as bytes:
        media_data = uploaded_sound_to_bucket.getvalue()
        #st.write(media_data)
        gcs_uri_input, gcs_uri_output, mime_type = utils.save_sound_gcs(uploaded_sound_to_bucket.name, media_data)
        st.audio(media_data, format=mime_type)

    bt1_stt, _,bt2_chaptering = st.columns([0.1,0.8,0.1])
    
    with bt1_stt:
        bt_run_stt_gemini =st.button(
            "Run STT", key="bt_run_stt_gemini"
        )
    with bt2_chaptering:        
        bt_run_chaptering_gemini =st.button(
            "Run chaptering", key="bt_run_chaptering_gemini"
        )

    if bt_run_stt_gemini and language_code_gemini  and gcs_uri_input and gcs_uri_output:
        
        
        final_res= ""
        with st.spinner(f"Generating STT using Gemini model: {multimodal_model_name_gemini}..."):
            
            audio = Part.from_uri(gcs_uri_input, mime_type=mime_type) 

            results = generate_transcript_from_audio(audio, language=language_code_gemini, model=multimodal_model_name_gemini)
            for result in results:
                if result[0] is not None:
                    st.write(result[0])                    

                if result[1] is not None:
                    final_res = result[1]
                
            
            import gcs as gcs

            
            gcs.write_string_to_bucket(config.BUCKET, f"/datasets/transcript/{uploaded_sound_to_bucket.name}/",final_res)
        

        st.markdown(f"Final result also available here: {gcs_uri_output}")
        st.markdown(f"""```json
{final_res}
```
""")
        json.dump(final_res, open(f"{uploaded_sound_to_bucket.name}.json", "w"))

        st.write("STT done")
                    
    
    if bt_run_chaptering_gemini and language_code_gemini  and gcs_uri_input and gcs_uri_output:
        from gemini import       generate_transcript_from_audio
        
        final_res= ""
        with st.spinner(f"Generating chaptering using Gemini model: {multimodal_model_name_gemini}..."):
            
            audio = Part.from_uri(gcs_uri_input, mime_type=mime_type) 

            results = generate_chaptering_from_audio(audio, language=language_code_gemini, model=multimodal_model_name_gemini)
            for result in results:
                if result[0] is not None:
                    st.write(result[0])                    

                if result[1] is not None:
                    final_res = result[1]
                
            
            import gcs as gcs

                            
            gcs.write_string_to_bucket(config.BUCKET, f"/datasets/transcript/{uploaded_sound_to_bucket.name}/",final_res)
        
        st.markdown(f"Final result also available here: {gcs_uri_output}")
        final_res = final_res.replace("},","}\n,\n")
        st.markdown(f"""```json
{final_res}
```
""")
        st.write("STT done")


with stt:
    st.markdown(
        """STT"""
    )
    
    language_code =  st.text_input("language_code", value="fr-FR", )
    REGION =  st.text_input("REGION", value="europe-west4", )

    bt_create_recognizer =st.button(
        "Create recognizer", key="bt_create_recognizer"
    )

    if bt_create_recognizer and language_code and REGION :
        from stt import       get_recognizer
        recognizer = get_recognizer(language_code)
        # from google.cloud.speech_v2 import SpeechClient
        # from google.cloud.speech_v2.types import cloud_speech
        # from google.api_core.client_options import ClientOptions            
        # client = SpeechClient(
        # client_options=ClientOptions(api_endpoint=f"{REGION}-speech.googleapis.com")
        # )
        # recognizer_id = f"chirp-{language_code.lower()}-demo"

        # recognizer_request = cloud_speech.CreateRecognizerRequest(
        #     parent=f"projects/{config.PROJECT_ID}/locations/{config.REGION}",
        #     recognizer_id=recognizer_id,
        #     recognizer=cloud_speech.Recognizer(
        #         language_codes=[language_code],
        #         model="chirp",
        #     ),
        # )
        # create_operation = client.create_recognizer(request=recognizer_request)
        # recognizer = create_operation.result()
        st.write("STT recognizer created: " + recognizer.name)
        recognizer_id = recognizer.name

    import config as config

    uploaded_file_to_bucket = st.file_uploader("Choose a video or audio file")
    if uploaded_file_to_bucket is not None:
        # To read file as bytes:
        media_data = uploaded_file_to_bucket.getvalue()
        st.write(media_data)
        print(f"BUCKET_NAME: {config.BUCKET}")
        gcs_uri_input = gcs.write_bytes_to_gcs(config.BUCKET, "datasets/input/" + uploaded_file_to_bucket.name,  media_data, "binary/octet-stream")
        print(f"gcs_uri_input: {gcs_uri_input}")
        gcs_uri_output = f"gs://{config.BUCKET}/datasets/transcript/{uploaded_file_to_bucket.name}/"
        print(f"gcs_uri_output: {gcs_uri_output}")

    bt_run_stt =st.button(
        "Run STT", key="bt_run_stt"
    )
    

    if bt_run_stt and language_code  and gcs_uri_input and gcs_uri_output:
        from stt import       transcribe_gcs            
        # transcribe_gcs(gcs_uri_input, gcs_uri_output, language_code, recognizer_id)
        with st.spinner("Generating STT using Chirp..."):

            result = transcribe_gcs(gcs_uri_input, gcs_uri_output, language_code)
            #st.write(result.result.transcripts[0].transcript)
            st.write("STT done")
            
with video:
    st.markdown(
        """video"""
    )   
    import youtubeAPI as yt
    youtube_url =  st.text_input("youtube_url", value="https://www.youtube.com/watch?v=aZ3bX2v3uwo" )
    bt_run_yt_transcript =st.button(
        "Export transcript from youtube video and summarize it using Gemini LLM", key="bt_run_yt_transcript"
    )
    
    if bt_run_yt_transcript and youtube_url:
        transcripts = yt.get_transcript(youtube_url)

        text = ""
        for transcript in transcripts:
            text += transcript["text"] + "  "
        st.write(text)

        response_summary = get_gemini_pro_text_response_prompt(
            text_model_pro,
            "Summarize this youtube video:\n" + text,
            generation_config=config_llm,
        )
        if response_summary:
            st.write("# Summary of youtube video\n" + response_summary)
            




####



from app_footer import footer
footer(st)




# def transcribe_streaming(stream_file: str) -> speech.RecognitionConfig:
#     """Streams transcription of the given audio file."""
#     from google.cloud import speech

#     client = speech.SpeechClient()


#     with open(stream_file, "rb") as audio_file:
#         content = audio_file.read()

#     # In practice, stream should be a generator yielding chunks of audio data.
#     stream = [content]

#     requests = (
#         speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
#     )

#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         sample_rate_hertz=16000,
#         language_code="fr-FR",
#     )

#     streaming_config = speech.StreamingRecognitionConfig(config=config)

#     # streaming_recognize returns a generator.
#     responses = client.streaming_recognize(
#         config=streaming_config,
#         requests=requests,
#     )

#     for response in responses:
#         # Once the transcription has settled, the first result will contain the
#         # is_final result. The other results will be for subsequent portions of
#         # the audio.
#         for result in response.results:
#             print(f"Finished: {result.is_final}")
#             print(f"Stability: {result.stability}")
#             alternatives = result.alternatives
#             # The alternatives are ordered from most likely to least.
#             for alternative in alternatives:
#                 st.write(f"Transcript: {alternative.transcript}")
#                 print(f"Confidence: {alternative.confidence}")
#                 print(f"Transcript: {alternative.transcript}")



# from pydub import AudioSegment
# from datetime import datetime
# import numpy as np
# import sounddevice as sd

# def listen(self, duration_seconds: float = np.inf) -> AudioSegment:
#     """Record audio from the microphone until user stops."""
#     # Adapted from
#     # <https://python-sounddevice.readthedocs.io/en/0.4.6/examples.html#
#     #  recording-with-arbitrary-duration>
#     debug_msg = "The assistant is listening"
#     if duration_seconds < np.inf:
#         debug_msg += f" for {duration_seconds} s"
#     debug_msg += "..."

#     inactivity_timeout_seconds = self.inactivity_timeout_seconds
#     if duration_seconds < np.inf:
#         inactivity_timeout_seconds = duration_seconds

#     q = queue.Queue()

#     def callback(indata, frames, time, status):  # noqa: ARG001
#         """This is called (from a separate thread) for each audio block."""
#         q.put(indata.copy())

#     raw_buffer = io.BytesIO()
#     start_time = datetime.now()
#     with self.get_sound_file(raw_buffer, mode="x") as sound_file, sd.InputStream(
#         samplerate=self.sample_rate,
#         blocksize=self.block_size,
#         channels=1,
#         callback=callback,
#         dtype="int16",  # int16, i.e., 2 bytes per sample
#     ):
#         logger.debug("{}", debug_msg)
#         # Recording will stop after inactivity_timeout_seconds of silence
#         voice_activity_detected = deque(
#             maxlen=int((1000.0 * inactivity_timeout_seconds) / self.frame_duration)
#         )
#         last_inactivity_checked = datetime.now()
#         continue_recording = True
#         speech_detected = False
#         elapsed_time = 0.0
#         with contextlib.suppress(KeyboardInterrupt):
#             while continue_recording and elapsed_time < duration_seconds:
#                 new_data = q.get()
#                 sound_file.write(new_data)

#                 # Gather voice activity samples for the inactivity check
#                 wav_buffer = _np_array_to_wav_in_memory(
#                     sound_data=new_data,
#                     sample_rate=self.sample_rate,
#                     subtype="PCM_16",
#                 )

#                 vad_thinks_this_chunk_is_speech = self.vad.is_speech(
#                     wav_buffer, self.sample_rate
#                 )
#                 voice_activity_detected.append(vad_thinks_this_chunk_is_speech)

#                 # Decide if user has been inactive for too long
#                 now = datetime.now()
#                 if duration_seconds < np.inf:
#                     continue_recording = True
#                 elif (
#                     now - last_inactivity_checked
#                 ).seconds >= inactivity_timeout_seconds:
#                     speech_likelihood = 0.0
#                     if len(voice_activity_detected) > 0:
#                         speech_likelihood = sum(voice_activity_detected) / len(
#                             voice_activity_detected
#                         )
#                     continue_recording = (
#                         speech_likelihood >= self.speech_likelihood_threshold
#                     )
#                     if continue_recording:
#                         speech_detected = True
#                     last_inactivity_checked = now

#                 elapsed_time = (now - start_time).seconds

#     if speech_detected or duration_seconds < np.inf:
#         return AudioSegment.from_wav(raw_buffer)
#     return AudioSegment.empty()



# ###################
