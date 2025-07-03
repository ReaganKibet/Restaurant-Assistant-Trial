from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger
import time
import os

from app.models.schemas import (
    ConversationRequest, StartConversationRequest, 
    ChatResponse, ChatMessage, UserPreferences
)
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage, UserPreferences
from app.core.conversation_manager import ConversationManager
from app.services.llm_service import LLMService
from app.services.menu_service import MenuService

router = APIRouter(prefix="/chat", tags=["chat"])

# Create a single, shared instance
llm_service = LLMService()
menu_service = MenuService()
conversation_manager = ConversationManager(llm_service, menu_service)


# Dependency injection
def get_conversation_manager():
    return conversation_manager  # <-- GOOD: always the same instance!

def get_llm_service():
    return LLMService()

# Chat Request Schema
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    preferences: Optional[UserPreferences] = None

LOGS_DIR = r"C:\Users\Elitebook\OneDrive\Documents\PROJECTS\Restaurant Assistant Trial 4\logs"
SESSIONS_LOG_FILE = os.path.join(LOGS_DIR, "active_sessions.log")

def log_active_sessions(session_ids):
    """Write all active session IDs to the sessions log file."""
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(SESSIONS_LOG_FILE, "w") as f:
            for sid in session_ids:
                f.write(f"{sid}\n")
    except Exception as e:
        logger.error(f"Failed to write active sessions log: {e}")

@router.post("/start", response_model=ChatResponse)
async def start_conversation(
    preferences: Optional[UserPreferences] = None,
    conv_manager: ConversationManager = Depends(get_conversation_manager)
):
    """Start a new conversation session"""
    try:
        response = await conv_manager.start_conversation(preferences=preferences)
        logger.info(f"Started new session: {response.session_id}")
        # Log all active session IDs for debugging
        session_ids = list(conv_manager.sessions.keys())
        logger.debug(f"All active sessions: {session_ids}")
        log_active_sessions(session_ids)
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
        # Log all active session IDs for debugging
        session_ids = list(conv_manager.sessions.keys())
        logger.debug(f"All active sessions before processing: {session_ids}")
        log_active_sessions(session_ids)

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

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    start_time = time.time()
    
    try:
        # Try Gemini first, fallback to Ollama if needed
        result = await llm_service.generate_response(
            prompt=request.message,
            context=request.context,
            use_fallback=True  # Always allow fallback
        )
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=result["response"],
            provider=result["provider"],  # "gemini" or "ollama"
            success=result["success"],
            fallback_used=result.get("fallback_used", False),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat", "providers": ["gemini", "ollama"]}
