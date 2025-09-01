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
from app.core.conversation_manager import ConversationManager
from app.services.llm_service import LLMService
from app.services.menu_service import MenuService

router = APIRouter(tags=["chat"])

# Import the global services from main.py instead of creating new instances
def get_conversation_manager():
    from app.main import conversation_manager
    if conversation_manager is None:
        raise HTTPException(status_code=503, detail="Conversation service not initialized")
    return conversation_manager

def get_llm_service():
    from app.main import llm_service
    if llm_service is None:
        raise HTTPException(status_code=503, detail="LLM service not initialized")
    return llm_service

def get_menu_service():
    from app.main import menu_service
    if menu_service is None:
        raise HTTPException(status_code=503, detail="Menu service not initialized")
    return menu_service

# Chat Request Schema
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    preferences: Optional[UserPreferences] = None

LOGS_DIR = os.path.join(os.getcwd(), "logs")
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
    request: StartConversationRequest,
    conv_manager: ConversationManager = Depends(get_conversation_manager)
):
    """Start a new conversation session"""
    try:
        response = await conv_manager.start_conversation(preferences=request.preferences)
        logger.info(f"Started new session: {response.session_id}")
        # Log all active session IDs for debugging
        session_ids = list(conv_manager.sessions.keys())
        logger.debug(f"All active sessions: {session_ids}")
        log_active_sessions(session_ids)
        return response
    except Exception as e:
        logger.error(f"Start error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    conv_manager: ConversationManager = Depends(get_conversation_manager)
):
    """Send a message to the assistant"""
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
            
        # Check if session exists
        if request.session_id not in conv_manager.sessions:
            raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
            
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

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.warning(f"Invalid session ID: {request.session_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except AttributeError as e:
        logger.error(f"Method not found error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Service method error: {str(e)}")
    except Exception as e:
        logger.error(f"Message error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")
    
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
        logger.error(f"History error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")

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
        logger.error(f"End error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to end conversation: {str(e)}")

@router.post("/", response_model=dict)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    start_time = time.time()
    
    try:
        # Try Gemini first, fallback to Ollama if needed
        result = await llm_service.generate_response(
            prompt=request.message,
            use_fallback=True  # Always allow fallback
        )
        
        processing_time = time.time() - start_time
        
        return {
            "message": result["response"],
            "provider": result["provider"],
            "success": result["success"],
            "fallback_used": result.get("fallback_used", False),
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat", "providers": ["gemini", "ollama"]}
