import time
import streamlit as st

import vertexai
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Image,
    Part,
)
import gemini

import utils
import json
import pandas as pd
from langchain.output_parsers import PandasDataFrameOutputParser
import gcs 
import config 
import bq
import data 
import header

header.header("IA journalism", "Sugest meta-data from an article.")

import app_sidebar
language_code_gemini, multimodal_model_name_gemini =  app_sidebar.get_sidebar_config()


default_url = "https://www.lanouvellerepublique.fr/blois/blois-le-rider-stephane-meneau-prend-son-envol"
default_prompt = f"""Use only the article body as source.
Answer in {language_code_gemini}.
Answer each questions in a string or sentence: 
 - What is the title of the article ?
 - What is the summary of the article ?
 - Is the sentiment positive or negative on the article ?
 - What are the tags of this articles ?
 - What are the tags to optimize SEO ?
 - What are the list of topics of this text ?
 - Multi-choice problem: What is the topic of this text? (entertainment, technology, politics, sports, business, health, fun, culture, science, fait-divers) ?
 - Export location present in this article ?
 - Export name of people in this article ?
 - Export date and event name as dictionary ?
 - Export date and location as dictionary ?
"""



# @st.cache_data(persist=True)
# def bq_event_name():
#     bq_table_name = "events_scrapping_"+ utils.get_date_time_string().replace(":","").replace("-","").replace(" ","_")
#     return bq_table_name

# bq_table_name = bq_event_name()

# url =  st.text_input("URL website to scrap", value=default_url, )

body_text= st.text_area(label="body_text", label_visibility="hidden", value="""Vendée : Julie Depardieu et Yves Duteil à l’affiche des Estivales de Caractère
Julie Depardieu sera à Pouzauges, le 22 juillet.

Par Dominique MICHONNEAU
Publié le 07/07/2024 à 18:05, mis à jour le 07/07/2024 à 20:45
Le festival sud-vendéen Les Estivales de Caractère propose cinq concerts, du 10 juillet au 18 septembre. À l’affiche : Julie Depardieu, Yves Duteil et le ténor Novelli.

L’association des Petites Cités de Caractère de la Vendée fête les 25 ans de son festival Les Nuits musicales en Vendée romane, devenu en 2023 Les Estivales de caractère. C’est Kora Jazz Trio qui ouvre le bal, le 10 juillet, en l’église de Nieul-sur-l’Autise (Rives-d’Autise), avant quatre autres concerts jusqu’au 18 septembre.


« Neuf communes vendéennes adhèrent à l’association. Ce festival permet d’accueillir des artistes de très haut niveau et d’horizons divers (musique actuelle, classique, baroque, jazz, chanson française, etc.) qui se produisent dans nos cités de caractère dont le patrimoine est aussi mis en valeur à chacune de ces représentations », résume Joseph Baudouin, président de l’association des Petites Cités de Caractère de la Vendée et Pays de la Loire.

Cette fois encore, l’édition 2024 des Estivales de Caractère offre une affiche d’artistes éclectiques, se produisant au cœur de sites remarquables, telle la chapelle des mineurs de Faymoreau de 1876, enrichie en 2001 de dix-neuf grands vitraux contemporains de Carmelo Zagari, dont la double lecture spirituelle (la Sainte Famille) et profane (le thème de la mine) est unique en France.

Jazz, classique et chant
Mercredi 10 juillet, à Nieul-sur-l’Autise (commune de Rives-d’Autise), à l’église, à 21 h, Kora Jazz Trio accordera le jazz et la musique mandingue, portés notamment par Abdoulaye Diabaté, pianiste et compositeur africain.


Jeudi 18 juillet, à Mortagne-sur-Sèvre, à l’église, à 21 h, David Enhco & Marc Perrenoud rendront hommage au grand trompettiste de jazz américain Chet Baker, David Enhco étant double Victoires du jazz.


Lundi 22 juillet, à Pouzauges, à l’église, à 21 h, Julie Depardieu lira des textes illustrant un hommage à Clara et Robert Schumann, notamment, avec des chants de la grande mezzo-soprano Delphine Haidan, et la pianiste Dana Ciocarlie.

Mardi 6 août, à Faymoreau, à la chapelle des Mineurs, à 21 h, le ténor Jean-François Novelli et la pianiste Maud Graton élèveront des compositeurs oubliés et grandes stars dans un récital de mélodies classiques.

Jean-François Novelli sera à Faymoreau, le 6 août.


Mercredi 18 septembre, à Mouchamps, à l’église, à 21 h, Yves Duteil (piano, guitare) se produira dans le cadre de sa tournée Chemin d’écriture, avec Philippe Nadal au violoncelle et Gilles Bloteau (basse, contrebasse).

Tarifs : 20 €, réduit 15 € la soirée. Concert de Julie Depardieu, Delphine Haidan, et Dana Ciocarlie : 25 € et 20 €. Yves Duteil : 34 €, réduit 29 €. Gratuit jusqu’à 10 ans. Renseignements et réservations : www.festival-vendee.com et 02.51.51.48.92.
"""  )

