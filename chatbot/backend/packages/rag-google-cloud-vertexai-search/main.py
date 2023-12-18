from rag_google_cloud_vertexai_search.chain import chain
from rag_google_cloud_vertexai_search.stuff_chain import qa_chain, retrieval_qa, conversational_retrieval 

if __name__ == "__main__":
    try :
        
        query = "Who is the CEO of Google Cloud?"
        print(chain.invoke(query))

        query = "Qu'a dit René Bouscatel ?"
        print("chain : " +  chain.invoke(query))
        print("qa_chain : " +  qa_chain.invoke(query))
        print("retrieval_qa : " +  retrieval_qa.invoke(query))
        print("conversational_retrieval : " +  conversational_retrieval.invoke(query))
    except Exception as e:
        print(f"initalisation error : {e}" )
