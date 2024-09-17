import os
import tempfile
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.milvus_manager import vector_store

async def process_pdf(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())
        temp_file.flush()
        temp_file_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_file_path)
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(data)
        vector_store.add_documents(documents=splits)

        return {"message": "PDF uploaded and stored successfully."}
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