with st.expander("Change default prompt to generate hastags"):
    prompt =  st.text_area("Prompt", label_visibility="hidden", value=default_prompt,  )
    #schema =  st.text_area("Schema", label_visibility="hidden", value=default_schema,  )
    # bq_table = st.text_input("Bigquery table name", bq_table_name)



run = st.button("Run")


if run:
    results = gemini.generate_prompt(text=body_text, prompt=prompt, model=multimodal_model_name_gemini)
    with st.spinner("In progress..."):
        with st.expander(f"Text generated in real-time by gemini {multimodal_model_name_gemini}", expanded=True):
            for result in results:
                if result[0] is not None:
                    st.markdown(result[0])                    

                if result[1] is not None:
                    generated_json = result[1]
    
    with st.expander(f"Final text generated by gemini {multimodal_model_name_gemini}", expanded=True):
            #st.markdown(generated_transcript)
            st.markdown("```json:\n" + generated_json.replace("\",","\",\n").replace(". ", ".\n").replace("  ", " ")
                        .replace("[","[\n").replace("]","\n]").replace("}","}\n").replace("{","{\n") + "\n```")

#####################################


# from langchain_community.document_loaders import AsyncChromiumLoader
# from langchain_community.document_transformers import BeautifulSoupTransformer
# from langchain.chains import create_extraction_chain
# # Utils
# from langchain.schema import HumanMessage, SystemMessage
# from langchain_community.llms.vertexai import VertexAI
# from langchain_community.embeddings import VertexAIEmbeddings
# from langchain.chat_models import ChatVertexAI
# from google.cloud import aiplatform
# import time
# from typing import List

# # LangChain
# import langchain
# from pydantic import BaseModel

# print(f"LangChain version: {langchain.__version__}")
# # Utility functions for Embeddings API with rate limiting
# def rate_limit(max_per_minute):
#     period = 60 / max_per_minute
#     print("Waiting")
#     while True:
#         before = time.time()
#         yield
#         after = time.time()
#         elapsed = after - before
#         sleep_time = max(0, period - elapsed)
#         if sleep_time > 0:
#             print(".", end="")
#             time.sleep(sleep_time)


# class CustomVertexAIEmbeddings(VertexAIEmbeddings):
#     requests_per_minute: int
#     num_instances_per_batch: int

#     # Overriding embed_documents method
#     def embed_documents(self, texts: List[str]):
#         limiter = rate_limit(self.requests_per_minute)
#         results = []
#         docs = list(texts)

#         while docs:
#             # Working in batches because the API accepts maximum 5
#             # documents per request to get embeddings
#             head, docs = (
#                 docs[: self.num_instances_per_batch],
#                 docs[self.num_instances_per_batch :],
#             )
#             chunk = self.client.get_embeddings(head)
#             results.extend(chunk)
#             next(limiter)

#         return [r.values for r in results]

# #Define LangChain Models using Vertex AI PaLM API for Text, Chat and Vertex AI Embedding for Text

