from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from rag_google_cloud_vertexai_search.chain import chain as rag_google_cloud_vertexai_search_chain
from rag_google_cloud_vertexai_search.stuff_chain import qa_chain, retrieval_qa, conversational_retrieval 
from rag_google_cloud_vertexai_search.datastore import refresh_data_store

# Create the FastAPI app
app = FastAPI()

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

ping_count = 0

@app.get("/ping")
@app.post("/ping")
async def ping():
    global ping_count
    ping_count = ping_count + 1
    return {"message": f"pong-{ping_count}"}
    
@app.get("/refresh")
@app.post("/refresh")
async def refresh():    
    refresh_data_store()
    return {"message": "refreshed"}
    
add_routes(app, rag_google_cloud_vertexai_search_chain, path="/chat")

add_routes(app, qa_chain, path="/qa")
add_routes(app, retrieval_qa, path="/retrieval_qa")
add_routes(app, conversational_retrieval, path="/conversational_retrieval")

def start():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    

if __name__ == "__main__":
    start()