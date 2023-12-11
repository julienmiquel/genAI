
import os

from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

import json
import textwrap

# Utils
import time
import uuid
from typing import List

import numpy as np
import vertexai

# Vertex AI
from google.cloud import aiplatform

print(f"Vertex AI SDK version: {aiplatform.__version__}")

# LangChain
import langchain

print(f"LangChain version: {langchain.__version__}")

from langchain.chains import RetrievalQA
from langchain.document_loaders import GCSDirectoryLoader
from langchain.embeddings import VertexAIEmbeddings
from langchain.llms import VertexAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from langchain.retrievers import (
    GoogleVertexAIMultiTurnSearchRetriever,
    GoogleVertexAISearchRetriever,
)
from langchain.agents.agent_toolkits import create_retriever_tool



# Get project, data store, and model type from env variables
# project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
# data_store_id = os.environ.get("DATA_STORE_ID")
# model_type = os.environ.get("MODEL_TYPE")

TEXT_MODEL_VERSION =     "text-bison@002"

PROJECT_ID = "ml-demo-384110"  # @param {type:"string"}
REGION = "europe-west1"  # @param {type:"string"}
DATA_STORE_LOCATION_ID = "global"  # Set to your data store location
data_store_id = "bq-gsoi-articles-rugby-deb_1701080507649"  # Set to your data store ID
model_type = "chat-bison"

DATA_STORE_LOCATION_ID = "global"  # Set to your data store location
DATA_STORE_ID = "bq-gsoi-articles-rugby-deb_1701080507649"  # Set to your data store ID


if not data_store_id:
    raise ValueError(
        "No value provided in env variable 'DATA_STORE_ID'. "
        "A  data store is required to run this application."
    )
# Set LLM and embeddings
model = ChatVertexAI(model_name=model_type, temperature=0.0)

# Create Vertex AI retriever
retriever = GoogleVertexAISearchRetriever(
    project_id=PROJECT_ID, 
    search_engine_id=data_store_id, 
    max_documents=10,
    engine_data_type=1, # structured data
)

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
    


# Text model instance integrated with langChain
llm = VertexAI(
    model_name=TEXT_MODEL_VERSION,
    max_output_tokens=1024,
    temperature=0.2,
    top_p=1.0,
    top_k=40,
    verbose=True,
)

# Embeddings API integrated with langChain
EMBEDDING_QPM = 100
EMBEDDING_NUM_BATCH = 5
embeddings = CustomVertexAIEmbeddings(
    requests_per_minute=EMBEDDING_QPM,
    num_instances_per_batch=EMBEDDING_NUM_BATCH,
)    


def configure_retriever():



    #Configure and use the retriever for structured data
    retriever = GoogleVertexAISearchRetriever(
        project_id=PROJECT_ID,
        location_id=DATA_STORE_LOCATION_ID,
        data_store_id=DATA_STORE_ID,
        max_documents=6,
        engine_data_type=1, # structured data
    )
    return retriever


vertexsearch_tools =create_retriever_tool(
    configure_retriever(),
    name="Search",
    description="Searches and returns documents (news, articles, informations) regarding news in France. The newspaper talking about latest information in France (rugby, sport, local information, economie...). You do not know anything about rugby, local news, so if you are ever asked about news you should use this tool.",
)


template = """SYSTEM: You are a news bot assistant helping the users with their questions on sud-ouest news paper.
You answer only in the same langage of the question.
Answer with details to justify the answer.

Question: {question}

Strictly Use ONLY the following pieces of context to answer the question at the end. Think step-by-step and then answer.
Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question:

Do not try to make up an answer:
 - If the answer to the question cannot be determined from the context alone, say "I cannot determine the answer to that."
 - If the context is empty, just say "I do not know the answer to that."

=============
<ctx>
{context}
</ctx>
=============
<hs>
{history}
</hs>
=============

Question: {question}
Helpful Answer:"""


prompt = PromptTemplate(
    input_variables=["history", "context", "question"],
    template=template,
)

# Uses LLM to synthesize results from the search index.
# Use Vertex PaLM Text API for LLM
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    verbose=True,
    chain_type_kwargs={
        "verbose": True,
        "prompt": prompt,
        "memory": ConversationBufferMemory(
            memory_key="history",
            input_key="question"),
    },
)



try:

    
    
    
    # RAG prompt
    template = """Answer the question based only on the following context:
    {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

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

except Exception as err:
    print(f"Unexpected ERROR {err}, {type(err)}")    
