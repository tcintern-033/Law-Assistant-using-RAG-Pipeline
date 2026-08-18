import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", os.getenv("HF_TOKEN", ""))
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Provider Settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "huggingface")
    
    # Model Specific Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
    HF_LLM_MODEL: str = os.getenv("HF_LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
    HF_EMBEDDING_MODEL: str = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    # RAG Tuning Settings
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "../chroma_db")
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "8"))
    FINAL_CONTEXT_K: int = int(os.getenv("FINAL_CONTEXT_K", "4"))
    MAX_CONTEXT_CHARS: int = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "50.0"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
