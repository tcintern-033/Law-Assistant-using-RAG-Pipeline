from app.embeddings.factory import get_embedding_provider
from langchain_core.embeddings import Embeddings

def get_embeddings() -> Embeddings:
    """Initialize and return the configured embedding model for Chroma compatibility."""
    provider = get_embedding_provider()
    return provider.langchain_embeddings
