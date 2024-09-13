from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .db.milvus import connect_to_milvus, create_collection, insert_embeddings, search_embeddings

app = FastAPI()

# Connect to Milvus and create a collection
connect_to_milvus()
collection = create_collection()

# Request body models
class EmbeddingRequest(BaseModel):
    embeddings: list[list[float]]

class SearchRequest(BaseModel):
    query_embedding: list[float]
    top_k: int = 5

@app.post("/insert")
async def insert_embeddings_route(request: EmbeddingRequest):
    try:
        # Insert embeddings into the Milvus collection
        insert_embeddings(collection, request.embeddings)
        return {"status": "success", "message": "Embeddings inserted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_embeddings_route(request: SearchRequest):
    try:
        # Search for the nearest neighbors
        results = search_embeddings(collection, request.query_embedding, request.top_k)
        return {"status": "success", "results": [r.id for r in results[0]]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Milvus with FastAPI is running!"}
