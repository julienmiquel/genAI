
import os

from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

# Get project, data store, and model type from env variables
#project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
#data_store_id = os.environ.get("DATA_STORE_ID")
#model_type = os.environ.get("MODEL_TYPE")

project_id = "ml-demo-384110"  # @param {type:"string"}
REGION = "europe-west1"  # @param {type:"string"}
DATA_STORE_LOCATION_ID = "global"  # Set to your data store location
data_store_id = "bq-gsoi-articles-rugby-deb_1701080507649"  # Set to your data store ID
model_type = "chat-bison"

if not data_store_id:
    raise ValueError(
        "No value provided in env variable 'DATA_STORE_ID'. "
        "A  data store is required to run this application."
    )
# Set LLM and embeddings
model = ChatVertexAI(model_name=model_type, temperature=0.0)

# Create Vertex AI retriever
retriever = GoogleVertexAISearchRetriever(
    project_id=project_id, 
    search_engine_id=data_store_id, 
    max_documents=10,
    engine_data_type=1, # structured data
)
 
def chat(query : str) :
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
        return chain.invoke(query)

    except Exception as err:
        print(f"Unexpected ERROR {err=}, {type(err)=}")    
        return f"error: {e}"