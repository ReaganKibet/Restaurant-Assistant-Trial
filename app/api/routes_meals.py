from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from loguru import logger

from app.models.schemas import (
    MenuItem, MealCategory, UserPreferences,
    MealRecommendation, OrderRequest, OrderResponse
)
from app.models.schemas import MenuItem
from app.services.menu_service import MenuService
from app.core.meal_selector import MealSelector
from app.core.allergy_checker import AllergyChecker
from app.core.offer_engine import OfferEngine

router = APIRouter()

# Dependency Providers
def get_menu_service() -> MenuService:
    return MenuService()

def get_meal_selector(menu_service: MenuService = Depends(get_menu_service)) -> MealSelector:
    return MealSelector(menu_service)

def get_allergy_checker() -> AllergyChecker:
    return AllergyChecker()

def get_offer_engine(menu_service: MenuService = Depends(get_menu_service)) -> OfferEngine:
    return OfferEngine(menu_service)

# Models
class SearchQuery(BaseModel):
    query: str
    category: Optional[MealCategory] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None

# Routes
@router.get("/menu", response_model=List[MenuItem])
async def get_menu(
    category: Optional[MealCategory] = None,
    cuisine: Optional[str] = Query(None, description="Filter by cuisine type"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    dietary_tags: Optional[List[str]] = Query(None, description="Dietary requirements"),
    max_spice: Optional[int] = Query(None, description="Maximum spice level (1-5)"),
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get all menu items, optionally filtered"""
    try:
        meals = await menu_service.search_items(
            category=category,
            cuisine_type=cuisine,
            max_price=max_price,
            min_price=min_price,
            dietary_tags=dietary_tags,
            max_spice_level=max_spice
        )
        return meals
    except Exception as e:
        logger.error(f"Error retrieving meals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve meals")

@router.get("/menu/{item_id}", response_model=MenuItem)
async def get_menu_item(
    item_id: str,
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get a specific menu item by ID"""
    try:
        item = await menu_service.get_item_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving menu item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve menu item")

@router.get("/menu/search", response_model=List[MenuItem])
async def search_menu(
    q: str = Query(..., description="Search query"),
    limit: Optional[int] = Query(10, description="Maximum number of results"),
    menu_service: MenuService = Depends(get_menu_service)
):
    """Search menu items by name, description, or ingredients"""
    try:
        meals = await menu_service.search_items(query=q)
        return meals[:limit] if limit else meals
    except Exception as e:
        logger.error(f"Error searching meals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search menu")

@router.post("/menu/recommend", response_model=List[MealRecommendation])
async def get_recommendations(
    preferences: UserPreferences,
    limit: int = Query(5, ge=1, le=10),
    meal_selector: MealSelector = Depends(get_meal_selector),
    allergy_checker: AllergyChecker = Depends(get_allergy_checker)
):
    """Get personalized meal recommendations"""
    try:
        recommendations = await meal_selector.get_recommendations(preferences, limit)
        if preferences.allergies:
            recommendations = await allergy_checker.filter_allergens(recommendations, preferences.allergies)
        return recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@router.get("/menu/{item_id}/similar", response_model=List[MenuItem])
async def get_similar_items(
    item_id: str,
    limit: int = Query(3, ge=1, le=10),
    meal_selector: MealSelector = Depends(get_meal_selector)
):
    """Get similar menu items based on a reference item"""
    try:
        similar_meals = await meal_selector.get_similar_items(item_id, limit)
        return similar_meals
    except Exception as e:
        logger.error(f"Error finding similar items: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find similar menu items")

@router.post("/menu/{item_id}/safety-check")
async def check_meal_safety(
    item_id: str,
    allergies: List[str],
    menu_service: MenuService = Depends(get_menu_service),
    allergy_checker: AllergyChecker = Depends(get_allergy_checker)
):
    """Check if a menu item is safe for someone with specific allergies"""
    try:
        meal = await menu_service.get_item_by_id(item_id)
        if not meal:
            raise HTTPException(status_code=404, detail="Menu item not found")
        safety_info = await allergy_checker.check_meal_safety(meal, allergies)
        return safety_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking menu item safety: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check menu item safety")

@router.get("/categories", response_model=List[str])
async def get_categories(
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get all available meal categories"""
    try:
        return await menu_service.get_categories()
    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")

@router.get("/cuisines", response_model=List[str])
async def get_cuisines(
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get all available cuisine types"""
    try:
        return await menu_service.get_cuisine_types()
    except Exception as e:
        logger.error(f"Error retrieving cuisines: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cuisines")

@router.get("/dietary-tags", response_model=List[str])
async def get_dietary_tags(
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get all available dietary tags"""
    try:
        return await menu_service.get_dietary_tags()
    except Exception as e:
        logger.error(f"Error retrieving dietary tags: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dietary tags")

@router.get("/offers", response_model=List[Dict])
async def get_current_offers(
    offer_engine: OfferEngine = Depends(get_offer_engine)
):
    """Get all current menu offers"""
    try:
        return await offer_engine.get_current_offers()
    except Exception as e:
        logger.error(f"Error retrieving offers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve offers")

@router.get("/", response_model=List[MenuItem])
async def list_meals(
    category: Optional[MealCategory] = None,
    cuisine: Optional[str] = Query(None, description="Filter by cuisine type"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    dietary_tags: Optional[List[str]] = Query(None, description="Dietary requirements"),
    max_spice: Optional[int] = Query(None, description="Maximum spice level (1-5)"),
    menu_service: MenuService = Depends(get_menu_service)
):
    """Get all menu items, optionally filtered"""
    try:
        meals = await menu_service.search_items(
            category=category,
            cuisine_type=cuisine,
            max_price=max_price,
            min_price=min_price,
            dietary_tags=dietary_tags,
            max_spice_level=max_spice
        )
        return meals
    except Exception as e:
        logger.error(f"Error retrieving meals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve meals")
