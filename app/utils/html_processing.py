from bs4 import BeautifulSoup
from typing import List
from app.core.milvus_manager import vector_store
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 500


def upload_html(html_source: str, page_url: str):
    soup = BeautifulSoup(html_source, "html.parser")
    body_tag = soup.find("body")
    documents = []

    if body_tag:
        for element in body_tag.find_all(recursive=True):
            if contains_block_element(element):
                continue
            text = element.get_text(separator=" ", strip=True)
            chunks = split_text_into_chunks(text, CHUNK_SIZE)
            element_xpath = get_xpath(soup, element)
            for chunk in chunks:
                document = Document(
                    page_content=chunk,
                    metadata={"url": page_url, "xpath": element_xpath},
                )
                documents.append(document)
    vector_store.add_documents(documents=documents)
    return {"message": "HTML source uploaded, chunked, and stored successfully."}


def contains_block_element(element) -> bool:
    block_elements = ["div", "section", "article", "header", "footer", "aside", "nav"]
    return any(element.find(block) for block in block_elements)


def split_text_into_chunks(text: str, max_chunk_size: int) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size, chunk_overlap=0
    )
    return text_splitter.split_text(text)


def get_xpath(soup: BeautifulSoup, element) -> str:
    components = []
    for parent in element.parents:
        siblings = parent.find_all(element.name, recursive=False)
        if len(siblings) > 1:
            components.append(f"{element.name}[{1 + siblings.index(element)}]")
        else:
            components.append(element.name)
        element = parent
    components.reverse()
    return "/" + "/".join(components)
