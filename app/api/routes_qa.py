from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.services.rag_service import RAGService
from app.services.menu_service import MenuService
from app.config import settings

router = APIRouter(prefix="/qa", tags=["Q&A"])

class QuestionRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None

class QAPairRequest(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None

def get_rag_service(menu_service: MenuService = Depends()) -> RAGService:
    return RAGService(menu_service)

@router.post("/ask")
async def ask_question(
    request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """
    Ask a question about the menu and get an answer
    """
    try:
        response = await rag_service.get_menu_qa(
            question=request.question,
            context=request.context
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

@router.post("/add-qa")
async def add_qa_pair(
    request: QAPairRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, str]:
    """
    Add a new Q&A pair to the knowledge base
    """
    try:
        await rag_service.add_qa_pair(
            question=request.question,
            answer=request.answer,
            category=request.category
        )
        return {"message": "Q&A pair added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding Q&A pair: {str(e)}"
        )

@router.post("/update-embeddings")
async def update_embeddings(
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, str]:
    """
    Update menu item embeddings
    """
    try:
        await rag_service.update_menu_embeddings()
        return {"message": "Menu embeddings updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating embeddings: {str(e)}"
        ) 