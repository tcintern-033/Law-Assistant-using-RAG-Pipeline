import os
import sys
import traceback
from fastapi.testclient import TestClient

# Ensure we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_diagnostics():
    report = []
    
    def log(msg, status="INFO", exception=None):
        line = f"[{status}] {msg}"
        print(line)
        report.append(line)
        if exception:
            err = traceback.format_exc()
            print(err)
            report.append(err)

    log("Starting comprehensive diagnostics for RAG Law Assistant...\n")

    # 1. Configuration Validation
    log("--- Phase 1: Configuration Validation ---")
    try:
        from app.config import settings
        log(f"HUGGINGFACEHUB_API_TOKEN is set: {bool(settings.HUGGINGFACEHUB_API_TOKEN)}")
        if not settings.HUGGINGFACEHUB_API_TOKEN or settings.HUGGINGFACEHUB_API_TOKEN == "your_huggingface_token_here":
            log("WARNING: Hugging Face token is missing or default. LLM calls will likely fail.", "WARN")
        log(f"LLM Provider: {settings.LLM_PROVIDER}")
        log(f"LLM Model: {settings.HF_LLM_MODEL}")
        log(f"Embedding Provider: {settings.EMBEDDING_PROVIDER}")
        log(f"Embedding Model: {settings.HF_EMBEDDING_MODEL}")
        log("Configuration loaded successfully.", "PASS")
    except Exception as e:
        log("Failed to load configuration.", "FAIL", e)

    # 2. Embeddings & Vector Store Initialization
    log("\n--- Phase 2: Embeddings & Vector Store ---")
    try:
        from app.vectorstore.chroma import get_vectorstore
        vectorstore = get_vectorstore()
        log("Vector store initialized successfully.", "PASS")
        
        # Test basic retrieval
        query = "What is theft?"
        results = vectorstore.similarity_search_with_score(query, k=1)
        if results:
            doc, score = results[0]
            log(f"Retrieval successful. Found doc: '{doc.metadata.get('document_name', 'unknown')}' with distance {score:.4f}", "PASS")
        else:
            log("Retrieval returned empty results. Is the DB populated?", "WARN")
    except Exception as e:
        log("Failed to initialize vector store or retrieve documents.", "FAIL", e)

    # 3. LLM Connectivity
    log("\n--- Phase 3: LLM Connectivity ---")
    try:
        from app.llm.factory import get_llm_provider
        provider = get_llm_provider()
        llm = provider.langchain_llm
        log("LLM instance created successfully.", "PASS")
        
        log("Attempting to invoke LLM with a basic prompt...")
        response = llm.invoke("Respond with exactly one word: Hello")
        log(f"LLM responded successfully: {response}", "PASS")
    except Exception as e:
        log("LLM invocation failed (likely 403 Forbidden or authentication error).", "FAIL", e)

    # 4. RAG Pipeline Execution
    log("\n--- Phase 4: Full RAG Pipeline ---")
    try:
        from app.services.rag_service import process_question
        from app.schemas.schemas import QuestionRequest
        
        request = QuestionRequest(question="What is Qatl-i-Amd?")
        response = process_question(request)
        log(f"Pipeline executed successfully. Answer preview: {response.answer[:100]}...", "PASS")
    except Exception as e:
        log("RAG Pipeline execution failed.", "FAIL", e)

    # 5. API Endpoints
    log("\n--- Phase 5: FastAPI Endpoints ---")
    try:
        from app.main import app
        client = TestClient(app)
        
        # Test /health
        res_health = client.get("/health")
        if res_health.status_code == 200:
            log("/health endpoint is active.", "PASS")
        else:
            log(f"/health returned {res_health.status_code}", "FAIL")
            
        # Test /ask payload validation (empty question)
        res_ask_invalid = client.post("/ask", json={"question": ""})
        if res_ask_invalid.status_code == 400:
            log("/ask validation (empty question) working.", "PASS")
        else:
            log(f"/ask validation failed. Expected 400, got {res_ask_invalid.status_code}", "WARN")
            
    except Exception as e:
        log("FastAPI endpoint testing failed.", "FAIL", e)

    log("\n--- Diagnostics Complete ---")
    
    with open("diagnostics.log", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("\nReport saved to diagnostics.log")

if __name__ == "__main__":
    run_diagnostics()
