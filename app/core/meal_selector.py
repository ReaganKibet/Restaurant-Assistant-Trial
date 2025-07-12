from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger

from app.models.schemas import MenuItem, UserPreferences, MealRecommendation
from app.services.menu_service import MenuService

class MealSelector:
    def __init__(self, menu_service: MenuService):
        self.menu_service = menu_service

    def _matches_allergies(self, item: MenuItem, allergies: List[str]) -> bool:
        # Return True if item contains any of the user's allergies
        return any(allergen in item.allergens for allergen in allergies)

    def _calculate_preference_score(
        self,
        item: MenuItem,
        preferences: UserPreferences
    ) -> float:
        score = 0.0
        max_score = 0.0

        # Dietary restrictions (30%)
        if preferences.dietary_restrictions:
            dietary_score = 0.0
            for restriction in preferences.dietary_restrictions:
                if restriction == "vegetarian" and item.is_vegetarian:
                    dietary_score += 1
                elif restriction == "vegan" and item.is_vegan:
                    dietary_score += 1
                elif restriction == "gluten_free" and item.is_gluten_free:
                    dietary_score += 1
                elif restriction == "dairy_free" and item.is_dairy_free:
                    dietary_score += 1
            score += (dietary_score / len(preferences.dietary_restrictions)) * 0.3
            max_score += 0.3

        # Price range (25%)
        if preferences.price_range:
            min_price, max_price = preferences.price_range
            if min_price <= item.price <= max_price:
                score += 0.25
            max_score += 0.25

        # Cuisine type (20%)
        if preferences.favorite_cuisines:
            if item.cuisine_type.value in [c.lower() for c in preferences.favorite_cuisines]:
                score += 0.2
            max_score += 0.2

        # Spice level (15%)
        if preferences.spice_preference is not None:
            spice_diff = abs(item.spice_level - preferences.spice_preference)
            spice_score = max(0, 1 - (spice_diff / 5))
            score += spice_score * 0.15
            max_score += 0.15

        # Allergies (exclude if any match)
        if preferences.allergies and self._matches_allergies(item, preferences.allergies):
            return 0.0  # Exclude this meal

        return score / max_score if max_score > 0 else 0

    def _generate_recommendation_reasons(
        self,
        item: MenuItem,
        preferences: UserPreferences,
        score: float
    ) -> List[str]:
        """Generate human-readable reasons for the recommendation"""
        reasons = []

         # High match score
        if score > 0.8:
            reasons.append("Excellent match for your preferences")
        elif score > 0.6:
            reasons.append("Good match for your preferences")

        # Cuisine preference
        if preferences.favorite_cuisines:
            for cuisine in preferences.favorite_cuisines:
                if cuisine.lower() in item.cuisine_type.lower():
                    reasons.append(f"Matches your preference for {cuisine} cuisine")  

            
        # Price range
        if preferences.price_range:
            min_price, max_price = preferences.price_range
            if min_price <= item.price <= max_price:
                reasons.append(f"fits your budget of ${min_price}-${max_price}")

        # Dietary restrictions
        if preferences.dietary_restrictions:
            matching_restrictions = []
            for restriction in preferences.dietary_restrictions:
                if (restriction == "vegetarian" and item.is_vegetarian or
                    restriction == "vegan" and item.is_vegan or
                    restriction == "gluten_free" and item.is_gluten_free or
                    restriction == "dairy_free" and item.is_dairy_free):
                    matching_restrictions.append(restriction.replace("_", " "))
            if matching_restrictions:
                reasons.append(f"meets your {', '.join(matching_restrictions)} requirements")

        # Spice level
        if preferences.spice_preference:
            if abs(item.spice_level - preferences.spice_preference) <= 1:
                reasons.append(f"matches your preferred spice level")

        # Combine reasons
        if reasons:
            return f"This {item.name} is recommended because it {', '.join(reasons)}."
        return f"This {item.name} is a good match for your preferences."
    
      # If no specific reasons, add general ones
        if not reasons:
            reasons.append("Recommended based on your preferences")

        return reasons[:3]  # Limit to top 3 reasons

    async def get_recommendations(
        self,
        preferences: UserPreferences,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 3
    ) -> List[MealRecommendation]:
        """Get personalized meal recommendations based on user preferences"""
        try:
            # Get all menu items
            all_items = self.menu_service.get_all_menu_items()

            # Calculate scores for each item
            scored_items = []
            for item in all_items:
                score = self._calculate_preference_score(item, preferences)
                scored_items.append((item, score))

            # Sort by score
            scored_items.sort(key=lambda x: x[1], reverse=True)

            # Generate recommendations
            recommendations = []
            for item, score in scored_items[:limit]:
                # Get alternatives (next best items)
                alternatives = [
                    alt_item if isinstance(alt_item, MenuItem) else MenuItem(**alt_item)
                    for alt_item, alt_score in scored_items[limit:limit+2]
                ]

                recommendation = MealRecommendation(
                    meal=item,
                    confidence_score=score,
                    reasoning=self._generate_recommendation_reasons(
                        item, preferences, score
                    ),
                    alternatives=alternatives
                )
                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating meal recommendations: {str(e)}")
            return []

    async def get_similar_items(
        self,
        item: MenuItem,
        limit: int = 3
    ) -> List[MenuItem]:
        """Get similar items based on a reference item"""
        try:
            all_items = self.menu_service.get_all_menu_items()
            similar_items = []

            for other_item in all_items:
                if other_item.id == item.id:
                    continue

                # Calculate similarity score
                score = 0.0
                max_score = 0.0

                # Category matching (30% weight)
                if other_item.category == item.category:
                    score += 0.3
                max_score += 0.3

                # Price similarity (20% weight)
                price_diff = abs(other_item.price - item.price)
                price_score = max(0, 1 - (price_diff / max(item.price, other_item.price)))
                score += price_score * 0.2
                max_score += 0.2

                # Ingredient overlap (30% weight)
                common_ingredients = set(i.lower() for i in other_item.ingredients) & \
                                   set(i.lower() for i in item.ingredients)
                ingredient_score = len(common_ingredients) / \
                                 max(len(other_item.ingredients), len(item.ingredients))
                score += ingredient_score * 0.3
                max_score += 0.3

                # Spice level similarity (20% weight)
                spice_diff = abs(other_item.spice_level - item.spice_level)
                spice_score = max(0, 1 - (spice_diff / 5))
                score += spice_score * 0.2
                max_score += 0.2

                # Normalize score
                final_score = score / max_score if max_score > 0 else 0
                similar_items.append((other_item, final_score))

            # Sort by similarity score
            similar_items.sort(key=lambda x: x[1], reverse=True)
            return [item for item, _ in similar_items[:limit]]

        except Exception as e:
            logger.error(f"Error finding similar items: {str(e)}")
            return []
