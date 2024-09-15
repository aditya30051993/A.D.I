import os
import tempfile
from fastapi import APIRouter, UploadFile, File
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Milvus
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import hub
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings


router = APIRouter()

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2", show_progress=True
)
vector_store = Milvus(embedding_function=embedding_function, auto_id=True)

llm = Ollama(
    model="llama3.1",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    stop=["<|eot_id|>"],
    base_url="http://192.168.6.201:9000",
)


@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Create a temporary file to store the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())  # Save the file contents
        temp_file.flush()  # Ensure data is written to disk
        temp_file_path = temp_file.name  # Get the file path

    try:
        # Load the PDF using the PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(data)
        vector_store.add_documents(documents=splits)

        return {"message": "PDF uploaded and stored successfully."}

    finally:
        # Delete the temporary file after processing
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.get("/search/")
async def search(query: str):
    prompt = hub.pull("rlm/rag-prompt")

    qa_chain = RetrievalQA.from_chain_type(
        llm, retriever=vector_store.as_retriever(), chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain.invoke({"query": query})

    return result
