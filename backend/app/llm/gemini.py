from app.llm.base import LLMProvider
from app.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        model_name = settings.GEMINI_MODEL or settings.LLM_MODEL
        
        # Make sure model name is correct for gemini
        if "gemini" not in model_name.lower():
            model_name = "gemini-3.6-flash"
            
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set. Cannot initialize Gemini LLM.")
            
        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=1024
        )

    def generate(self, prompt_template, context: str, question: str) -> str:
        chain = prompt_template | self._llm
        response = chain.invoke({"context": context, "question": question})
        return response.content if hasattr(response, "content") else str(response)

    @property
    def langchain_llm(self):
        return self._llm
