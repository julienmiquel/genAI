from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from rag_google_cloud_vertexai_search.chain import chain as rag_google_cloud_vertexai_search_chain
from rag_google_cloud_vertexai_search.stuff_chain import qa_chain, retrieval_qa, conversational_retrieval 

app = FastAPI()

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/ping")
async def ping():
    return {"message": "pong"}
    
add_routes(app, rag_google_cloud_vertexai_search_chain, path="/chat")

add_routes(app, qa_chain, path="/qa")
add_routes(app, retrieval_qa, path="/retrieval_qa")
add_routes(app, conversational_retrieval, path="/conversational_retrieval")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

    
    
