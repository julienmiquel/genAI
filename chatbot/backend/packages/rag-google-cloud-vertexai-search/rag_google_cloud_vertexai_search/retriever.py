
import os

from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

# Get project, data store, and model type from env variables
PROJECT_ID  = os.environ.get("GCP_PROJECT_ID")
REGION      =  os.environ.get("GCP_REGION")

DATA_STORE_ID           = os.environ.get("DATA_STORE_ID")
DATA_STORE_LOCATION_ID  =  os.environ.get("DATA_STORE_LOCATION_ID")
DATA_STORE_MAX_DOC = os.environ.get("DATA_STORE_MAX_DOC", 3)

LLM_CHAT_MODEL_VERSION  = os.environ.get("LLM_CHAT_MODEL_VERSION", "chat-bison@002")
LLM_TEXT_MODEL_VERSION  = os.environ.get("LLM_TEXT_MODEL_VERSION", "text-bison@002")


def get_retriever():
    # Create Vertex AI retriever
    retriever = GoogleVertexAISearchRetriever(
        project_id=PROJECT_ID, 
        data_store_id=DATA_STORE_ID, 
        location_id = DATA_STORE_LOCATION_ID,
        max_documents=DATA_STORE_MAX_DOC,
        engine_data_type=1, # structured data, 
        get_extractive_answers = True,
        max_extractive_answer_count=5,
        max_extractive_segment_count=1,
    )


    

    return retriever