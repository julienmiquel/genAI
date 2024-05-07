import io
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

st.set_page_config(layout="wide")

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

st.header("Vertex AI Demo", divider="rainbow",)
text_model_pro, multimodal_model_pro, image_model, image2text_model = load_models()

story_data = cache_data()

tab3, tab6, tab5, tab1, tab2,  tab4,  = st.tabs(
    ["Image Playground","Audio & video", "Real-estate", "Generate story", "Marketing campaign",  "Video Playground", ]
)


@st.cache_data(persist=True)
def loadData():
    character_name_value = st.session_state.get("character_name", "Mittens")
    # character_type_value = st.session_state.get("character_type", "Cat")
    # character_persona_value = st.session_state.get("character_persona", "Mitten is a very friendly cat.")
    # character_location_value = st.session_state.get("character_location", "Andromeda Galaxy")
    # story_premise_value = st.session_state.get("story_premise", ["Love", "Adventure"])
    return character_name_value #, character_type_value, character_persona_value, character_location_value, story_premise_value

def saveData(character_name_value#, character_type_value,character_persona_value,character_location_value,story_premise_value,story_premise_value
             ):
        st.session_state["character_name_value"] = character_name_value
        print("SaveData : "+character_name_value)

def submit():
    st.session_state["character_name"] = character_name
    print("Save : "+st.session_state["character_name"])

with tab1:
    st.write("Using Gemini Pro - Text only model")
    st.subheader("Generate a story")

    character_name_value = loadData()#, character_type_value, character_persona_value, character_location_value, story_premise_value 
    
    
    # Story premise
    character_name = st.text_input(
        "Enter character name: \n\n", key="character_name", value=character_name_value#, on_change=submit
    )
    saveData(character_name_value)
    character_type = st.text_input(
        "What type of character is it? \n\n", key="character_type", value="Cat"
    )
    character_persona = st.text_input(
        "What personality does the character have? \n\n",
        key="character_persona",
        value="Mitten is a very friendly cat.",
    )
    character_location = st.text_input(
        "Where does the character live? \n\n",
        key="character_location",
        value="Andromeda Galaxy",
    )
    story_premise = st.multiselect(
        "What is the story premise? (can select multiple) \n\n",
        [
            "Love",
            "Adventure",
            "Mystery",
            "Horror",
            "Comedy",
            "Sci-Fi",
            "Fantasy",
            "Thriller",
        ],
        key="story_premise",
        default=["Love", "Adventure"],
    )
    creative_control = st.radio(
        "Select the creativity level: \n\n",
        ["Low", "High"],
        key="creative_control",
        horizontal=True,
    )
    length_of_story = st.radio(
        "Select the length of the story: \n\n",
        ["Short", "Long"],
        key="length_of_story",
        horizontal=True,
    )

    if creative_control == "Low":
        temperature = 0.30
    else:
        temperature = 0.95

    max_output_tokens = 2048

    prompt = f"""Write a {length_of_story} story based on the following premise: \n
    character_name: {character_name} \n
    character_type: {character_type} \n
    character_persona: {character_persona} \n
    character_location: {character_location} \n
    story_premise: {",".join(story_premise)} \n
    If the story is "short", then make sure to have 5 chapters or else if it is "long" then 10 chapters.
    Important point is that each chapters should be generated based on the premise given above.
    First start by giving the book introduction, chapter introductions and then each chapter. It should also have a proper ending.
    The book should have prologue and epilogue.
    """
    # config = GenerationConfig(
    #     temperature=temperature,
    #     candidate_count=1,
    #     max_output_tokens=max_output_tokens,
    # )

    config_llm = {
        "temperature": 0.8,
        "max_output_tokens": 2048,
    }

    image_prompt = f"""Generate a character based on following parameters: character_name: {character_name} \n
        character_type: {character_type} \n
        character_persona: {character_persona} \n
        character_location: {character_location} \n
        story_premise: {",".join(story_premise)} \n"""


    generate_t2t = st.button("Generate my story", key="generate_t2t")
    if generate_t2t and prompt:
        # st.write(prompt)
        with st.spinner("Generating your story using Gemini..."):
            first_tab1, first_tab2 = st.tabs(["Story", "Prompt" ])
            with first_tab1:
                
                response = get_gemini_pro_text_response(
                    text_model_pro,
                    prompt,
                    generation_config=config_llm,
                )
                if response:
                    st.write("Your story:")
                    st.write(response)
                    story_data.story = response

            with first_tab2:
                st.text(prompt)
         

    generate_t2i = st.button("Generate an illustrative image of the main character", key="generate_t2ti")
    if generate_t2i and image_prompt and story_data.story:
        
        with st.spinner("Generating your storyboard using imagen..."):
            st.write("Your story:")
            st.write(story_data.story)

            first_img_tab1, first_img_tab2 = st.tabs(["Image", "Prompt"])
            with first_img_tab1:
                import text2img as text2img
                images, generate_response = text2img.imagen_generate(image_prompt, image_model )
                
                if images:
                    st.write("Your storyboard:")
                    for image in images:
                        from PIL import Image as PIL_image

                        st.image(image, width=350, caption=f"Your generated character named {character_name}")
                        story_data.image_character = image
                        st.write(image)
            with first_img_tab2:
                st.text(image_prompt)

    generate_t3i = st.button("Generate my storyboard based on character and story", key="generate_t3i")
    if generate_t3i and story_data.story:

        story_parts = story_data.story.split("**")                
        with st.spinner("Generating your storyboard using imagen..."):
            st.write("Your story:")
            for story_part in story_parts:
                st.write(story_part)

                par_image_prompt = f"""Generate an ilustrative scene based on the context below of the character based on following parameters: 
                character_name: {character_name} \n
    character_type: {character_type} \n
    character_persona: {character_persona} \n
    character_location: {character_location} \n
    story_premise: {",".join(story_premise)} \n
    story_scene: {",".join(story_part)} \n
    """

                first_img_tab1, first_img_tab2 = st.tabs(["Image", "Prompt"])
                with first_img_tab1:
                    import text2img as text2img
                    images, generate_response = text2img.imagen_generate(image_prompt, image_model )
                    
                    if images:
                        #st.write("Your storyboard:")
                        for image in images:
                            from PIL import Image as PIL_image

                            st.image(image, width=350, caption=f"Your generated character named {character_name}")
                            story_data.image_character = image
                            st.write(image)


                
