from typing import List, Dict, Any, Optional
from loguru import logger

from app.models.schemas import MenuItem
from app.services.menu_service import MenuService

class AllergyChecker:
    def __init__(self):
        self.allergen_severity_levels = {
            "high": ["peanuts", "tree nuts", "shellfish", "fish"],
            "medium": ["milk", "eggs", "soy", "wheat"],
            "low": ["sesame", "sulfites", "celery", "mustard"]
        }

        self.allergen_synonyms = {
            'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'lactose'],
            'gluten': ['wheat', 'barley', 'rye', 'oats', 'flour'],
            'nuts': ['tree nuts', 'almonds', 'walnuts', 'pecans', 'cashews', 'pistachios'],
            'peanuts': ['groundnuts'],
            'shellfish': ['crab', 'lobster', 'shrimp', 'prawns', 'mussels', 'clams'],
            'fish': ['salmon', 'tuna', 'cod', 'mackerel'],
            'eggs': ['egg', 'albumen'],
            'soy': ['soya', 'soybeans', 'tofu', 'tempeh'],
            'sesame': ['sesame seeds', 'tahini']
        }

    def _get_allergen_severity(self, allergen: str) -> str:
        """Get the severity level of an allergen"""
        allergen = allergen.lower()
        for severity, allergens in self.allergen_severity_levels.items():
            if allergen in allergens:
                return severity
        return "unknown"

    def _check_ingredient_allergens(
        self,
        ingredient: str,
        allergies: List[str]
    ) -> List[Dict[str, Any]]:
        """Check if an ingredient contains any allergens"""
        found_allergens = []
        ingredient = ingredient.lower()

        for allergy in allergies:
            allergy_norm = allergy.lower()
            ingredient_norm = ingredient.lower()
            # Check for direct match
            if allergy_norm in ingredient_norm:
                found_allergens.append({
                    "allergen": allergy_norm,
                    "severity": self._get_allergen_severity(allergy_norm),
                    "match_type": "direct"
                })
                continue

            # Synonym match
            synonyms = self.allergen_synonyms.get(allergy_norm, [])
            for synonym in synonyms:
                if synonym in ingredient_norm:
                    found_allergens.append({
                        "allergen": allergy_norm,
                        "severity": self._get_allergen_severity(allergy_norm),
                        "match_type": "synonym"
                    })
                    break

            # Variation match
            for variation in self._get_allergen_variations(allergy_norm):
                if variation in ingredient_norm:
                    found_allergens.append({
                        "allergen": allergy_norm,
                        "severity": self._get_allergen_severity(allergy_norm),
                        "match_type": "variation"
                    })
                    break

        return found_allergens

    def _get_allergen_variations(self, allergen: str) -> List[str]:
        """Get common variations of allergen names"""
        variations = {
            "peanuts": ["peanut", "arachis", "groundnut"],
            "tree nuts": ["almond", "cashew", "walnut", "pecan", "hazelnut", "brazil nut"],
            "shellfish": ["shrimp", "crab", "lobster", "prawn", "crayfish"],
            "fish": ["salmon", "tuna", "cod", "halibut", "anchovy"],
            "milk": ["dairy", "lactose", "whey", "casein"],
            "eggs": ["egg", "albumin", "ovalbumin"],
            "soy": ["soya", "soybean", "edamame"],
            "wheat": ["gluten", "flour", "semolina"],
            "sesame": ["sesame seed", "tahini"],
            "sulfites": ["sulphite", "sulfite", "sulphur dioxide"],
            "celery": ["celery seed", "celery salt"],
            "mustard": ["mustard seed", "mustard powder"]
        }
        return variations.get(allergen.lower(), [])

    async def filter_allergens(
        self,
        meals: List[MenuItem],
        allergies: List[str]
    ) -> List[MenuItem]:
        """Filter out meals that contain allergens"""
        if not allergies:
            return meals

        safe_meals = []
        for meal in meals:
            is_safe = True
            allergen_warnings = []

            # Check each ingredient
            for ingredient in meal.ingredients:
                found_allergens = self._check_ingredient_allergens(
                    ingredient,
                    allergies
                )
                if found_allergens:
                    is_safe = False
                    allergen_warnings.extend(found_allergens)

            if is_safe:
                safe_meals.append(meal)
            else:
                logger.warning(
                    f"Meal {meal.name} contains allergens: {allergen_warnings}"
                )

        return safe_meals

    async def get_allergen_warnings(
        self,
        meal: MenuItem,
        allergies: List[str]
    ) -> List[Dict[str, Any]]:
        """Get detailed allergen warnings for a meal"""
        warnings = []
        
        for ingredient in meal.ingredients:
            found_allergens = self._check_ingredient_allergens(
                ingredient,
                allergies
            )
            if found_allergens:
                for allergen in found_allergens:
                    warnings.append({
                        "allergen": allergen["allergen"],
                        "severity": allergen["severity"],
                        "ingredient": ingredient,
                        "match_type": allergen["match_type"]
                    })

        return warnings

    async def get_safe_alternatives(
        self,
        meal: MenuItem,
        allergies: List[str],
        menu_service: MenuService
    ) -> List[MenuItem]:
        """Get safe alternative meals that don't contain the allergens"""
        all_meals = menu_service.get_all_menu_items()
        safe_alternatives = []

        for alternative in all_meals:
            if alternative.id == meal.id:
                continue

            # Check if alternative is safe
            warnings = await self.get_allergen_warnings(alternative, allergies)
            if not warnings:
                safe_alternatives.append(alternative)

        return safe_alternatives

    async def get_allergen_info(
        self,
        allergen: str,
        menu_service: MenuService
    ) -> Dict[str, Any]:
        """Get detailed information about an allergen"""
        allergen_info = menu_service.get_allergen_info(allergen)
        if not allergen_info:
            return {
                "name": allergen,
                "severity": self._get_allergen_severity(allergen),
                "description": "No detailed information available",
                "common_sources": [],
                "cross_reactors": []
            }

        return {
            "name": allergen_info["name"],
            "severity": allergen_info.get("severity", self._get_allergen_severity(allergen)),
            "description": allergen_info.get("description", ""),
            "common_sources": allergen_info.get("common_sources", []),
            "cross_reactors": allergen_info.get("cross_reactors", [])
        }
