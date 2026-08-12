from app.llm.base import LLMProvider
from app.config import settings
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

class HuggingFaceLLMProvider(LLMProvider):
    def __init__(self):
        token = settings.HUGGINGFACEHUB_API_TOKEN
        model_name = settings.HF_LLM_MODEL or settings.LLM_MODEL
        
        # If model_name is still set to a gemini string by mistake, default to mistral
        if "gemini" in model_name.lower():
            model_name = "mistralai/Mistral-7B-Instruct-v0.3"
            
        kwargs = {
            "repo_id": model_name,
            "temperature": 0.1,
            "max_new_tokens": 1024,
            "task": "text-generation"
        }
        
        if token:
            kwargs["huggingfacehub_api_token"] = token
            
        endpoint = HuggingFaceEndpoint(**kwargs)
        self._llm = ChatHuggingFace(llm=endpoint)

    def generate(self, prompt_template, context: str, question: str) -> str:
        chain = prompt_template | self._llm
        response = chain.invoke({"context": context, "question": question})
        return response.content if hasattr(response, "content") else str(response)

    @property
    def langchain_llm(self):
        return self._llm
