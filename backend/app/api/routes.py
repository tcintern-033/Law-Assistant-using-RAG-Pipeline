from fastapi import APIRouter, HTTPException
from app.schemas.schemas import QuestionRequest, AnswerResponse
from app.services.rag_service import process_question

router = APIRouter()

@router.get("/")
async def root():
    return {
        "message": "Pakistan Law RAG Assistant API",
        "status": "running"
    }

@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }

@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    if len(request.question) > 1000:
        raise HTTPException(status_code=400, detail="Question is too long.")
        
    try:
        response = process_question(request)
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
