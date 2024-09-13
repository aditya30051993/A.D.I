from fastapi import APIRouter, UploadFile, File
from ..core.config import collection
from ..model.embedding_model import model
from PyPDF2 import PdfReader

router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    MAX_TEXT_LENGTH = 500
    text_chunks = [text[i:i + MAX_TEXT_LENGTH] for i in range(0, len(text), MAX_TEXT_LENGTH)]

    for chunk in text_chunks:
        doc_embedding = model.encode([chunk], convert_to_numpy=True)
        entities = [
            doc_embedding.tolist(),
            [chunk]
        ]
        collection.insert(entities)

    return {"message": "PDF uploaded and stored successfully."}

@router.get("/search/")
async def search(query: str):
    query_embedding = model.encode([query], convert_to_numpy=True)

    try:
        results = collection.search(
            data=query_embedding.tolist(),
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=5,
        )
        
        search_results = []
        for result in results:
            for hit in result:
                ids = [hit.id]
                collection.load()
                query_result = collection.query(expr=f"id in {ids}", output_fields=["text"])
                search_results.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "text": query_result[0]["text"]
                })

        return {"results": search_results}

    except Exception as e:
        return {"error": str(e)}