with tab2:
    st.write("Using Gemini Pro - Text only model")
    st.subheader("Generate your marketing campaign")

    product_name = st.text_input(
        "What is the name of the product? \n\n", key="product_name", value="ZomZoo"
    )
    product_category = st.radio(
        "Select your product category: \n\n",
        ["Clothing", "Electronics", "Food", "Health & Beauty", "Home & Garden"],
        key="product_category",
        horizontal=True,
    )
    st.write("Select your target audience: ")
    target_audience_age = st.radio(
        "Target age: \n\n",
        ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        key="target_audience_age",
        horizontal=True,
    )
    # target_audience_gender = st.radio("Target gender: \n\n",["male","female","trans","non-binary","others"],key="target_audience_gender",horizontal=True)
    target_audience_location = st.radio(
        "Target location: \n\n",
        ["Urban", "Suburban", "Rural"],
        key="target_audience_location",
        horizontal=True,
    )
    st.write("Select your marketing campaign goal: ")
    campaign_goal = st.multiselect(
        "Select your marketing campaign goal: \n\n",
        [
            "Increase brand awareness",
            "Generate leads",
            "Drive sales",
            "Improve brand sentiment",
        ],
        key="campaign_goal",
        default=["Increase brand awareness", "Generate leads"],
    )
    if campaign_goal is None:
        campaign_goal = ["Increase brand awareness", "Generate leads"]
    brand_voice = st.radio(
        "Select your brand voice: \n\n",
        ["Formal", "Informal", "Serious", "Humorous"],
        key="brand_voice",
        horizontal=True,
    )
    estimated_budget = st.radio(
        "Select your estimated budget ($): \n\n",
        ["1,000-5,000", "5,000-10,000", "10,000-20,000", "20,000+"],
        key="estimated_budget",
        horizontal=True,
    )

    prompt = f"""Generate a marketing campaign for {product_name}, a {product_category} designed for the age group: {target_audience_age}.
    The target location is this: {target_audience_location}.
    Aim to primarily achieve {campaign_goal}.
    Emphasize the product's unique selling proposition while using a {brand_voice} tone of voice.
    Allocate the total budget of {estimated_budget}.
    With these inputs, make sure to follow following guidelines and generate the marketing campaign with proper headlines: \n
    - Briefly describe company, its values, mission, and target audience.
    - Highlight any relevant brand guidelines or messaging frameworks.
    - Provide a concise overview of the campaign's objectives and goals.
    - Briefly explain the product or service being promoted.
    - Define your ideal customer with clear demographics, psychographics, and behavioral insights.
    - Understand their needs, wants, motivations, and pain points.
    - Clearly articulate the desired outcomes for the campaign.
    - Use SMART goals (Specific, Measurable, Achievable, Relevant, and Time-bound) for clarity.
    - Define key performance indicators (KPIs) to track progress and success.
    - Specify the primary and secondary goals of the campaign.
    - Examples include brand awareness, lead generation, sales growth, or website traffic.
    - Clearly define what differentiates your product or service from competitors.
    - Emphasize the value proposition and unique benefits offered to the target audience.
    - Define the desired tone and personality of the campaign messaging.
    - Identify the specific channels you will use to reach your target audience.
    - Clearly state the desired action you want the audience to take.
    - Make it specific, compelling, and easy to understand.
    - Identify and analyze your key competitors in the market.
    - Understand their strengths and weaknesses, target audience, and marketing strategies.
    - Develop a differentiation strategy to stand out from the competition.
    - Define how you will track the success of the campaign.
   -  Utilize relevant KPIs to measure performance and return on investment (ROI).
   Give proper bullet points and headlines for the marketing campaign. Do not produce any empty lines.
   Be very succinct and to the point.
    """
    generation_config = {
        "temperature": 0.8,
        "max_output_tokens": 2048,
    }
    generate_t2t = st.button("Generate my campaign", key="generate_campaign")
    if generate_t2t and prompt:
        second_tab1, second_tab2 = st.tabs(["Campaign", "Prompt"])
        with st.spinner("Generating your marketing campaign using Gemini..."):
            with second_tab1:
                response = get_gemini_pro_text_response(
                    text_model_pro,
                    prompt,
                    generation_config=generation_config,
                )
                if response:
                    st.write("Your marketing campaign:")
                    st.write(response)
            with second_tab2:
                st.text(prompt)


    

