import os
import textwrap
from typing import Annotated, Sequence, TypedDict

from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage
from langchain.tools import Tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS  # or Chroma, Weaviate, etc.
from langchain_openai import ChatOpenAI
from langgraph.graph import MessageGraph, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings


from .extensions import postgresdb
from .config import Config
from .mcp_client import get_mcp_client
import chromadb

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from .config import Config
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


async def get_chroma_collection(api_key):
    chroma_client = chromadb.AsyncHttpClient(
        host=Config.CHROMA_HOST,
        port=Config.CHROMA_PORT,
        ssl=False,
        headers=None,
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

    collection = chroma_client.get_or_create_collection(
        name="chats",
        embedding_function=OpenAIEmbeddingFunction(
            api_key=api_key,
            model="text-embedding-3-large",
        ),
    )
    return collection


async def add_to_chroma_collection(api_key, session_id, new_messages):
    collection = await get_chroma_collection(api_key)
    collection.add(
        documents=[
            {"content": content, "metadata": {"session_id": session_id, "role": role}}
            for role, content in new_messages.items()
        ]
    )


async def get_retriever_tool(api_key):
    collection = await get_chroma_collection(api_key)
    retriever = collection.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        name="chat_rag",
        description="""
        Use this to answer questions based on user chat history (summarized and semantically indexed).
        Use this when the user asks about prior chats, what they asked earlier, or wants a summary of past conversations.
        
        Use this tool when the user refers to anything mentioned before, asks for a summary of previous messages or sessions, 
        or references phrases like 'what I said earlier', 'things we discussed', 'my earlier question', 'until now', 'till date', 'all my conversations' or 'previously mentioned'.
        The chat history is semantically indexed and summarized using vector search.
        """,
    )
    return retriever_tool
