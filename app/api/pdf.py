import json
import os
import tempfile
from typing import List
from bs4 import BeautifulSoup
from fastapi import APIRouter, UploadFile, File
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Milvus
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.documents import Document
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to Edge WebDriver executable
edge_driver_path = r"C:\Users\Mayank\Documents\msedgedriver.exe"

# Set up Edge options
edge_options = Options()
# edge_options.add_argument("--headless")  # Optional: Run headless
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-dev-shm-usage")

# Set up the Edge driver
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service, options=edge_options)

router = APIRouter()

CHUNK_SIZE = 500  # Max size of each chunk
COLLECTION_NAME = "_browser_session"  # Collection name for the browser session

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2", show_progress=True
)
vector_store = Milvus(embedding_function=embedding_function, auto_id=True)
vector_store_browser = Milvus(
    embedding_function=embedding_function, collection_name=COLLECTION_NAME, auto_id=True
)

llm = Ollama(
    model="llama3.1",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    stop=["<|eot_id|>"],
    base_url="http://192.168.6.201:9000",
)


def upload_html(html_source: str, page_url: str):
    # Parse HTML
    soup = BeautifulSoup(html_source, "html.parser")

    # Find the <body> tag
    body_tag = soup.find("body")

    # Initialize list to hold the processed chunks
    documents = []

    # Process only elements within the <body> tag
    if body_tag:
        for element in body_tag.find_all(
            recursive=True
        ):  # Traverse all elements within <body>
            # Skip if this element contains nested block elements (e.g., div, section)
            if contains_block_element(element):
                continue

            # Extract the text of this element
            text = element.get_text(separator=" ", strip=True)

            # Split the text into chunks if necessary
            chunks = split_text_into_chunks(text, CHUNK_SIZE)

            # Get the XPath for the current element
            element_xpath = get_xpath(soup, element)

            # Create documents for each chunk
            for chunk in chunks:
                document = Document(
                    page_content=chunk,
                    metadata={"url": page_url, "xpath": element_xpath},
                )
                documents.append(document)

    # Add documents to the vector store with session as "browser_session"
    vector_store_browser.add_documents(documents=documents)

    return {"message": "HTML source uploaded, chunked, and stored successfully."}


def contains_block_element(element) -> bool:
    """Check if the given element contains any block elements like div, section, etc."""
    block_elements = ["div", "section", "article", "header", "footer", "aside", "nav"]
    return any(element.find(block) for block in block_elements)


def split_text_into_chunks(text: str, max_chunk_size: int) -> List[str]:
    """Split text into smaller chunks if it exceeds the max chunk size."""
    # Split the text into chunks of up to max_chunk_size
    if len(text) <= max_chunk_size:
        return [text]

    # Split the text into chunks based on max_chunk_size
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size, chunk_overlap=0
    )
    chunks = text_splitter.split_text(text)

    return chunks


def get_xpath(soup: BeautifulSoup, element) -> str:
    """Generate a simple XPath for the given BeautifulSoup element."""
    components = []
    for parent in element.parents:
        siblings = parent.find_all(element.name, recursive=False)
        if 1 < len(siblings):
            components.append("%s[%d]" % (element.name, 1 + siblings.index(element)))
        else:
            components.append(element.name)
        element = parent
    components.reverse()
    return "/" + "/".join(components)


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


def apply_action_on_driver(action_response: dict):
    """
    Takes action response (JSON format) and applies it to the Selenium driver.

    Parameters:
    driver (webdriver.Chrome): Selenium WebDriver instance.
    action_response (dict): Action response in the form of JSON containing 'type' and 'url'.
    """
    actions = action_response.get("action", [])

    for action in actions:
        action_type = action.get("type")

        if action_type == "visit":
            # Visit a specified URL
            url = action.get("url")
            if url:
                print(f"Visiting URL: {url}")
                driver.get(url)

        elif action_type == "click":
            # Click an element by XPath
            xpath = action.get("xpath")
            if xpath:
                print(f"Clicking element with XPath: {xpath}")
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    element.click()
                except TimeoutException:
                    print(
                        f"Element with XPath {xpath} not clickable within 10 seconds."
                    )

        elif action_type == "input":
            # Input text into an element by XPath
            xpath = action.get("xpath")
            text = action.get("text", "")
            if xpath:
                print(f"Inputting text '{text}' into element with XPath: {xpath}")
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, xpath))
                    )
                    element.clear()
                    element.send_keys(text)
                except TimeoutException:
                    print(f"Element with XPath {xpath} not visible within 10 seconds.")

        else:
            print(f"Unsupported action type: {action_type}")


@router.get("/search/")
async def search(query: str):
    prompt_template = """
You are a Selenium browser assistant. You will receive a page URL, a parent XPATH, and text to work with. Additionally, you will be given a user query. Only from the context DOM, provide instructions to the Selenium driver for navigating, scrolling, clicking, or inputting if they are intended by the query. You must always provide the response with a summary of the information extracted based on the query or respond with how these actions can result in the requested information.

Return the result strictly in JSON format:
{{
  "action": [],
  "response": ""
}}

If nothing relevant is found in the context DOM and no specific URL is intended to be visited from the query, respond with: action with visit with search_query, query made to search on Google with the intent to find relevant information:
{{
  "action": [
    {{
      "type": "visit",
      "url": "{{search_query}}"
    }}
  ],
  "response": "No relevant information found. Consider searching on Google with the query: {{search_query}}."
}}

Ensure that this schema is strictly followed:
- Actions should only come from the CONTEXT DOM.
- Actions should only be for clicking or inputting.
- If a specific URL is provided in the query, visit that URL.
- If no specific URL is provided and nothing relevant is found in the CONTEXT DOM, only then share a action to visit for {{search_query}}.

Question: {question} 
Context: {context}
    """

    html = driver.page_source
    url = driver.current_url
    upload_html(html, url)

    chat_prompt = ChatPromptTemplate([("system", prompt_template)])

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vector_store_browser.as_retriever(),
        chain_type_kwargs={"prompt": chat_prompt},
    )

    result = qa_chain.invoke({"query": query})
    action_response = {}
    try:
        action_response = json.loads(result.get("result"))
    except:
        pass

    apply_action_on_driver(action_response)

    return result