# # LLM model
# llm = VertexAI(
#     model_name=config.GEMINI_MULTIMODAL_MODEL_NAME,
#     max_output_tokens=8190,
#     temperature=0.1,
#     top_p=1.0,
#     top_k=40,
#     verbose=True,
# )

# # Chat
# #chat = ChatVertexAI()

# # Embedding
# EMBEDDING_QPM = 100
# EMBEDDING_NUM_BATCH = 5
# embeddings = CustomVertexAIEmbeddings( model_name="textembedding-gecko@003",
#     requests_per_minute=EMBEDDING_QPM,
#     num_instances_per_batch=EMBEDDING_NUM_BATCH,
# )

# # Vertex AI

# print(f"Vertex AI SDK version: {aiplatform.__version__}")

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


# import pprint

# from langchain_text_splitters import RecursiveCharacterTextSplitter

# def convert_url_to_slug(url):
#   """Converts a web URL to a slug format.

#   Args:
#     url: The web URL to convert.

#   Returns:
#     The URL converted to slug format.
#   """
#   # Remove the protocol (http/https)
#   url = url.replace("https://", "").replace("http://", "").replace("www.", "")


#   # Replace slashes with underscores
#   url = url.replace("/", "_")

#   # Remove any remaining special characters
#   url = url.replace(".", "-").replace(":", "-").replace("?", "-").replace("!", "-")

#   return url



# def scrape_with_playwright(url):
#     loader = AsyncChromiumLoader([url], headless=True
#                                  #, user_agent="Chrome/114.0.0.0"
#                                  )
#     #docs = loader.ascrape_playwright(url=url)
    
    
#     docs = loader.load()
#     from langchain_community.document_transformers import Html2TextTransformer

#     html2text = Html2TextTransformer()
#     docs = html2text.transform_documents(docs)

#     print(f"Loaded documents {len(docs)} from urls: {url}")
#     if len(docs) > 0:
#         print(docs[0].page_content)
#         # write file on disk
#         for doc in docs:
#             print(doc.metadata)
#             data_dir = convert_url_to_slug(url)
#             #debugFile = str(doc.metadata["source"]).replace("/","_").replace(":", "_")
#             with open(f"./data_db/debug_{data_dir}.txt", "w", encoding="utf-8") as f:
#                 f.write(doc.page_content)


#     bs_transformer = BeautifulSoupTransformer()
#     docs_transformed = bs_transformer.transform_documents(
#         docs #, tags_to_extract=["span"]
#     )

#     #    # Chunk the documents
#     # splitter = RecursiveCharacterTextSplitter(
#     #     chunk_size=1000,  # Adjust chunk size as needed
#     #     chunk_overlap=200,  # Adjust overlap as needed
#     #     separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
#     # )
#     # chunked_docs = splitter.split_documents(docs)

#     print("Extracting content with LLM")

#     # Grab the first 1000 tokens of the site
#     splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#         chunk_size=2000, 
#         chunk_overlap=500,  # Adjust overlap as needed
#     )
#     splits = splitter.split_documents(docs_transformed)

#     # data_arr = []

    

#         # Store docs in local vectorstore as index
#     # it may take a while since API is rate limited
#     from langchain.vectorstores import Chroma

    
#     db = Chroma.from_documents(splits, embeddings, persist_directory=f"./data_db/{data_dir}")
#     # Expose index to the retriever
#     retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 2})

#         # Create chain to answer questions
#     from langchain.chains import RetrievalQA

#     # Uses LLM to synthesize results from the search index.
#     # We use Vertex PaLM Text API for LLM
#     qa = RetrievalQA.from_chain_type(
#         llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
#     )
#     query = f"""
# TASK: {prompt} 
# FORMAT: {prompt_format}
#     """
#     result = qa({"query": query}).get("result")
#     print(result)

#     # print(f"Number of splits: {len(splits)}")
#     # # Process the first split
#     # for split in splits:
#     #     print(split.page_content)
#     #     extracted_content = extract(schema=schema, content=split.page_content)
#     #     pprint.pprint(extracted_content)
#     #     data_arr.append(extracted_content)
#     return result, query


if False:



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
