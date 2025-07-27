from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from .config import Config

async def update_vector_index(api_key, session_id, new_messages):
    docs = []
    for role, content in new_messages.items():
        if content:
            doc = Document(
                page_content=content,
                metadata={"session_id": session_id, "role": role}
            )
            docs.append(doc)

    if docs:
        embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-large")
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=Config.CHROMA_PERSIST_DIRECTORY
        )
        vectorstore.add_documents(docs)
        vectorstore.persist()