with tab3:
    st.write("Using Gemini Pro Vision - Multimodal model")
    tab_image, tab_image_to_text, tab_image_to_text_to_image, image_undst, screens_undst, diagrams_undst, recommendations, sim_diff = st.tabs(
        [
            "Using Imagen - Text 2 image" , "Using Imagen - image 2 text", "Using Imagen - image 2 text 2 image :-)", 
            "Furniture recommendation",
            "Oven instructions",
            "ER diagrams",
            "Glasses recommendation",
            "Math reasoning",
            
        ]
    )

    with tab_image:
        st.write("Using Imagen - Text 2 image")
        st.subheader("Generate image")

        image_prompt = "A real-estate luxury living room"
        image_prompt = st.text_area('Enter your text here...', image_prompt, )

        generate_t2imagen = st.button("Generate an image", key="generate_t2imagen")
        if generate_t2imagen and image_prompt:
            
            with st.spinner("Generating an image using imagen..."):
                
                first_img_tab1, first_img_tab2 = st.tabs(["Image", "Prompt"])
                with first_img_tab1:
                    import text2img as text2img
                    images, generate_response = text2img.imagen_generate(image_prompt, image_model )
                    
                    if images:
                        for image in images:
                            st.image(image, width=350, caption=f"Your generated image")                       
                    else:
                        st.text("Error when generate image")
                        st.text(generate_response)    
                with first_img_tab2:
                    st.text(image_prompt)


    with tab_image_to_text:
        st.write("Using Imagen - image 2 text")
        st.subheader("image decription")

        image_2_describe_to_image = None
        uploaded_image2t2i_file = st.file_uploader("Choose an image file", type= ["jpg", "jpeg"])

        if uploaded_image2t2i_file is not None:
            # To read file as bytes:
            bytes_data = uploaded_image2t2i_file.getvalue()
            st.image(bytes_data, caption='Uploaded image')
            from PIL import Image as PIL_image
            #image_2_describe = PIL_image.Image.frombytes(bytes_data)
            #image_2_describe = Image.from_bytes(bytes_data)
            print("######################################")
            #print(image_2_describe) # = "image/jpeg"
            captions =  get_image_2_text_response(model=image2text_model, source_bytes=bytes_data)
            st.write("Caption from imagen:")
            st.write(captions)

            prompt = "Create a detailed prompt from the image"

            image_part = Part.from_data(bytes_data, mime_type="image/jpeg")
            response_gemini = get_gemini_pro_vision_response(
                model=multimodal_model_pro, prompt_list=[image_part, prompt]
            )
            st.write("Caption from gemini:")
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
    with tab_image_to_text_to_image:
        st.write("Using Imagen - image 2 text 2 image :-)")
        st.subheader("image description and generation")

        image_2_describe = None
        uploaded_image_to_text_to_image_file = st.file_uploader("Choose an image file", 
                                                                type= ["jpg", "jpeg"], 
                                                                key="uploaded_image_to_text_to_image_file")

        if uploaded_image_to_text_to_image_file is not None:
            # To read file as bytes:
            bytes_data = uploaded_image_to_text_to_image_file.getvalue()
            st.image(bytes_data, caption='Uploaded image')
            from PIL import Image as PIL_image
            #image_2_describe = PIL_image.Image.frombytes(bytes_data)
            #image_2_describe = Image.from_bytes(bytes_data)
            print("######################################")
            #print(image_2_describe) # = "image/jpeg"
            captions =  get_image_2_text_response(model=image2text_model, source_bytes=bytes_data)
            st.write("Caption from imagen:")            
            st.write(captions)

            image_part = Part.from_data(bytes_data, mime_type="image/jpeg")
            prompt = "Create a detailed prompt from the image"

            response_gemini = get_gemini_pro_vision_response(
                model=multimodal_model_pro, prompt_list=[image_part, prompt]
            )
            st.write("Caption from gemini:")
            st.markdown(response_gemini)

            image_prompt =  response_gemini + ", ".join(captions) 
            st.write(image_prompt)

            with st.spinner("Generating an image using imagen..."):
                
                first_img_tab1, first_img_tab2 = st.tabs(["Image", "Prompt"])
                with first_img_tab1:
                    import text2img as text2img
                    images, generate_response = text2img.imagen_generate(image_prompt, image_model )
                    
                    if images:
                        for image in images:
                            st.image(image, width=350, caption=f"Your generated image")                       
                    else:
                        st.text("Error when generate image")
                        st.text(generate_response)
                        
                with first_img_tab2:
                    st.text(image_prompt)


    with image_undst:
        st.markdown(
            """In this demo, you will be presented with a scene (e.g., a living room) and will use the Gemini model to perform visual understanding. You will see how Gemini can be used to recommend an item (e.g., a chair) from a list of furniture options as input. You can use Gemini to recommend a chair that would complement the given scene and will be provided with its rationale for such selections from the provided list.
                    """
        )

        room_image_uri = (
            "gs://github-repo/img/gemini/retail-recommendations/rooms/living_room.jpeg"
        )
        chair_1_image_uri = (
            "gs://github-repo/img/gemini/retail-recommendations/furnitures/chair1.jpeg"
        )
        chair_2_image_uri = (
            "gs://github-repo/img/gemini/retail-recommendations/furnitures/chair2.jpeg"
        )
        chair_3_image_uri = (
            "gs://github-repo/img/gemini/retail-recommendations/furnitures/chair3.jpeg"
        )
        chair_4_image_uri = (
            "gs://github-repo/img/gemini/retail-recommendations/furnitures/chair4.jpeg"
        )

        room_image_urls = (
            "https://storage.googleapis.com/" + room_image_uri.split("gs://")[1]
        )
        chair_1_image_urls = (
            "https://storage.googleapis.com/" + chair_1_image_uri.split("gs://")[1]
        )
        chair_2_image_urls = (
            "https://storage.googleapis.com/" + chair_2_image_uri.split("gs://")[1]
        )
        chair_3_image_urls = (
            "https://storage.googleapis.com/" + chair_3_image_uri.split("gs://")[1]
        )
        chair_4_image_urls = (
            "https://storage.googleapis.com/" + chair_4_image_uri.split("gs://")[1]
        )

        room_image = Part.from_uri(room_image_uri, mime_type="image/jpeg")
        chair_1_image = Part.from_uri(chair_1_image_uri, mime_type="image/jpeg")
        chair_2_image = Part.from_uri(chair_2_image_uri, mime_type="image/jpeg")
        chair_3_image = Part.from_uri(chair_3_image_uri, mime_type="image/jpeg")
        chair_4_image = Part.from_uri(chair_4_image_uri, mime_type="image/jpeg")

        st.image(room_image_urls, width=350, caption="Image of a living room")
        st.image(
            [
                chair_1_image_urls,
                chair_2_image_urls,
                chair_3_image_urls,
                chair_4_image_urls,
            ],
            width=200,
            caption=["Chair 1", "Chair 2", "Chair 3", "Chair 4"],
        )

        st.write(
            "Our expectation: Recommend a chair that would complement the given image of a living room."
        )
        content = [
            "Consider the following chairs:",
            "chair 1:",
            chair_1_image,
            "chair 2:",
            chair_2_image,
            "chair 3:",
            chair_3_image,
            "and",
            "chair 4:",
            chair_4_image,
            "\n"
            "For each chair, explain why it would be suitable or not suitable for the following room:",
            room_image,
            "Only recommend for the room provided and not other rooms. Provide your recommendation in a table format with chair name and reason as columns.",
        ]

        tab1, tab2 = st.tabs(["Response", "Prompt"])
        generate_image_description = st.button(
            "Generate recommendation....", key="generate_image_description"
        )
        with tab1:
            if generate_image_description and content:
                with st.spinner("Generating recommendation using Gemini..."):
                    response = get_gemini_pro_vision_response(
                        multimodal_model_pro, content
                    )
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.text(content)

    with screens_undst:
        stove_screen_uri = (
            "gs://github-repo/img/gemini/multimodality_usecases_overview/stove.jpg"
        )
        stove_screen_url = (
            "https://storage.googleapis.com/" + stove_screen_uri.split("gs://")[1]
        )

        st.write(
            "Equipped with the ability to extract information from visual elements on screens, Gemini can analyze screenshots, icons, and layouts to provide a holistic understanding of the depicted scene."
        )
        # cooking_what = st.radio("What are you cooking?",["Turkey","Pizza","Cake","Bread"],key="cooking_what",horizontal=True)
        stove_screen_img = Part.from_uri(stove_screen_uri, mime_type="image/jpeg")
        st.image(stove_screen_url, width=350, caption="Image of a oven")
        st.write(
            "Our expectation: Provide instructions for resetting the clock on this appliance in English"
        )
        prompt = """How can I reset the clock on this appliance? Provide the instructions in English.
If instructions include buttons, also explain where those buttons are physically located.
"""
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        generate_instructions_description = st.button(
            "Generate instructions", key="generate_instructions_description"
        )
        with tab1:
            if generate_instructions_description and prompt:
                with st.spinner("Generating instructions using Gemini..."):
                    response = get_gemini_pro_vision_response(
                        multimodal_model_pro, [stove_screen_img, prompt]
                    )
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.text(prompt + "\n" + "input_image")

    with diagrams_undst:
        er_diag_uri = (
            "gs://github-repo/img/gemini/multimodality_usecases_overview/er.png"
        )
        er_diag_url = "https://storage.googleapis.com/" + er_diag_uri.split("gs://")[1]

        st.write(
            "Gemini's multimodal capabilities empower it to comprehend diagrams and take actionable steps, such as optimization or code generation. The following example demonstrates how Gemini can decipher an Entity Relationship (ER) diagram."
        )
        er_diag_img = Part.from_uri(er_diag_uri, mime_type="image/jpeg")
        st.image(er_diag_url, width=350, caption="Image of a ER diagram")
        st.write(
            "Our expectation: Document the entities and relationships in this ER diagram."
        )
        prompt = """Document the entities and relationships in this ER diagram.
                """
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        er_diag_img_description = st.button("Generate!", key="er_diag_img_description")
        with tab1:
            if er_diag_img_description and prompt:
                with st.spinner("Generating..."):
                    response = get_gemini_pro_vision_response(
                        multimodal_model_pro, [er_diag_img, prompt]
                    )
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.text(prompt + "\n" + "input_image")

    with recommendations:
        compare_img_1_uri = (
            "gs://github-repo/img/gemini/multimodality_usecases_overview/glasses1.jpg"
        )
        compare_img_2_uri = (
            "gs://github-repo/img/gemini/multimodality_usecases_overview/glasses2.jpg"
        )

        compare_img_1_url = (
            "https://storage.googleapis.com/" + compare_img_1_uri.split("gs://")[1]
        )
        compare_img_2_url = (
            "https://storage.googleapis.com/" + compare_img_2_uri.split("gs://")[1]
        )

        st.write(
            """Gemini is capable of image comparison and providing recommendations. This may be useful in industries like e-commerce and retail.
                    Below is an example of choosing which pair of glasses would be better suited to various face types:"""
        )
        compare_img_1_img = Part.from_uri(compare_img_1_uri, mime_type="image/jpeg")
        compare_img_2_img = Part.from_uri(compare_img_2_uri, mime_type="image/jpeg")
        face_type = st.radio(
            "What is your face shape?",
            ["Oval", "Round", "Square", "Heart", "Diamond"],
            key="face_type",
            horizontal=True,
        )
        output_type = st.radio(
            "Select the output type",
            ["text", "table", "json"],
            key="output_type",
            horizontal=True,
        )
        st.image(
            [compare_img_1_url, compare_img_2_url],
            width=350,
            caption=["Glasses type 1", "Glasses type 2"],
        )
        st.write(
            f"Our expectation: Suggest which glasses type is better for the {face_type} face shape"
        )
        content = [
            f"""Which of these glasses you recommend for me based on the shape of my face:{face_type}?
           I have an {face_type} shape face.
           Glasses 1: """,
            compare_img_1_img,
            """
           Glasses 2: """,
            compare_img_2_img,
            f"""
           Explain how you reach out to this decision.
           Provide your recommendation based on my face shape, and reasoning for each in {output_type} format.
           """,
        ]
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        compare_img_description = st.button(
            "Generate recommendation!", key="compare_img_description"
        )
        with tab1:
            if compare_img_description and content:
                with st.spinner("Generating recommendations using Gemini..."):
                    response = get_gemini_pro_vision_response(
                        multimodal_model_pro, content
                    )
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.text(content)

    with sim_diff:
        math_image_uri = "gs://github-repo/img/gemini/multimodality_usecases_overview/math_beauty.jpg"
        math_image_url = (
            "https://storage.googleapis.com/" + math_image_uri.split("gs://")[1]
        )
        st.write(
            "Gemini can also recognize math formulas and equations and extract specific information from them. This capability is particularly useful for generating explanations for math problems, as shown below."
        )
        math_image_img = Part.from_uri(math_image_uri, mime_type="image/jpeg")
        st.image(math_image_url, width=350, caption="Image of a math equation")
        st.markdown(
            """
                Our expectation: Ask questions about the math equation as follows:
                - Extract the formula.
                - What is the symbol right before Pi? What does it mean?
                - Is this a famous formula? Does it have a name?
                    """
        )
        prompt = """
Follow the instructions.
Surround math expressions with $.
Use a table with a row for each instruction and its result.

INSTRUCTIONS:
- Extract the formula.
- What is the symbol right before Pi? What does it mean?
- Is this a famous formula? Does it have a name?
"""
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        math_image_description = st.button(
            "Generate answers!", key="math_image_description"
        )
        with tab1:
            if math_image_description and prompt:
                with st.spinner("Generating answers for formula using Gemini..."):
                    response = get_gemini_pro_vision_response(
                        multimodal_model_pro, [math_image_img, prompt]
                    )
                    st.markdown(response)
                    st.markdown("\n\n\n")
        with tab2:
            st.write("Prompt used:")
            st.text(prompt)

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


