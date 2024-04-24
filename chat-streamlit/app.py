import streamlit as st
from PIL import Image
from src.utils import *
from src.vertex import *

# Utils
import time
from typing import List

# Langchain
import langchain
from pydantic import BaseModel

print(f"LangChain version: {langchain.__version__}")

# Vertex AI
from google.cloud import aiplatform
from langchain.chat_models import ChatVertexAI
from langchain.embeddings import VertexAIEmbeddings
from langchain.llms import VertexAI
from langchain.schema import HumanMessage, SystemMessage

print(f"Vertex AI SDK version: {aiplatform.__version__}")

# Utility functions for Embeddings API with rate limiting
def rate_limit(max_per_minute):
    period = 60 / max_per_minute
    print("Waiting")
    while True:
        before = time.time()
        yield
        after = time.time()
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
            print(".", end="")
            time.sleep(sleep_time)


class CustomVertexAIEmbeddings(VertexAIEmbeddings, BaseModel):
    requests_per_minute: int
    num_instances_per_batch: int

    # Overriding embed_documents method
    def embed_documents(self, texts: List[str]):
        limiter = rate_limit(self.requests_per_minute)
        results = []
        docs = list(texts)

        while docs:
            # Working in batches because the API accepts maximum 5
            # documents per request to get embeddings
            head, docs = (
                docs[: self.num_instances_per_batch],
                docs[self.num_instances_per_batch :],
            )
            chunk = self.client.get_embeddings(head)
            results.extend(chunk)
            next(limiter)

        return [r.values for r in results]

# LLM model
llm = VertexAI(
    model_name="text-bison@002",
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
)

# Chat
chat = ChatVertexAI()

# Embedding
EMBEDDING_QPM = 100
EMBEDDING_NUM_BATCH = 5
embeddings = CustomVertexAIEmbeddings(
    requests_per_minute=EMBEDDING_QPM,
    num_instances_per_batch=EMBEDDING_NUM_BATCH,
)

st.set_page_config(
    page_title="Demo Langchain Vertex PaLM Text Generation API",
    page_icon=":robot:",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This app shows you how to use Vertex PaLM Text Generator API"
    }
)

#creating session states
create_session_state()



image = Image.open('./image/palm.jpg')
st.image(image)
st.title(":red[PaLM 2] :blue[Vertex AI] Text Generation")

with st.sidebar:
    image = Image.open('./image/sidebar_image.jpg')
    st.image(image)
    st.markdown("<h2 style='text-align: center; color: red;'>Setting Tab</h2>", unsafe_allow_html=True)


    st.write("Model Settings:")

    #define the temeperature for the model
    temperature_value = st.slider('Temperature :', 0.0, 1.0, 0.2)
    st.session_state['temperature'] = temperature_value

    #define the temeperature for the model
    token_limit_value = st.slider('Token limit :', 1, 1024, 256)
    st.session_state['token_limit'] = token_limit_value

    #define the temeperature for the model
    top_k_value = st.slider('Top-K  :', 1,40,40)
    st.session_state['top_k'] = top_k_value

    #define the temeperature for the model
    top_p_value = st.slider('Top-P :', 0.0, 1.0, 0.8)
    st.session_state['top_p'] = top_p_value

    if st.button("Reset Session"):
        reset_session()



with st.container():
    st.write("Current Generator Settings: ")
    # if st.session_state['temperature'] or st.session_state['debug_mode'] or :
    st.write ("Temperature: ",st.session_state['temperature']," \t \t Token limit: ",st.session_state['token_limit']
                ," \t \t Top-K: ",st.session_state['top_k']
                ," \t \t Top-P: ",st.session_state['top_p']
                ," \t \t Debug Model: ",st.session_state['debug_mode'])


    prompt = st.text_area("Add your prompt: ",height = 100)
    if prompt:
        st.session_state['prompt'].append(prompt)
        st.markdown("<h3 style='text-align: center; color: blue;'>Generator Model Response</h3>", unsafe_allow_html=True)
        with st.spinner('PaLM is working to generate, wait.....'):
            response = get_text_generation(prompt=prompt, temperature = st.session_state['temperature'],
                                max_output_tokens = st.session_state['token_limit'],
                                top_p = st.session_state['top_p'],
                                top_k = st.session_state['top_k'])
            st.session_state['response'].append(response)
            st.markdown(response)
