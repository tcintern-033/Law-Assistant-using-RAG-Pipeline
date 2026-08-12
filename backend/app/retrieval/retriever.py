from langchain_core.retrievers import BaseRetriever
from app.vectorstore.chroma import get_vectorstore
from app.config import settings

def get_retriever() -> BaseRetriever:
    """Initialize and return the retriever for RAG."""
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.TOP_K}
    )
