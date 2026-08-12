from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt_template, context: str, question: str) -> str:
        pass
    
    @property
    @abstractmethod
    def langchain_llm(self):
        """Returns the underlying LangChain LLM object for easy composition."""
        pass
