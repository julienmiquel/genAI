import datetime
import io
import os
import random
import time
import streamlit as st
import videoedit as videoedit

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

st.set_page_config(page_title="Google Cloud AI Demos (Gemini) - SEO optimizations for news", layout="wide")

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

story_data = cache_data()
list_of_tabs_name = ["Image"  "video", ]
tab3,   tab4,  = st.tabs(
    ["Image Playground",  "Video Playground", ],    
    #["Image","audio", "Real-estate", "story", "Marketing",  "video", ],    
)
list_of_tabs = [tab3, tab4]



# try:    
#     # Handling query parameters
#     query = st.query_params

#     ## Look-up the tab from the query
#     index_tab = list_of_tabs_name.index(query["tab"][0])
#     # with list_of_tabs[index_tab]:
#     #     st.write(query["tab"])

#     my_js = """
#     alert("Hola mundo");
#     """
#     my_html = f"<script>{my_js}</script>"

#     st.components.v1.html(my_html)
#     st.markdown(my_html,unsafe_allow_html=True)

# except ValueError:
#     ## Do nothing if the query parameter does not correspond to any of the tabs
#     pass




with tab3:
    st.write("Using Gemini Pro Vision - Multimodal model")
    # tab_image_to_text    = st.tabs(
    #     [
    #         "SEO optimization images "            
    #     ]
    # )


    # with tab_image_to_text:
    st.write("Using Imagen - image 2 text")
    st.subheader("image decription", anchor="imagedesc")

    image_2_describe_to_image = None
    text_body = st.text_area(label="Image context", value="")
    uploaded_image2t2i_file = st.file_uploader("Choose an image file", type= ["jpg", "jpeg", "png"])
    bt_run = st.button("run")
    if uploaded_image2t2i_file is not None and bt_run:
        # To read file as bytes:
        bytes_data = uploaded_image2t2i_file.getvalue()
        st.image(bytes_data, caption='Uploaded image')
        from PIL import Image as PIL_image
        #image_2_describe = PIL_image.Image.frombytes(bytes_data)
        #image_2_describe = Image.from_bytes(bytes_data)
        print("######################################")
        #print(image_2_describe) # = "image/jpeg"
        if False:
            captions =  get_image_2_text_response(model=image2text_model, source_bytes=bytes_data)
            st.write("Caption from imagen:")
            st.write(captions)

        image_part = Part.from_data(bytes_data, mime_type="image/jpeg")

        prompt = "Create a detailed image description from the image in French"
        response_gemini = get_gemini_pro_vision_response(
            model=multimodal_model_pro, prompt_list=[image_part, prompt]
        )
        st.markdown("## Caption from gemini: ")
        st.markdown(response_gemini)


        prompt = "Create an image description to optimize SEO from the image"

        response_gemini = get_gemini_pro_vision_response(
            model=multimodal_model_pro, prompt_list=[image_part, prompt]
        )
        st.markdown("## SEO description optimized from gemini:")
        st.markdown(response_gemini)

        prompt = f"Create an image description to optimize SEO from the image and the context: <context> {text_body}</context>"

        response_gemini = get_gemini_pro_vision_response(
            model=multimodal_model_pro, prompt_list=[image_part, prompt]
        )
        st.markdown("## SEO description optimized from gemini enriched with news context:")
        st.markdown(response_gemini)

        prompt = f"generate 10 best SEO hashtags from image and context <context> {text_body}</context>"

        response_gemini = get_gemini_pro_vision_response(
            model=multimodal_model_pro, prompt_list=[image_part, prompt]
        )
        st.markdown("## 10 best SEO hashtags optimized from gemini enriched with news context:")
        st.markdown(response_gemini)

        prompt = f"generate 10 best SEO hashtags optimized for French market from image and context <context> {text_body}</context>"

        response_gemini = get_gemini_pro_vision_response(
            model=multimodal_model_pro, prompt_list=[image_part, prompt]
        )
        st.markdown("## 10 best SEO hashtags optimized for France enriched with news context:")
        st.markdown(response_gemini)
        # describe_i2timagen = st.button("Describe an image", key="describe_i2timagen")
        # if describe_i2timagen and image_2_describe: # and image_prompt:
            
        #     with st.spinner("Generating a description of an image using imagen..."):
                
        #         first_img_tab1, first_img_tab2 = st.tabs(["Image", "Prompt"])
        #         with first_img_tab1:
        #             import text2img as text2img
        #             images, generate_response = text2img.imagen_generate(image_prompt, image_model )
                    
        #             if images:
        #                 for image in images:
        #                     st.image(image, width=350, caption=f"Your generated image")                       
        #             else:
        #                 st.text("Error when generate image")
        #                 st.text(generate_response)    
        #         with first_img_tab2:
        #             st.text(image_prompt)

