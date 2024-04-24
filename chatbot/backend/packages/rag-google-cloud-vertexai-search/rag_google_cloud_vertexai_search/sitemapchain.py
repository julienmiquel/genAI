import os

from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

from .retriever import get_retriever


# Get project, data store, and model type from env variables
PROJECT_ID  = os.environ.get("GCP_PROJECT_ID")
REGION      =  os.environ.get("GCP_REGION")

DATA_STORE_ID           = os.environ.get("DATA_STORE_ID")
DATA_STORE_LOCATION_ID  =  os.environ.get("DATA_STORE_LOCATION_ID")
DATA_STORE_MAX_DOC = os.environ.get("DATA_STORE_MAX_DOC", 3)

LLM_CHAT_MODEL_VERSION  = os.environ.get("LLM_CHAT_MODEL_VERSION", "chat-bison@002")
LLM_TEXT_MODEL_VERSION  = os.environ.get("LLM_TEXT_MODEL_VERSION", "text-bison@002")


if not DATA_STORE_ID:
    raise ValueError(
        "No value provided in env variable 'DATA_STORE_ID'. "
        "A  data store is required to run this application."
    )

# Set LLM and embeddings
model = ChatVertexAI(model_name=LLM_CHAT_MODEL_VERSION, 
                     temperature=0.1, 
                     top_k=30, 
                     top_p=0.85, 
                     max_tokens=1024,
                     max_output_tokens=1024, 
                     verbose=True, 
                     location=REGION, 
                     project=PROJECT_ID, 
                     )

# Create Vertex AI retriever
retriever = get_retriever()

from langchain_community.document_loaders.sitemap import SitemapLoader

sitemap_loader = SitemapLoader(web_path="https://langchain.readthedocs.io/sitemap.xml")

loader = SitemapLoader(
    web_path="https://langchain.readthedocs.io/sitemap.xml",
    filter_urls=["https://api.python.langchain.com/en/latest"],
)
documents = loader.load()

docs = sitemap_loader.load()

sitemap_loader.requests_per_second = 2
# Optional: avoid `[SSL: CERTIFICATE_VERIFY_FAILED]` issue
sitemap_loader.requests_kwargs = {"verify": False}

# RAG prompt
template = """Answer the question in French based only on the following context with the urls of sources:
{context}
Question: {question}
Answer with sources: 
"""
prompt = ChatPromptTemplate.from_template(template )

# RAG
chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | model
    | StrOutputParser() 
)


# Add typing for input
class Question(BaseModel):
    __root__: str


chain = chain.with_types(input_type=Question)
