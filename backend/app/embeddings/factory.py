from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.huggingface import HuggingFaceEmbeddingProvider

def get_embedding_provider() -> EmbeddingProvider:
    """Factory to return the configured embedding provider."""
    return HuggingFaceEmbeddingProvider()
