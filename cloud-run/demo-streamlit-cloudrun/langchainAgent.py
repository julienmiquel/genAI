#@title Main code: Import packages, define helper functions, tools and chains.
import requests
import re
import config as config

from pypdf import PdfReader
from vertexai.vision_models import ImageTextModel, Image
from vertexai.language_models import TextGenerationModel
from vertexai.preview.vision_models import Image, ImageGenerationModel
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.llms import VertexAI
from langchain.vectorstores import FAISS
from langchain.embeddings import VertexAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.chains import RetrievalQAWithSourcesChain

from youtubeAPI import get_transcript


# Define the LLM and its parameters
LLM_MODEL = "text-bison@002" #@param
MAX_OUTPUT_TOKENS = 1024 #@param
TEMPERATURE = 0.2 #@param
TOP_P = 0.8 #@param
TOP_K = 40 #@param
VERBOSE = False

llm_params=dict(
      model_name=LLM_MODEL,
      max_output_tokens=MAX_OUTPUT_TOKENS,
      temperature=TEMPERATURE,
      top_p=TOP_P,
      top_k=TOP_K,
    )


# Model to use with LangChain agent
llm = VertexAI(**llm_params)

# Model to generate images
image_model = model = ImageTextModel.from_pretrained("imagetext@002")

# Text model from Vertex AI
text_model = model = TextGenerationModel.from_pretrained(LLM_MODEL)


# Define a few tools to use on our conversational Agent Chat Bot Assistant.
# Tool to summarize youtube videos
def summarize(video_url):
    transcripts = get_transcript(video_url)

    transcript = '\n'.join([item['text'] for item in transcripts])
    prompt = """"
        The text below is from a youtube video. Create a summary of the transcript
        making sure you get the main points of the video:

        Text: {}
        Summary:
    """.format(transcript[:15000])
    response = text_model.predict(
        prompt,
        max_output_tokens=1024,
        temperature=0.2,)
    text = response.text
    return text


# gemini-1.0-ultra-001
#https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from tenacity import retry, stop_after_attempt, wait_random_exponential

def generate_gemini_1_pro(prompt):
  

  model_name = "gemini-1.0-pro-001"
  print(f"Start generate {model_name} based on text len: {len(prompt)}"  )

  vertexai.init(project=config.PROJECT_ID, location=config.LOCATION)
  model = GenerativeModel(model_name)



  model = GenerativeModel(model_name)
  responses = model.generate_content(prompt ,
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.,
        "top_p": 1,
        "top_k": 32
    },
    safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    },
    stream=True,
  )

  array = []
  for response in responses:
    print(response.text, end="")
    array.append(response.text)

  return "".join(array)


print("sanity check generate_gemini_1_pro")
generate_gemini_1_pro("what is gemini llm ?")

# Tool to search the company knowledge base using Vertex Search to get information
# About google Analytics documentation
def get_ga_info(question):
    es_retriever = GoogleVertexAISearchRetriever(
    project_id=config.PROJECT_ID,
    location_id='global',
    data_store_id=config.DATA_STORE_ID)

    # QA Chain
    retrieval_qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm, chain_type="stuff", retriever=es_retriever)
    answer = retrieval_qa_with_sources({"question": question})
    return answer["answer"]


# Tool to get captions of images
def get_image_description(image_url):
    response = requests.get(image_url)
    image = response.content
    source_image = Image(image)

    captions = image_model.get_captions(
        image=source_image,
        # Optional:
        number_of_results=2,
        language="en",
    )
    return captions[0]

# Tool to index a pdf to ask quesstions about it
def pdf_qa(string):
    question, pdf_url = string.split(",")
    loader = PyPDFLoader(pdf_url.strip())
    pages = loader.load_and_split()
    # Create a vector representation of each chunk from the PDF.
    vectordb = FAISS.from_documents(pages, VertexAIEmbeddings())
    # Implementation of RAG on the PDF file provided by the user)
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectordb.as_retriever())
    result = qa({"query": question})
    return result['result']

# List of tools the agent will have access to, can be extended with other tools.
tools = [
    Tool(
        name = "Image captioning",

        func=get_image_description,
        description="useful for when you recieve a image url to answer questions about that image. The function takes a parameter image_url and returns the description of that image in plain text"
    ),
    Tool(
        name = "PDF Q&A tool",
        func=pdf_qa,
        description="useful for when you need to answer questions about a pdf document. The function takes 2 parameters pdf_url and question. The input to this tool should be a comma separated string, representing the question and the pdf_url. For example, `what is this pdf about, http://pdf.com` would be the input if you wanted to as what is this pdf about given this url http://pdf.com"
    ),
    Tool(
        name="Youtube Video Sumarizer",
        func=summarize,
        description="useful for when you need to summirize the content of a youtube video and give the summary back to the user. The function takes a youtube video url as input and returns the summary of the video transcript"
    ),
    Tool(
        name="Google Analytics Documentation Search",
        func=get_ga_info,
        description="useful for when you need to answer questions about product Google Analytics. The function takes the user question as an input and returns the answer"
    )
]


context = """Assistant is a large language model.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist."""


history = ConversationBufferMemory(memory_key="chat_history")
# Agent initialization, here the ReAct prompt strategy is implemented.
agent_chain = initialize_agent(tools, llm,
                               agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                               memory=history,
                               agent_kwargs={'prefix':context})

# Final ReACT prompt
print(agent_chain.agent.llm_chain.prompt.template)

user = "User" #@param
bot = "bot" #@param
exit_command = "bye" #@param
verbose = False #@param

# Chatbot memory
history = ConversationBufferMemory(memory_key="chat_history")

# Agent initialization, here the ReAct prompt strategy is implemented.
agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=verbose, memory=history, agent_kwargs={'prefix':context})