with tab4:
    st.write("Using Gemini Pro Vision - Multimodal model")

    vide_desc, video_tags, video_highlights, video_geoloaction = st.tabs(
        ["Video description", "Video tags", "Video highlights", "Video geolocation"]
    )

    with vide_desc:
        st.markdown(
            """Gemini can also provide the description of what is going on in the video:"""
        )
        vide_desc_uri = "gs://github-repo/img/gemini/multimodality_usecases_overview/mediterraneansea.mp4"
        video_desc_url = (
            "https://storage.googleapis.com/" + vide_desc_uri.split("gs://")[1]
        )
        if vide_desc_uri:
            vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")
            st.video(video_desc_url)
            st.write("Our expectation: Generate the description of the video")
            prompt = """Describe what is happening in the video and answer the following questions: \n
            - What am I looking at? \n
            - Where should I go to see it? \n
            - What are other top 5 places in the world that look like this?
            """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            vide_desc_description = st.button(
                "Generate video description", key="vide_desc_description"
            )
            with tab1:
                if vide_desc_description and prompt:
                    with st.spinner("Generating video description using Gemini..."):
                        response = get_gemini_pro_vision_response(
                            multimodal_model_pro, [prompt, vide_desc_img]
                        )
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.write(prompt, "\n", "{video_data}")

    with video_tags:
        st.markdown(
            """Gemini can also extract tags throughout a video, as shown below:."""
        )
        video_tags_uri = "gs://github-repo/img/gemini/multimodality_usecases_overview/photography.mp4"
        video_tags_url = (
            "https://storage.googleapis.com/" + video_tags_uri.split("gs://")[1]
        )
        if video_tags_url:
            video_tags_img = Part.from_uri(video_tags_uri, mime_type="video/mp4")
            st.video(video_tags_url)
            st.write("Our expectation: Generate the tags for the video")
            prompt = """Answer the following questions using the video only:
                        1. What is in the video?
                        2. What objects are in the video?
                        3. What is the action in the video?
                        4. Provide 5 best tags for this video?
                        Give the answer in the table format with question and answer as columns.
            """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            video_tags_description = st.button(
                "Generate video tags", key="video_tags_description"
            )
            with tab1:
                if video_tags_description and prompt:
                    with st.spinner("Generating video description using Gemini..."):
                        response = get_gemini_pro_vision_response(
                            multimodal_model_pro, [prompt, video_tags_img]
                        )
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.write(prompt, "\n", "{video_data}")
    with video_highlights:
        st.markdown(
            """Below is another example of using Gemini to ask questions about objects, people or the context, as shown in the video about Pixel 8 below:"""
        )
        video_highlights_uri = (
            "gs://github-repo/img/gemini/multimodality_usecases_overview/pixel8.mp4"
        )
        video_highlights_url = (
            "https://storage.googleapis.com/" + video_highlights_uri.split("gs://")[1]
        )
        if video_highlights_url:
            video_highlights_img = Part.from_uri(
                video_highlights_uri, mime_type="video/mp4"
            )
            st.video(video_highlights_url)
            st.write("Our expectation: Generate the highlights for the video")
            prompt = """Answer the following questions using the video only:
What is the profession of the girl in this video?
Which all features of the phone are highlighted here?
Summarize the video in one paragraph.
Provide the answer in table format.
            """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            video_highlights_description = st.button(
                "Generate video highlights", key="video_highlights_description"
            )
            with tab1:
                if video_highlights_description and prompt:
                    with st.spinner("Generating video highlights using Gemini..."):
                        response = get_gemini_pro_vision_response(
                            multimodal_model_pro, [prompt, video_highlights_img]
                        )
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.write(prompt, "\n", "{video_data}")

    with video_geoloaction:
        st.markdown(
            """Even in short, detail-packed videos, Gemini can identify the locations."""
        )
        video_geoloaction_uri = (
            "gs://github-repo/img/gemini/multimodality_usecases_overview/bus.mp4"
        )
        video_geoloaction_url = (
            "https://storage.googleapis.com/" + video_geoloaction_uri.split("gs://")[1]
        )
        if video_geoloaction_url:
            video_geoloaction_img = Part.from_uri(
                video_geoloaction_uri, mime_type="video/mp4"
            )
            st.video(video_geoloaction_url)
            st.markdown(
                """Our expectation: \n
            Answer the following questions from the video:
                - What is this video about?
                - How do you know which city it is?
                - What street is this?
                - What is the nearest intersection?
            """
            )
            prompt = """Answer the following questions using the video only:
            What is this video about?
            How do you know which city it is?
            What street is this?
            What is the nearest intersection?
            Answer the following questions in a table format with question and answer as columns.
            """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            video_geoloaction_description = st.button(
                "Generate", key="video_geoloaction_description"
            )
            with tab1:
                if video_geoloaction_description and prompt:
                    with st.spinner("Generating location tags using Gemini..."):
                        response = get_gemini_pro_vision_response(
                            multimodal_model_pro, [prompt, video_geoloaction_img]
                        )
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.write(prompt, "\n", "{video_data}")



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


from app_footer import footer
footer(st)


