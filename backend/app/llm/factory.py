from app.config import settings
from app.llm.base import LLMProvider
from app.llm.huggingface import HuggingFaceLLMProvider

def get_llm_provider() -> LLMProvider:
    """Factory to return the configured LLM provider."""
    return HuggingFaceLLMProvider()
