from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from app.core.milvus_manager import vector_store
from langchain.prompts.chat import ChatPromptTemplate

llm = Ollama(
    model="llama3.1",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    stop=["<|eot_id|>"],
    base_url="http://192.168.6.201:9000",
)

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

chat_prompt = ChatPromptTemplate([("system", prompt_template)])

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vector_store.as_retriever(),
    chain_type_kwargs={"prompt": chat_prompt},
)
