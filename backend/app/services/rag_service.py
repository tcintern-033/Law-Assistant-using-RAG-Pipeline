from app.schemas.schemas import QuestionRequest, AnswerResponse, Source, RetrievalDiagnostics
from app.vectorstore.chroma import get_vectorstore
from app.rag.chain import generate_answer
from app.config import settings

def process_question(request: QuestionRequest) -> AnswerResponse:
    """Process a user question through the RAG pipeline."""
    try:
        vectorstore = get_vectorstore()
    except Exception as e:
        raise RuntimeError(f"Error initializing vector database. Did you run the ingestion script? Details: {e}")
        
    try:
        # 1. Retrieve candidates with similarity scores
        candidates_with_scores = vectorstore.similarity_search_with_score(
            request.question, 
            k=settings.RETRIEVAL_K
        )
    except Exception as e:
        raise RuntimeError(f"Error retrieving documents from vector database: {e}")
        
    # 2. Relevance Filtering
    # Chroma returns distance metrics (lower is better)
    filtered_docs = []
    for doc, score in candidates_with_scores:
        if score <= settings.SIMILARITY_THRESHOLD:
            filtered_docs.append(doc)
            
    # 3. Take Top K final chunks
    final_docs = filtered_docs[:settings.FINAL_CONTEXT_K]
        
    # Generate answer
    try:
        answer, context_chars = generate_answer(request.question, final_docs)
    except Exception as e:
        # Bubble up LLM specific errors (e.g. 429 rate limit)
        raise e
    
    # Format sources
    sources = []
    for doc in final_docs:
        sources.append(Source(
            document=doc.metadata.get("document_name", "Unknown Document"),
            page=doc.metadata.get("page"),
            section=doc.metadata.get("section"),
            content=doc.page_content
        ))
        
    return AnswerResponse(
        answer=answer,
        sources=sources,
        retrieved_chunks=len(final_docs),
        retrieval=RetrievalDiagnostics(
            candidates=len(candidates_with_scores),
            final_chunks=len(final_docs),
            context_characters=context_chars
        )
    )