with tab5:
    st.write("Using Gemini Pro Vision - Real-Estate")


    re_windows, re_chatbot  = st.tabs(
        ["Real-Estate Windows identification" , "Chat bot"]
    )

    with re_chatbot:
        st.markdown(
            """Votre assistant de l'immobilier"""
        )
        chatbot = True
        web_input = st.text_input("URL", key="web_input", value="https://www.orpi.com/annonce-vente-appartement-t3-capbreton-40130-711-044059-848/?agency=monemartinaudcapbreton"
    )

    with re_windows:
        st.markdown(
            """Gemini can also provide usefull information to identify the real-estate windows:"""
        )

        image_uri = "https://soglass.fr/1424-large_default/double-vitrage-sur-mesure.jpg"

        # room_image_uri = (
        #     "gs://github-repo/img/gemini/retail-recommendations/rooms/living_room.jpeg"
        # )
        st.image(image_uri, width=350, caption="Fenetre à double vitrage")


        from vertexai.preview.generative_models import (
            GenerationConfig,
            GenerativeModel,
            Image,
            Part,
        )

        image = Part.from_uri(room_image_uri, mime_type="image/jpeg")

        uploaded_file = st.file_uploader("Choose a file", key="uploaded_file")
        if uploaded_file is not None:
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
#            st.write(bytes_data)
            st.image(bytes_data, caption='Uploaded image')
            from PIL import Image as PIL_image

            image = Image.from_bytes(bytes_data)
            print("######################################")
            print(image._pil_image) # = "image/jpeg"

 
        st.write(
            "Our expectation: Classify type of windows"
        )

        instructions = "Instructions: Consider the following image that contains windows:"
        instructions= st.text_input("Instructions", value=instructions, )

        prompt = """Windows thermal classification based on image provided.
Answer in JSON format with keys  type, thermal isolation reason, confidence, level of thermal isolation.
Classify the windows based on his type (simple, double, triple).
Explain the reason of the classification.
Explain the reason of the type of material.
Provide confidence level.

JSON:"""
        prompt = st.text_area('Enter your text here...', prompt, )

 
        tab1, tab2 = st.tabs( ["Response", "Prompt"])
        generate_re_image_description = st.button(
            "Generate recommendation....", key="generate_re_image_description"
        )
        contents = []
        with tab1:

            if generate_re_image_description and image:
                contents = [
                        instructions,
                        image,
                        prompt,
                    ]
                with st.spinner("Generating recommendation using Gemini..."):

