from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from loguru import logger

from app.services.menu_service import MenuService
from app.services.llm_service import LLMService

router = APIRouter()

def get_menu_service():
    return MenuService()

def get_llm_service():
    return LLMService()

@router.get("/health")
async def admin_health_check():
    """Comprehensive health check for admin"""
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": None
    }
    
    try:
        # Check menu service
        menu_service = MenuService()
        menu_items = await menu_service.get_all_items()
        health_status["services"]["menu_service"] = {
            "status": "healthy",
            "menu_items_count": len(menu_items)
        }
    except Exception as e:
        health_status["services"]["menu_service"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    try:
        # Check LLM service
        llm_service = LLMService()
        test_response = await llm_service._generate_response("Hello, this is a health check.")
        health_status["services"]["llm_service"] = {
            "status": "healthy",
            "model": llm_service.model,
            "base_url": llm_service.base_url
        }
    except Exception as e:
        health_status["services"]["llm_service"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat()
    
    return health_status

@router.get("/stats")
async def get_system_stats(
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get system statistics"""
    try:
        stats = {
            "menu": {
                "total_items": len(await menu_service.get_all_items()),
                "categories": await menu_service.get_categories(),
                "cuisines": await menu_service.get_cuisine_types(),
                "dietary_tags": await menu_service.get_dietary_tags()
            }
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system stats")

@router.post("/test-llm")
async def test_llm_connection(
    test_message: str = "Hello, this is a test message.",
    llm_service: LLMService = Depends(get_llm_service)
):
    """Test LLM connection and response"""
    try:
        response = await llm_service._generate_response(test_message)
        return {
            "status": "success",
            "model": llm_service.model,
            "base_url": llm_service.base_url,
            "test_message": test_message,
            "llm_response": response
        }
    except Exception as e:
        logger.error(f"LLM test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM test failed: {str(e)}")

@router.get("/config")
async def get_configuration():
    """Get current system configuration (non-sensitive)"""
    from app.config import settings
    
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "model_name": settings.MODEL_NAME,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "max_recommendations": settings.MAX_RECOMMENDATIONS,
        "min_match_score": settings.MIN_MATCH_SCORE,
        "session_timeout_minutes": settings.SESSION_TIMEOUT_MINUTES
    }