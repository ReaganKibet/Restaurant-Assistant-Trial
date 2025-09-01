from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.routing import Route, Mount

from app.api import routes_chat, routes_meals, routes_admin
from app.core.conversation_manager import ConversationManager
from app.services.llm_service import LLMService
from app.services.menu_service import MenuService
from app.config import settings
from typing import Optional, Dict, Any
import os
from pathlib import Path

# Global services - initialized once in lifespan
llm_service: Optional[LLMService] = None
menu_service: Optional[MenuService] = None
conversation_manager: Optional[ConversationManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_service, menu_service, conversation_manager
    logger.info("🚀 Starting Restaurant AI Assistant...")

    try:
        # Initialize services
        llm_service = LLMService()
        logger.info(f"✅ LLM Service initialized with model: {llm_service.model}")

        menu_service = MenuService()
        items = await menu_service.get_all_items()
        logger.info(f"✅ Menu Service initialized with {len(items)} items")

        conversation_manager = ConversationManager(llm_service, menu_service)
        logger.info("✅ Conversation Manager initialized")

        logger.info("🎉 Restaurant AI Assistant started successfully!")
        
        # Test route registration - Fixed to handle different route types
        for route in app.routes:
            if isinstance(route, Route):
                logger.info(f"📍 Registered route: {route.methods} {route.path}")
            elif isinstance(route, Mount):
                logger.info(f"📁 Mounted path: {route.path} -> {route.name or 'static'}")
            else:
                logger.info(f"📍 Registered route: {type(route).__name__} {route.path}")
                
    except Exception as e:
        logger.error(f"❌ Failed to start services: {str(e)}", exc_info=True)
        raise

    yield

    logger.info("🛑 Shutting down Restaurant AI Assistant...")


# Initialize FastAPI app
app = FastAPI(
    title="Restaurant AI Assistant",
    description="An intelligent restaurant chatbot system that helps customers find the perfect meal",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Fixed for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://botappetite.netlify.app", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dependency functions
def get_conversation_manager():
    if conversation_manager is None:
        raise HTTPException(status_code=503, detail="Conversation Manager not initialized")
    return conversation_manager

def get_menu_service():
    if menu_service is None:
        raise HTTPException(status_code=503, detail="Menu Service not initialized")
    return menu_service

def get_llm_service():
    if llm_service is None:
        raise HTTPException(status_code=503, detail="LLM Service not initialized")
    return llm_service

# Include routers AFTER defining dependency functions
app.include_router(routes_chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(routes_meals.router, prefix="/api/meals", tags=["meals"])
app.include_router(routes_admin.router, prefix="/api/admin", tags=["admin"])

# Mount static files directory
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {
        "message": "Restaurant AI Assistant API is running",
        "status": "healthy",
        "endpoints": {
            "chat": "/api/chat",
            "meals": "/api/meals", 
            "admin": "/api/admin",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "llm": llm_service is not None,
            "menu": menu_service is not None,
            "conversation": conversation_manager is not None
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global exception handler for HTTP exceptions"""
    logger.error(f"HTTP error occurred: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "path": str(request.url.path)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all exceptions"""
    logger.error(f"Unexpected error: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "path": str(request.url.path)}
    )

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    logger.add("logs/app.log", rotation="1 day", retention="30 days")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
