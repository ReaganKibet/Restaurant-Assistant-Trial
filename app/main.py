# app/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.api import routes_chat, routes_meals, routes_admin
from app.core.conversation_manager import ConversationManager
from app.services.llm_service import LLMService
from app.services.menu_service import MenuService
from app.config import settings
from typing import Optional, Dict, Any
import os
from pathlib import Path

# Services to be initialized on startup
llm_service: LLMService = None
menu_service: MenuService = None
conversation_manager: ConversationManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_service, menu_service, conversation_manager
    logger.info("🚀 Starting Restaurant AI Assistant...")

    try:
        llm_service = LLMService()
        logger.info(f"✅ LLM Service initialized with model: {llm_service.model}")

        menu_service = MenuService()
        items = await menu_service.get_all_items()
        logger.info(f"✅ Menu Service initialized with {len(items)} items")

        conversation_manager = ConversationManager(llm_service, menu_service)
        logger.info("✅ Conversation Manager initialized")

        logger.info("🎉 Restaurant AI Assistant started successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to start services: {str(e)}")
        raise

    yield

    logger.info("🛑 Shutting down Restaurant AI Assistant...")


# Initialize FastAPI app with lifespan (single instance)
app = FastAPI(
    title="Restaurant AI Assistant",
    description="An intelligent restaurant chatbot system that helps customers find the perfect meal",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://botappetite.netlify.app"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(routes_chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(routes_meals.router, prefix="/api/meals", tags=["meals"])
app.include_router(routes_admin.router, prefix="/api/admin", tags=["admin"])

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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global exception handler for HTTP exceptions"""
    logger.error(f"HTTP error occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

# Dependency functions for routes
def get_conversation_manager():
    if conversation_manager is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return conversation_manager

def get_menu_service():
    if menu_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return menu_service

def get_llm_service():
    if llm_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return llm_service

@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting LLM Chat API")

@app.get("/health", response_model=dict)
async def health() -> dict:
    return {"status": "ok"}



if __name__ == "__main__":
    logger.add("logs/app.log", rotation="1 day", retention="30 days")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
