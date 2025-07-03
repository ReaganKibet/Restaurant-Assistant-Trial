from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class DietaryRestriction(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    HALAL = "halal"
    KOSHER = "kosher"

class MealCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    SIDE_DISH = "side_dish"

class UserPreferences(BaseModel):
    dietary_restrictions: List[DietaryRestriction] = []
    allergies: List[str] = []
    price_range: Optional[tuple[float, float]] = None
    favorite_cuisines: List[str] = []
    disliked_ingredients: List[str] = []
    spice_preference: Optional[int] = Field(None, ge=1, le=5)  # 1-5 scale
    preferred_meal_types: List[str] = Field(default_factory=list)  # breakfast, lunch, dinner
    dislikes: List[str] = Field(default_factory=list)


class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: MealCategory
    ingredients: List[str]
    allergens: List[str]
    nutritional_info: Dict[str, Any]
    preparation_time: int  # in minutes
    spice_level: int = Field(..., ge=0, le=5, description="Spice level from 0 (not spicy) to 5 (very spicy)")  # 1-5 scale
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    is_dairy_free: bool
    image_url: Optional[str] = None
    available: bool
    popularity_score: float = 0.0

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    suggested_meals: Optional[List[MenuItem]] = None
    follow_up_questions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MealRecommendation(BaseModel):
    meal: MenuItem
    confidence_score: float
    reasoning: str
    nutritional_info: Optional[Dict[str, Any]] = None
    alternatives: List[MenuItem]

class OrderRequest(BaseModel):
    meal_ids: List[str]
    special_instructions: Optional[str] = None
    table_number: Optional[int] = None

class OrderResponse(BaseModel):
    order_id: str
    status: str
    estimated_time: int  # in minutes
    total_price: float
    items: List[MenuItem]
    confirmation_message: str
    
class ConversationRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    preferences: Optional[UserPreferences] = None

class StartConversationRequest(BaseModel):
    preferences: Optional[UserPreferences] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str
    preferences: Dict[str, Any]
    context: Optional[List[Dict[str, Any]]] = None  # <-- Add this line if you need context