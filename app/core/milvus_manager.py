from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Milvus

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2", 
    show_progress=True
)

vector_store = Milvus(
    embedding_function=embedding_function,
    collection_name="_browser_session",
    auto_id=True,
)
