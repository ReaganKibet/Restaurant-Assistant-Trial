from typing import List, Dict, Any, Optional
import json
from loguru import logger
from datetime import datetime
import os

from app.config import settings
from app.models.schemas import MenuItem, MealCategory

# Add Supabase import
USE_SUPABASE = getattr(settings, "USE_SUPABASE", False)
if USE_SUPABASE:
    from supabase import create_client, Client
    SUPABASE_URL = settings.SUPABASE_URL
    SUPABASE_KEY = settings.SUPABASE_KEY
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class MenuService:
    def __init__(self):
        self.menu_data_path = settings.MENU_DATA_PATH
        self.allergens_data_path = settings.ALLERGENS_DATA_PATH
        self.ingredients_data_path = settings.INGREDIENTS_DATA_PATH

        # Load data based on config
        if USE_SUPABASE:
            self.menu_data = self._load_menu_data_supabase()
            self.allergens_data = self._load_allergens_data_supabase()
            self.ingredients_data = self._load_ingredients_data_supabase()
        else:
            self.menu_data = self._load_menu_data()
            self.allergens_data = self._load_allergens_data()
            self.ingredients_data = self._load_ingredients_data()

        self.menu_items = [MenuItem(**item) for item in self.menu_data.get("items", [])]

    def _load_menu_data(self) -> Dict[str, Any]:
        """Load menu data from JSON file"""
        try:
            with open(self.menu_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading menu data: {str(e)}")
            return {"items": []}

    def _load_allergens_data(self) -> Dict[str, Any]:
        """Load allergens data from JSON file"""
        try:
            with open(self.allergens_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading allergens data: {str(e)}")
            return {"allergens": []}

    def _load_ingredients_data(self) -> Dict[str, Any]:
        """Load ingredients data from JSON file"""
        try:
            with open(self.ingredients_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading ingredients data: {str(e)}")
            return {"ingredients": []}

    # Supabase loaders
    def _load_menu_data_supabase(self) -> Dict[str, Any]:
        """Load menu data from Supabase"""
        try:
            response = supabase.table("menu_items").select("*").execute()
            items = response.data if response.data else []
            return {"items": items}
        except Exception as e:
            logger.error(f"Error loading menu data from Supabase: {str(e)}")
            return {"items": []}

    def _load_allergens_data_supabase(self) -> Dict[str, Any]:
        """Load allergens data from Supabase"""
        try:
            response = supabase.table("allergens").select("*").execute()
            if response.data:
                return response.data[0]
            return {"allergens": []}
        except Exception as e:
            logger.error(f"Error loading allergens data from Supabase: {str(e)}")
            return {"allergens": []}

    def _load_ingredients_data_supabase(self) -> Dict[str, Any]:
        """Load ingredients data from Supabase"""
        try:
            response = supabase.table("ingredients").select("*").execute()
            if response.data:
                return response.data[0]
            return {"ingredients": []}
        except Exception as e:
            logger.error(f"Error loading ingredients data from Supabase: {str(e)}")
            return {"ingredients": []}

    def _create_sample_menu(self):
        """Create sample menu items for testing"""
        sample_items = [
            {
                "id": "1",
                "name": "Margherita Pizza",
                "description": "Classic pizza with fresh mozzarella, tomato sauce, and basil",
                "price": 14.99,
                "category": "Pizza",
                "cuisine_type": "Italian",
                "ingredients": ["mozzarella", "tomato sauce", "basil", "pizza dough"],
                "allergens": ["gluten", "dairy"],
                "dietary_tags": ["vegetarian"],
                "spice_level": 1,
                "preparation_time": 15,
                "popularity_score": 8.5,
                "available": True
            },
            {
                "id": "2",
                "name": "Chicken Tikka Masala",
                "description": "Tender chicken in creamy tomato-based curry with aromatic spices",
                "price": 18.99,
                "category": "Curry",
                "cuisine_type": "Indian",
                "ingredients": ["chicken", "tomatoes", "cream", "onions", "garlic", "ginger", "spices"],
                "allergens": ["dairy"],
                "dietary_tags": ["gluten-free"],
                "spice_level": 3,
                "preparation_time": 25,
                "popularity_score": 9.2,
                "available": True
            },
            {
                "id": "3",
                "name": "Caesar Salad",
                "description": "Crisp romaine lettuce with parmesan, croutons, and caesar dressing",
                "price": 12.99,
                "category": "Salad",
                "cuisine_type": "American",
                "ingredients": ["romaine lettuce", "parmesan cheese", "croutons", "caesar dressing"],
                "allergens": ["dairy", "eggs", "gluten"],
                "dietary_tags": ["vegetarian"],
                "spice_level": 0,
                "preparation_time": 10,
                "popularity_score": 7.8,
                "available": True
            }
        ]
        
        self.menu_items = [MenuItem(**item) for item in sample_items]
        logger.info(f"Created {len(self.menu_items)} sample menu items")

    def get_all_menu_items(self) -> List[MenuItem]:
        """Get all menu items"""
        return [MenuItem(**item) for item in self.menu_data.get("items", [])]

    def get_menu_items_by_category(self, category: MealCategory) -> List[MenuItem]:
        """Get menu items by category"""
        return [
            MenuItem(**item)
            for item in self.menu_data.get("items", [])
            if item["category"] == category
        ]

    def get_menu_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """Get a specific menu item by ID"""
        for item in self.menu_data.get("items", []):
            if item["id"] == item_id:
                return MenuItem(**item)
        return None

    def search_menu_items(
        self,
        query: str,
        category: Optional[MealCategory] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None
    ) -> List[MenuItem]:
        """Search menu items based on various criteria"""
        results = []
        query = query.lower()

        for item in self.menu_data.get("items", []):
            # Skip if category doesn't match
            if category and item["category"] != category:
                continue

            # Skip if price is outside range
            if max_price and item["price"] > max_price:
                continue
            if min_price and item["price"] < min_price:
                continue

            # Check if query matches name or description
            if (query in item["name"].lower() or
                query in item["description"].lower() or
                any(query in ing.lower() for ing in item["ingredients"])):
                results.append(MenuItem(**item))

        return results


    def _get_default_allergens(self) -> Dict[str, Any]:
        """Return default allergen information"""
        return {
            "common_allergens": [
                "dairy", "eggs", "fish", "shellfish", "tree nuts", 
                "peanuts", "wheat", "gluten", "soy", "sesame"
            ],
            "allergen_groups": {
                "dairy": ["milk", "cheese", "butter", "cream", "yogurt"],
                "gluten": ["wheat", "barley", "rye", "oats"],
                "nuts": ["almonds", "walnuts", "pecans", "cashews", "pistachios"]
            }
        }

    async def get_all_items(self) -> List[MenuItem]:
        """Get all menu items"""
        return [item for item in self.menu_items if item.available]

    async def get_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """Get a specific menu item by ID"""
        for item in self.menu_items:
            if item.id == item_id and item.available:
                return item
        return None

    async def search_items(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        cuisine_type: Optional[str] = None,
        dietary_tags: Optional[List[str]] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        max_spice_level: Optional[int] = None
    ) -> List[MenuItem]:
        """Search menu items based on various criteria"""
        results = []
        
        for item in self.menu_items:
            if not item.available:
                continue
                
            # Text search in name and description
            if query:
                query_lower = query.lower()
                if not (query_lower in item.name.lower() or 
                       query_lower in item.description.lower() or
                       any(query_lower in ingredient.lower() for ingredient in item.ingredients)):
                    continue
            
            # Category filter
            if category and item.category.lower() != category.lower():
                continue
                
            # Cuisine type filter
            if cuisine_type and item.cuisine_type.lower() != cuisine_type.lower():
                continue
                
            # Dietary tags filter
            if dietary_tags:
                if not any(tag.lower() in [dt.lower() for dt in item.dietary_tags] for tag in dietary_tags):
                    continue
            
            # Price range filter
            if max_price and item.price > max_price:
                continue
            if min_price and item.price < min_price:
                continue
                
            # Spice level filter
            if max_spice_level and item.spice_level > max_spice_level:
                continue
                
            results.append(item)
        
        # Sort by popularity score (descending)
        results.sort(key=lambda x: x.popularity_score, reverse=True)
        return results

    async def get_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set()
        for item in self.menu_items:
            if item.available:
                categories.add(item.category)
        return sorted(list(categories))

    async def get_cuisine_types(self) -> List[str]:
        """Get all available cuisine types"""
        cuisines = set()
        for item in self.menu_items:
            if item.available:
                cuisines.add(item.cuisine_type)
        return sorted(list(cuisines))

    async def get_dietary_tags(self) -> List[str]:
        """Get all available dietary tags"""
        tags = set()
        for item in self.menu_items:
            if item.available:
                tags.update(item.dietary_tags)
        return sorted(list(tags))

    def get_ingredients_info(self, ingredient_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an ingredient"""
        for ingredient in self.ingredients_data.get("ingredients", []):
            if ingredient["name"].lower() == ingredient_name.lower():
                return ingredient
        return None

    def get_allergen_info(self, allergen_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an allergen"""
        for allergen in self.allergens_data.get("allergens", []):
            if allergen["name"].lower() == allergen_name.lower():
                return allergen
        return None

    def get_common_allergens(self) -> List[str]:
        """Get list of common allergens"""
        return [a["name"] for a in self.allergens_data.get("allergens", [])]

    def get_popular_items(self, limit: int = 5) -> List[MenuItem]:
        """Get the most popular menu items"""
        items = self.menu_data.get("items", [])
        # Sort by popularity (assuming there's a 'popularity' field)
        sorted_items = sorted(
            items,
            key=lambda x: x.get("popularity", 0),
            reverse=True
        )
        return [MenuItem(**item) for item in sorted_items[:limit]]

    def get_special_items(self) -> List[MenuItem]:
        """Get items that are currently on special"""
        current_time = datetime.now()
        special_items = []

        for item in self.menu_data.get("items", []):
            if "special" in item:
                special = item["special"]
                if (special.get("is_active", False) and
                    current_time >= datetime.fromisoformat(special.get("start_time", "2000-01-01")) and
                    current_time <= datetime.fromisoformat(special.get("end_time", "2100-01-01"))):
                    special_items.append(MenuItem(**item))

        return special_items