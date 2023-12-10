from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

#from rag_google_cloud_sensitive_data_protection.chain import chain as rag_google_cloud_sensitive_data_protection_chain
from rag_google_cloud_vertexai_search.chain import chain as rag_google_cloud_vertexai_search_chain
from simplechat.chain import chain as simplechat_chain
from simplechat.agentWikipedia import agentWikipedia as agent_Wikipedia


app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/ping")
async def ping():
    return {"message": "pong"}

    
add_routes(app, rag_google_cloud_vertexai_search_chain, path="/chat")
add_routes(app, simplechat_chain, path="/simplechat")
add_routes(app, agent_Wikipedia, path="/wikipedia")


#add_routes(app, rag_google_cloud_sensitive_data_protection_chain, path="/rag-google-cloud-sensitive-data-protection")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

    
    
