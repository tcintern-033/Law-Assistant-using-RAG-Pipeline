from app.config import settings
from app.llm.base import LLMProvider
from app.llm.huggingface import HuggingFaceLLMProvider
from app.llm.gemini import GeminiLLMProvider

def get_llm_provider() -> LLMProvider:
    """Factory to return the configured LLM provider."""
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "gemini":
        return GeminiLLMProvider()
    elif provider == "huggingface":
        return HuggingFaceLLMProvider()
    else:
        # Default to huggingface if unknown
        return HuggingFaceLLMProvider()
