import os
import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Add the parent directory to the Python path so we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.loaders.document_loader import load_documents
from app.vectorstore.chroma import add_documents_to_vectorstore

def main():
    print("Starting document ingestion process...")
    
    # 1. Load documents
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    documents = load_documents(data_dir=data_dir)
    
    if not documents:
        print("No documents found in the data directory. Please add PDFs to data/ and try again.")
        return
        
    print(f"Total documents loaded: {len(documents)}")
    
    # 2. Split documents
    # Using chunk_size=1000 and chunk_overlap=150 as a starting point. 
    # These can be tuned later for optimal legal text retrieval.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150
    )
    
    print("Splitting documents into chunks...")
    chunks = text_splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")
    
    # 3. Store in ChromaDB
    chroma_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../chroma_db"))
    add_documents_to_vectorstore(chunks, persist_directory=chroma_dir)
    
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
