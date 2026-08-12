import os
import hashlib
import json
from functools import lru_cache
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.embeddings.embedding import get_embeddings
from app.config import settings

def _verify_collection_compatibility(persist_directory: str):
    """Check if the currently configured embedding matches the one used to create the collection."""
    metadata_path = os.path.join(persist_directory, "collection_metadata.json")
    
    current_provider = settings.EMBEDDING_PROVIDER.lower()
    current_model = settings.HF_EMBEDDING_MODEL if current_provider in ["huggingface", "local"] else settings.EMBEDDING_MODEL
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        saved_provider = metadata.get("provider", "unknown").lower()
        saved_model = metadata.get("model", "unknown")
        
        if saved_provider != current_provider or saved_model != current_model:
            raise RuntimeError(
                f"\nERROR:\n"
                f"The existing ChromaDB collection was created using:\n"
                f"Provider: {saved_provider}\n"
                f"Model: {saved_model}\n\n"
                f"Current configuration uses:\n"
                f"Provider: {current_provider}\n"
                f"Model: {current_model}\n\n"
                f"These embedding models are incompatible.\n"
                f"Use the original embedding model or create a new collection (delete chroma_db folder)."
            )
    else:
        # Save metadata for new collection
        os.makedirs(persist_directory, exist_ok=True)
        with open(metadata_path, 'w') as f:
            json.dump({
                "provider": current_provider,
                "model": current_model
            }, f)

@lru_cache(maxsize=1)
def get_vectorstore(persist_directory: str = None) -> Chroma:
    """Initialize and return the Chroma vector store. Cached to prevent reloading on every request."""
    if persist_directory is None:
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
    _verify_collection_compatibility(persist_directory)
        
    embeddings = get_embeddings()
    
    return Chroma(
        collection_name="pakistan_law",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

def generate_chunk_id(document_name: str, page: int, chunk_index: int, content: str) -> str:
    """Generate a deterministic SHA256 ID for a document chunk."""
    raw = f"{document_name}|{page}|{chunk_index}|{content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def add_documents_to_vectorstore(documents: list[Document], persist_directory: str = None):
    """Add documents to ChromaDB. Avoids duplicates by metadata if possible (or simple add)."""
    vectorstore = get_vectorstore(persist_directory)
    
    # Extract deterministic IDs based on metadata and content
    ids = []
    for i, doc in enumerate(documents):
        doc_name = doc.metadata.get("document_name", "unknown")
        page = doc.metadata.get("page", 0)
        chunk_id = generate_chunk_id(doc_name, page, i, doc.page_content)
        ids.append(chunk_id)
        
    # Check existing IDs to prevent re-embedding
    try:
        existing_data = vectorstore.get(include=[])
        existing_ids = set(existing_data.get("ids", []))
    except Exception:
        existing_ids = set()
        
    new_docs = []
    new_ids = []
    
    for doc, doc_id in zip(documents, ids):
        if doc_id not in existing_ids:
            new_docs.append(doc)
            new_ids.append(doc_id)
            
    print(f"Total chunks: {len(documents)}")
    print(f"Already indexed: {len(documents) - len(new_docs)}")
    print(f"Remaining: {len(new_docs)}")
    
    if not new_docs:
        print("Status: COMPLETE. No new documents to add.")
        return
        
    # Batch inserts to respect memory/API rate limits and save progress
    batch_size = 100
    successfully_indexed = len(documents) - len(new_docs)
    
    for i in range(0, len(new_docs), batch_size):
        batch_docs = new_docs[i:i + batch_size]
        batch_ids = new_ids[i:i + batch_size]
        batch_num = i//batch_size + 1
        print(f"\nProcessing Batch: {batch_num}")
        try:
            vectorstore.add_documents(documents=batch_docs, ids=batch_ids)
            successfully_indexed += len(batch_docs)
            print(f"Successfully indexed: {successfully_indexed}")
            print(f"Remaining: {len(documents) - successfully_indexed}")
            
            if i + batch_size < len(new_docs):
                import time
                if settings.EMBEDDING_PROVIDER.lower() == "google":
                    print("Sleeping for 10 seconds to respect API rate limits...")
                    time.sleep(10)
        except Exception as e:
            print(f"\n❌ Embedding failed")
            print(f"Provider: {settings.EMBEDDING_PROVIDER}")
            print(f"Batch: {batch_num}")
            print(f"Successfully indexed: {successfully_indexed}")
            print(f"Remaining: {len(documents) - successfully_indexed}")
            print(f"\nExisting ChromaDB data has been preserved.")
            print(f"Run ingestion again after resolving the provider issue. Details: {e}")
            break
            
    if successfully_indexed == len(documents):
        print("\nStatus: COMPLETE")
