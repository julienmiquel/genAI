import time
import streamlit as st

import vertexai
import utils
import json
import pandas as pd
from langchain.output_parsers import PandasDataFrameOutputParser
import gcs 
import config 
import bq
import data 
import header

header.header("Data journalism", "How to do data scrapping with langchain & Gemini ?")

default_url = "https://results.elections.europa.eu/fr/resultats-des-elections/2024-2029/"
default_prompt = """Retrieves the number of seats each group has won. Extract group, seat, percentage ​​and associated labels. 
"""

prompt_format = """
Output Format: application/json
Answer in json with key value format. 
Output must be compatible with panda dataframe input format.
All arrays must be of the same length.
"""

default_schema = """
{
"groups": [
"name 1",
"name 2"
],
"seats": [
1,
3
]
}
"""

@st.cache_data(persist=True)
def bq_event_name():
    bq_table_name = "events_scrapping_"+ utils.get_date_time_string().replace(":","").replace("-","").replace(" ","_")
    return bq_table_name

bq_table_name = bq_event_name()

url =  st.text_input("URL website to scrap", value=default_url, )
with st.expander("Change default prompt to convert data to structure datas"):
    prompt =  st.text_area("Prompt", label_visibility="hidden", value=default_prompt,  )
    #schema =  st.text_area("Schema", label_visibility="hidden", value=default_schema,  )
    bq_table = st.text_input("Bigquery table name", bq_table_name)



run_scrapping = st.button("Run")


#####################################


from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain.chains import create_extraction_chain
# Utils
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.llms.vertexai import VertexAI
from langchain_community.embeddings import VertexAIEmbeddings
from langchain.chat_models import ChatVertexAI
from google.cloud import aiplatform
import time
from typing import List

# LangChain
import langchain
from pydantic import BaseModel

print(f"LangChain version: {langchain.__version__}")
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


class CustomVertexAIEmbeddings(VertexAIEmbeddings):
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

#Define LangChain Models using Vertex AI PaLM API for Text, Chat and Vertex AI Embedding for Text

# LLM model
llm = VertexAI(
    model_name=config.GEMINI_MULTIMODAL_MODEL_NAME,
    max_output_tokens=8190,
    temperature=0.1,
    top_p=1.0,
    top_k=40,
    verbose=True,
)

# Chat
#chat = ChatVertexAI()

# Embedding
EMBEDDING_QPM = 100
EMBEDDING_NUM_BATCH = 5
embeddings = CustomVertexAIEmbeddings( model_name="textembedding-gecko@003",
    requests_per_minute=EMBEDDING_QPM,
    num_instances_per_batch=EMBEDDING_NUM_BATCH,
)

# Vertex AI

print(f"Vertex AI SDK version: {aiplatform.__version__}")

# schema = {
#     "properties": {
#         "news_article_title": {"type": "string"},
#         "news_article_summary": {"type": "string"},
#     },
#     "required": ["news_article_title", "news_article_summary"],
# }


# def extract(content: str, schema: dict):
#     chain = create_extraction_chain(schema=schema, llm=llm, verbose=True)
#     return chain.run(content)

# # Load HTML
# loader = AsyncChromiumLoader(["https://www.wsj.com"])
# html = loader.load()


import pprint

from langchain_text_splitters import RecursiveCharacterTextSplitter

def convert_url_to_slug(url):
  """Converts a web URL to a slug format.

  Args:
    url: The web URL to convert.

  Returns:
    The URL converted to slug format.
  """
  # Remove the protocol (http/https)
  url = url.replace("https://", "").replace("http://", "").replace("www.", "")


  # Replace slashes with underscores
  url = url.replace("/", "_")

  # Remove any remaining special characters
  url = url.replace(".", "-").replace(":", "-").replace("?", "-").replace("!", "-")

  return url



def scrape_with_playwright(url):
    loader = AsyncChromiumLoader([url], headless=True                                 
                                 )
    docs = loader.load()#.scrape_playwright(url=url)
    
    #docs = loader.load()
    print(f"Loaded documents {len(docs)} from urls: {url}")
    if len(docs) > 0:
        print(docs[0].page_content)
        # write file on disk
        for doc in docs:
            print(doc.metadata)
            data_dir = convert_url_to_slug(url)
            #debugFile = str(doc.metadata["source"]).replace("/","_").replace(":", "_")
            with open(f"./data_db/debug_{data_dir}.html", "w", encoding="utf-8") as f:
                f.write(doc.page_content)


    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs #, tags_to_extract=["span"]
    )

    #    # Chunk the documents
    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=1000,  # Adjust chunk size as needed
    #     chunk_overlap=200,  # Adjust overlap as needed
    #     separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    # )
    # chunked_docs = splitter.split_documents(docs)

    print("Extracting content with LLM")

    # Grab the first 1000 tokens of the site
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, 
        chunk_overlap=200,  # Adjust overlap as needed
    )
    splits = splitter.split_documents(docs_transformed)

    # data_arr = []

    

        # Store docs in local vectorstore as index
    # it may take a while since API is rate limited
    from langchain.vectorstores import Chroma

    
    db = Chroma.from_documents(splits, embeddings, persist_directory=f"./data_db/{data_dir}")
    # Expose index to the retriever
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # Create chain to answer questions
    from langchain.chains import RetrievalQA

    # Uses LLM to synthesize results from the search index.
    # We use Vertex PaLM Text API for LLM
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=False
    )
    query = f"""
TASK: {prompt} 
FORMAT: {prompt_format}
    """
    result = qa({"query": query}).get("result")
    print(result)

    # print(f"Number of splits: {len(splits)}")
    # # Process the first split
    # for split in splits:
    #     print(split.page_content)
    #     extracted_content = extract(schema=schema, content=split.page_content)
    #     pprint.pprint(extracted_content)
    #     data_arr.append(extracted_content)
    return result, query


if run_scrapping:



    # str_json_schema = utils.CleanJsonOutput(schema)
    
    # json_data = json.loads(str_json_schema)

    # df_schema = pd.DataFrame(json_data)
    # parser = PandasDataFrameOutputParser(dataframe=df_schema)

    import gemini

    
    
    extracted_content, final_prompt = scrape_with_playwright(url)
    #cleaned_content = utils.CleanJsonOutput(extracted_content)
    cleaned_content = gemini.CleanData(extracted_content)
    if len(cleaned_content) > 0:
        st.markdown("```json\n"+cleaned_content)
            
        inject_bq = st.button("Inject data into Bigquery")

        # if inject_bq:
        try:
            
        
            extracted_content = json.loads(cleaned_content)
            df = pd.DataFrame(extracted_content)
            df["update_time"] = utils.get_date_time_string()
            df["prompt"] = final_prompt
            df["url"] = url
            st.dataframe(df)

            bq.save_unsafe_bq(df,table_id=f"data_journalism.{bq_table}", project_id=config.PROJECT_ID)
            st.success("Data injected into Bigquery")
            
        except Exception as e:
            st.error(f"Bigquery injection failed because of : {e}")
            print(f"ERROR: Bigquery injection failed because of : {e}")

    else:
        st.write(extracted_content)


from app_footer import footer
footer(st)