#                    responses = multimodal_model_pro.generate_content(contents, stream=True)

                    # answer  = "Answer is: "
                    # for response in responses:
                    #     print(response.text, end="")
                    #     answer += response.text
                    
                    # st.text(answer)
                    contents = [
                            instructions,
                            image,
                            prompt,
                        ]

                    response = get_gemini_pro_vision_response(
                        multimodal_model_pro, contents
                    )
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.text(
                "\n".join(
                    [
                            instructions,                            
                            prompt,
                        ]))


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

with tab6:
    st.write("Audio & video - STT Chirp")


    podcast_all, gemini_stt, stt, video  = st.tabs(
        ["Podcast every-things", "Gemini as STT", "STT Chirp" , "video - youtube"]
    )

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

        # 2) Generate script
        if generate_podcast and text_to_generate_podcast and len(text_to_generate_podcast) > 0:

                with st.spinner("Generating summary using Gemini..."):
                    podcast_summary_prompt, text_summary_to_generate_podcast = stt_generate_summary(text_to_generate_podcast, prompt_content_balise_start, prompt_content_balise_stop)
                    with st.expander("Summary", expanded=True):    
                        st.markdown(text_summary_to_generate_podcast)

                # with st.spinner("Generating podcast title using Gemini..."):                    
                #     podcast_title = stt_generate_title( prompt_content_balise_start, prompt_content_balise_stop, text_summary_to_generate_podcast)
                #     podcast_title = podcast_title.replace("#","").replace("*","")
                #     st.markdown(f"# TITLE : {podcast_title}")
                #     print(podcast_title)
                podcast_title = ""

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
                        podcast_chunck_file = f"{podcast_title}  {utils.create_timestamped_name('podcast')}"
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
                        else:
                            st.markdown("# No audio generated")


    with gemini_stt:
        st.markdown(
            """Gemini as STT"""
        )
        language_code_gemini =  st.text_input("language_code_gemini", value="fr-FR", )


        uploaded_sound_to_bucket = st.file_uploader("Choose a audio file", type=None)
        if uploaded_sound_to_bucket is not None:
            # To read file as bytes:
            media_data = uploaded_sound_to_bucket.getvalue()
            #st.write(media_data)
            print(f"BUCKET_NAME: {config.BUCKET}")
            gcs_uri_input = gcs.write_bytes_to_gcs(config.BUCKET, "datasets/input/" + uploaded_sound_to_bucket.name,  media_data, "binary/octet-stream")
            print(f"gcs_uri_input: {gcs_uri_input}")
            gcs_uri_output = f"gs://{config.BUCKET}/datasets/transcript/{uploaded_sound_to_bucket.name}/"
            print(f"gcs_uri_output: {gcs_uri_output}")

        bt_run_stt_gemini =st.button(
            "Run STT", key="bt_run_stt_gemini"
        )
        if bt_run_stt_gemini and language_code_gemini  and gcs_uri_input and gcs_uri_output:
            from gemini import       generate_transcript_from_audio
            
            final_res= ""
            with st.spinner("Generating STT using Gemini..."):
                audio = Part.from_uri(gcs_uri_input, mime_type="audio/x-m4a") 

                results = generate_transcript_from_audio(audio, language=language_code_gemini)
                for result in results:
                    if result[0] is not None:
                        st.markdown(result[0])                    

                    if result[1] is not None:
                        final_res = result[1]
                    
                
                import gcs as gcs

                                
                gcs.write_string_to_bucket(config.BUCKET, f"/datasets/transcript/{uploaded_sound_to_bucket.name}/",final_res)
            
            st.markdown(f"Final result also available here: {gcs_uri_output}")
            st.markdown(final_res)
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
