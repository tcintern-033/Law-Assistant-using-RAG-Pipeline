import os
import glob
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

_ocr_reader = None

def get_ocr_reader():
    """Lazily load EasyOCR to save memory."""
    global _ocr_reader
    if _ocr_reader is None:
        print("Initializing EasyOCR for Urdu/English (this will download model weights on first run)...")
        import easyocr
        # Force CPU if no GPU available to prevent crashes
        _ocr_reader = easyocr.Reader(['ur', 'en'], gpu=False)
    return _ocr_reader

def get_document_name(filename: str) -> str:
    """Extract a clean document name from the filename."""
    base_name = os.path.basename(filename).replace(".pdf", "")
    return base_name.replace("_", " ").title()

def load_urdu_ocr_pdf(pdf_path: str, doc_name: str) -> list[Document]:
    """Render PDF pages to images and use EasyOCR to extract Urdu/English text."""
    import fitz # PyMuPDF
    reader = get_ocr_reader()
    pdf_doc = fitz.open(pdf_path)
    docs = []
    
    print(f"Starting OCR extraction for {doc_name} ({len(pdf_doc)} pages)...")
    for i in range(len(pdf_doc)):
        page = pdf_doc[i]
        # 150 DPI is a good balance between OCR accuracy and processing speed
        pix = page.get_pixmap(dpi=150)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        if pix.n == 4:
            img = img[:, :, :3] # Remove alpha channel
            
        result = reader.readtext(img, detail=0)
        text = "\n".join(result)
        
        metadata = {
            "source": os.path.basename(pdf_path),
            "document_name": doc_name,
            "document_type": "legal_document",
            "page": i
        }
        docs.append(Document(page_content=text, metadata=metadata))
        
        if (i+1) % 10 == 0:
            print(f"OCR Progress: {i+1}/{len(pdf_doc)} pages")
            
    return docs

def load_documents(data_dir: str = "../data") -> list[Document]:
    """Load all PDFs from the data directory and attach metadata."""
    if not os.path.exists(data_dir):
        print(f"Warning: Directory {data_dir} does not exist. No documents loaded.")
        return []
        
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    all_documents = []
    
    for pdf_path in pdf_files:
        try:
            doc_name = get_document_name(pdf_path)
            
            # The Constitution PDF is non-Unicode Urdu, so we MUST OCR it
            if "constitution" in doc_name.lower():
                docs = load_urdu_ocr_pdf(pdf_path, doc_name)
            else:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                
                # Attach extra metadata for PyPDFLoader
                for doc in docs:
                    doc.metadata["source"] = os.path.basename(pdf_path)
                    doc.metadata["document_name"] = doc_name
                    doc.metadata["document_type"] = "legal_document"
                    
            all_documents.extend(docs)
            print(f"Loaded {len(docs)} pages from {doc_name}")
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")
            
    return all_documents
