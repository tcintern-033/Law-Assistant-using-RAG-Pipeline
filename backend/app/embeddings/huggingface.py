from typing import List
from app.embeddings.base import EmbeddingProvider
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings

class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        # Initialize the underlying LangChain embedding model
        model_name = settings.HF_EMBEDDING_MODEL
        self._embeddings = HuggingFaceEmbeddings(model_name=model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embeddings.embed_query(text)
    
    # Langchain Chroma integration requires the provider to act somewhat like the langchain embeddings interface.
    # Exposing the underlying _embeddings is easier for integration, but if we need strict adherence:
    @property
    def langchain_embeddings(self):
        """Returns the underlying LangChain embeddings object for compatibility with Chroma."""
        return self._embeddings
