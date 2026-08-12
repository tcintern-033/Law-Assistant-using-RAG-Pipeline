from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.rag.prompt import get_rag_prompt
from app.config import settings

def format_docs(docs):
    """Format documents into a readable string for the prompt, strictly limiting character count."""
    context_parts = []
    total_chars = 0
    max_chars = settings.MAX_CONTEXT_CHARS

    for i, doc in enumerate(docs):
        doc_name = doc.metadata.get("document_name", "Unknown Document")
        page = doc.metadata.get("page", "Unknown Page")
        section = doc.metadata.get("section", "Unknown Section")
        
        meta_str = f"Document: {doc_name}\nPage: {page}"
        if section != "Unknown Section":
            meta_str += f"\nSection: {section}"
            
        chunk_text = f"SOURCE {i+1}\n{meta_str}\nContent:\n{doc.page_content}"
        
        if total_chars + len(chunk_text) > max_chars:
            print(f"Context limit reached at chunk {i+1}. Stopping context injection.")
            break
            
        context_parts.append(chunk_text)
        total_chars += len(chunk_text)
        
    return "\n\n".join(context_parts), total_chars

from app.llm.factory import get_llm_provider

def get_llm():
    """Initialize the LLM using the configured provider."""
    provider = get_llm_provider()
    return provider.langchain_llm

def generate_answer(question: str, docs: list) -> tuple[str, int]:
    """Generate an answer using the LLM based on retrieved docs."""
    # Custom grounding check
    if not docs:
        return "The available legal documents do not contain enough information to answer this question reliably.", 0
        
    prompt = get_rag_prompt()
    llm = get_llm()
    output_parser = StrOutputParser()
    
    chain = prompt | llm | output_parser
    
    context, context_chars = format_docs(docs)
    print(f"Sending prompt to LLM ({settings.LLM_PROVIDER}): Question len={len(question)}, Context chars={context_chars}")
    
    try:
        response = chain.invoke({
            "context": context,
            "question": question
        })
        return response, context_chars
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Error during LLM invocation: {e}")
        # Identify rate limits/quota exhaustion (HTTP 429)
        if "429" in error_msg or "resource_exhausted" in error_msg or "quota" in error_msg:
            raise RuntimeError("The AI service is temporarily rate-limited or out of quota. Please try again shortly.")
        raise RuntimeError("An error occurred while generating the answer from the legal context.")
