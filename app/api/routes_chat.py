from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.models.schemas import (
    ConversationRequest, StartConversationRequest, 
    ChatResponse, ChatMessage, UserPreferences
)
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage, UserPreferences
from app.core.conversation_manager import ConversationManager
from app.services.llm_service import LLMService
from app.services.menu_service import MenuService

router = APIRouter()

# Create a single, shared instance
llm_service = LLMService()
menu_service = MenuService()
conversation_manager = ConversationManager(llm_service, menu_service)


# Dependency injection
def get_conversation_manager():
    return ConversationManager(llm_service, menu_service)

# Chat Request Schema
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    preferences: Optional[UserPreferences] = None

@router.post("/start", response_model=ChatResponse)
async def start_conversation(
    preferences: Optional[UserPreferences] = None,
    conv_manager: ConversationManager = Depends(get_conversation_manager)
):
    """Start a new conversation session"""
    try:
        response = await conv_manager.start_conversation(preferences=preferences)
        logger.info(f"Started new session: {response.session_id}")
        return response
    except Exception as e:
        logger.error(f"Start error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start conversation")

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    conv_manager: ConversationManager = Depends(get_conversation_manager)
):
    """Send a message to the assistant"""
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")

        response = await conv_manager.process_message(
            message=request.message,
            session_id=request.session_id,
            preferences=request.preferences
        )
        logger.info(f"Processed message for session: {request.session_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid session ID: {request.session_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Message error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.get("/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    conv_manager: ConversationManager = Depends(get_conversation_manager)
):
    """Get chat history for a session"""
    try:
        return await conv_manager.get_chat_history(session_id)
    except ValueError as e:
        logger.warning(f"Invalid session ID: {session_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.delete("/session/{session_id}")
async def end_conversation(
    session_id: str,
    conv_manager: ConversationManager = Depends(get_conversation_manager)
):
    """End a session and clean up resources"""
    try:
        await conv_manager.end_conversation(session_id)
        logger.info(f"Ended session: {session_id}")
        return {"message": "Conversation ended successfully"}
    except ValueError as e:
        logger.warning(f"Invalid session ID: {session_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"End error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end conversation")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat"}
