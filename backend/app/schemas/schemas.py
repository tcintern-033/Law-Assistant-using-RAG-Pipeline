from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str

class Source(BaseModel):
    document: str
    page: Optional[int] = None
    section: Optional[str] = None
    content: str

class RetrievalDiagnostics(BaseModel):
    candidates: int
    final_chunks: int
    context_characters: int

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    retrieved_chunks: int = 0  # kept for backward compatibility
    retrieval: Optional[RetrievalDiagnostics] = None
    disclaimer: str = "Educational Disclaimer: This information is provided for educational purposes only and is not a substitute for professional legal advice. Verify important legal matters against current official sources and consult a qualified legal professional where appropriate."
