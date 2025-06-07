from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.models.schemas import MenuItem
from app.services.menu_service import MenuService

class OfferEngine:
    def __init__(self, menu_service: MenuService):
        self.menu_service = menu_service
        self.current_offers: Dict[str, Dict[str, Any]] = {}

    def _is_valid_time(self, start_time: str, end_time: str) -> bool:
        """Check if current time is within offer validity period"""
        try:
            current = datetime.now()
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return start <= current <= end
        except Exception as e:
            logger.error(f"Error checking offer validity: {str(e)}")
            return False

    def _calculate_discount(
        self,
        original_price: float,
        discount_type: str,
        discount_value: float
    ) -> float:
        """Calculate discounted price based on discount type"""
        try:
            if discount_type == "percentage":
                return original_price * (1 - discount_value / 100)
            elif discount_type == "fixed":
                return max(0, original_price - discount_value)
            else:
                return original_price
        except Exception as e:
            logger.error(f"Error calculating discount: {str(e)}")
            return original_price

    async def get_current_offers(self) -> List[Dict[str, Any]]:
        """Get all currently active offers"""
        active_offers = []
        current_time = datetime.now()

        for offer_id, offer in self.current_offers.items():
            if self._is_valid_time(offer["start_time"], offer["end_time"]):
                active_offers.append({
                    "id": offer_id,
                    "name": offer["name"],
                    "description": offer["description"],
                    "discount_type": offer["discount_type"],
                    "discount_value": offer["discount_value"],
                    "applicable_items": offer["applicable_items"],
                    "valid_until": offer["end_time"]
                })

        return active_offers

    async def apply_offer(
        self,
        items: List[MenuItem],
        offer_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Apply available offers to a list of items"""
        if not offer_id:
            # Get all applicable offers
            offers = await self.get_current_offers()
        else:
            # Get specific offer
            if offer_id not in self.current_offers:
                return []
            offers = [self.current_offers[offer_id]]

        discounted_items = []
        for item in items:
            item_discounts = []
            original_price = item.price

            for offer in offers:
                # Check if item is eligible for offer
                if (item.id in offer["applicable_items"] or
                    offer["applicable_items"] == ["all"]):
                    
                    discounted_price = self._calculate_discount(
                        original_price,
                        offer["discount_type"],
                        offer["discount_value"]
                    )

                    item_discounts.append({
                        "offer_id": offer["id"],
                        "offer_name": offer["name"],
                        "original_price": original_price,
                        "discounted_price": discounted_price,
                        "savings": original_price - discounted_price
                    })

            if item_discounts:
                # Apply best discount
                best_discount = max(
                    item_discounts,
                    key=lambda x: x["savings"]
                )
                discounted_items.append({
                    "item": item,
                    "discount": best_discount
                })
            else:
                discounted_items.append({
                    "item": item,
                    "discount": None
                })

        return discounted_items

    async def create_offer(
        self,
        name: str,
        description: str,
        discount_type: str,
        discount_value: float,
        applicable_items: List[str],
        start_time: str,
        end_time: str
    ) -> Dict[str, Any]:
        """Create a new offer"""
        offer_id = f"offer_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        offer = {
            "id": offer_id,
            "name": name,
            "description": description,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "applicable_items": applicable_items,
            "start_time": start_time,
            "end_time": end_time,
            "created_at": datetime.now().isoformat()
        }

        self.current_offers[offer_id] = offer
        return offer

    async def get_combo_deals(
        self,
        items: List[MenuItem]
    ) -> List[Dict[str, Any]]:
        """Get available combo deals for selected items"""
        combo_deals = []
        
        # Example combo logic (can be expanded based on business rules)
        for item in items:
            # Check for drink + main course combos
            if item.category == "main_course":
                drinks = self.menu_service.get_menu_items_by_category("beverage")
                for drink in drinks:
                    combo_deals.append({
                        "name": f"{item.name} + {drink.name} Combo",
                        "items": [item, drink],
                        "original_price": item.price + drink.price,
                        "combo_price": (item.price + drink.price) * 0.9,  # 10% discount
                        "savings": (item.price + drink.price) * 0.1
                    })

            # Check for dessert + main course combos
            if item.category == "main_course":
                desserts = self.menu_service.get_menu_items_by_category("dessert")
                for dessert in desserts:
                    combo_deals.append({
                        "name": f"{item.name} + {dessert.name} Combo",
                        "items": [item, dessert],
                        "original_price": item.price + dessert.price,
                        "combo_price": (item.price + dessert.price) * 0.85,  # 15% discount
                        "savings": (item.price + dessert.price) * 0.15
                    })

        return combo_deals

    async def get_seasonal_specials(self) -> List[Dict[str, Any]]:
        """Get seasonal special offers"""
        current_month = datetime.now().month
        seasonal_offers = []

        # Example seasonal logic (can be expanded)
        if current_month in [12, 1, 2]:  # Winter
            seasonal_offers.append({
                "name": "Winter Warmers",
                "description": "Special winter menu items with hot beverages",
                "discount": "15% off on selected winter items",
                "valid_until": f"{datetime.now().year}-02-28"
            })
        elif current_month in [6, 7, 8]:  # Summer
            seasonal_offers.append({
                "name": "Summer Refreshments",
                "description": "Cool summer specials with iced drinks",
                "discount": "20% off on selected summer items",
                "valid_until": f"{datetime.now().year}-08-31"
            })

        return seasonal_offers

    async def get_loyalty_rewards(
        self,
        customer_id: str,
        total_spent: float
    ) -> Dict[str, Any]:
        """Calculate loyalty rewards for a customer"""
        # Example loyalty tiers (can be customized)
        tiers = {
            "bronze": {"threshold": 0, "discount": 5},
            "silver": {"threshold": 1000, "discount": 10},
            "gold": {"threshold": 5000, "discount": 15},
            "platinum": {"threshold": 10000, "discount": 20}
        }

        # Determine customer tier
        current_tier = "bronze"
        for tier, details in tiers.items():
            if total_spent >= details["threshold"]:
                current_tier = tier

        # Calculate next tier progress
        next_tier = None
        for tier, details in sorted(
            tiers.items(),
            key=lambda x: x[1]["threshold"]
        ):
            if details["threshold"] > total_spent:
                next_tier = {
                    "name": tier,
                    "threshold": details["threshold"],
                    "remaining": details["threshold"] - total_spent
                }
                break

        return {
            "customer_id": customer_id,
            "current_tier": current_tier,
            "total_spent": total_spent,
            "discount_percentage": tiers[current_tier]["discount"],
            "next_tier": next_tier
        }
