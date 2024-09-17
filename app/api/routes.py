from fastapi import APIRouter, UploadFile, File
from app.utils.html_processing import upload_html
from app.utils.pdf_processing import process_pdf
from app.core.ollama_manager import qa_chain
from app.core.selenium_driver import driver, apply_action_on_driver
import json

router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    return await process_pdf(file)

@router.get("/search_pdf/")
async def search(query: str):
    result = qa_chain.invoke({"query": query})
    return result

@router.get("/assistant/")
async def assistant(query: str):
    html = driver.page_source
    url = driver.current_url
    upload_html(html, url)

    result = qa_chain.invoke({"query": query})
    action_response = {}
    
    try:
        action_response = json.loads(result.get("result"))
    except:
        pass

    apply_action_on_driver(action_response)

    return result
