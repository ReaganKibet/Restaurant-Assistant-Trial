from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from loguru import logger

from app.models.schemas import (
    ChatMessage, ChatResponse, UserPreferences,
    MenuItem, MealRecommendation
)
from app.services.llm_service import LLMService
from app.services.menu_service import MenuService
from app.core.meal_selector import MealSelector
from app.core.allergy_checker import AllergyChecker

class ConversationManager:
    def __init__(self, llm_service: LLMService, menu_service: MenuService):
        self.llm_service = llm_service
        self.menu_service = menu_service
        self.meal_selector = MealSelector(menu_service)
        self.allergy_checker = AllergyChecker()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    @property
    def sessions(self):
        # Expose sessions for logging/debugging
        return self.active_sessions

    async def _update_filtered_meals(self, session):
        preferences = session["preferences"]
        if preferences_are_sufficient(preferences):
            filtered_meals = await self.meal_selector.get_recommendations(preferences)
            if preferences.allergies:
                filtered_meals = await self.allergy_checker.filter_allergens(
                    meals=filtered_meals, allergies=preferences.allergies
                )
            session["filtered_meals"] = filtered_meals
        else:
            session["filtered_meals"] = []

    async def start_conversation(
        self,
        preferences: Optional[UserPreferences] = None
    ) -> ChatResponse:
        """Start a new conversation session"""
        session_id = str(uuid.uuid4())
        
        # Initialize session data
        self.active_sessions[session_id] = {
            "messages": [],
            "preferences": preferences or UserPreferences(),
            "start_time": datetime.utcnow()
        }

        session = self.active_sessions[session_id]
        await self._update_filtered_meals(session)
        if session["filtered_meals"]:
            meal = session["filtered_meals"][0].meal
            response_message = (
                f"I recommend the {meal.name}: {meal.description} (${meal.price}). "
                "Would you like to order this, add it to your order, or see more options? "
                "Just reply 'order' to confirm, or let me know if you want something else."
            )
            return ChatResponse(
                message=response_message,
                session_id=session_id,
                suggested_meals=session["filtered_meals"],
                follow_up_questions=["Would you like to order this meal, add a side, or see more options?"],
                metadata=None
            )

        # Generate welcome message
        welcome_message = await self.llm_service.generate_welcome_message(
            preferences=preferences
        )

        return ChatResponse(
            message=welcome_message,
            session_id=session_id,
            follow_up_questions=[
                "What type of cuisine are you in the mood for?",
                "Do you have any dietary restrictions?",
                "What's your preferred price range?"
            ]
        )

    async def process_message(
        self,
        message: str,
        session_id: str,
        preferences: Optional[UserPreferences] = None
    ) -> ChatResponse:
        """Process a user message and generate a response"""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session ID")

        session = self.active_sessions[session_id]
        
        # Update preferences if provided
        if preferences:
            session["preferences"] = preferences
            await self._update_filtered_meals(session)
        # Add user message to history
        session["messages"].append(
            ChatMessage(role="user", content=message)
        )

        # Recommend immediately if filtered meals exist
        if session.get("filtered_meals"):
            meal = session["filtered_meals"][0].meal
            response_message = (
                f"I recommend the {meal.name}: {meal.description} (${meal.price}). "
                "Would you like to order this, add it to your order, or see more options? "
                "Just reply 'order' to confirm, or let me know if you want something else."
            )
            return ChatResponse(
                message=response_message,
                session_id=session_id,
                suggested_meals=session["filtered_meals"],
                follow_up_questions=["Would you like to order this meal, add a side, or see more options?"],
                metadata=None
            )

        # --- OTHERWISE, USE LLM FOR NEXT STEP ---
        llm_response = await self.llm_service.process_message(
            message=message,
            context=session["messages"],
            preferences=session["preferences"]
        )

        # Get meal recommendations if appropriate
        suggested_meals = None
        if llm_response.get("should_recommend_meals", False):
            suggested_meals = await self.meal_selector.get_recommendations(
                preferences=session["preferences"],
                context=llm_response.get("context", {})
            )
            logger.info(f"LLM response: {llm_response}") 
        # Check for allergies if meals are suggested
        if suggested_meals:
            suggested_meals = await self.allergy_checker.filter_allergens(
                meals=suggested_meals,
                allergies=session["preferences"].allergies
            )

        # Generate follow-up questions
        follow_up_questions = await self.llm_service.generate_follow_up_questions(
            message=message,
            suggested_meals=suggested_meals,
            context=llm_response
        )

        # Create response
        response = ChatResponse(
            message=llm_response["message"],
            session_id=session_id,
            suggested_meals=suggested_meals,
            follow_up_questions=follow_up_questions,
            metadata=llm_response.get("metadata")
        )

        # Add assistant response to history
        session["messages"].append(
            ChatMessage(
                role="assistant",
                content=response.message,
                metadata=response.metadata
            )
        )

        return response

    async def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Retrieve chat history for a session"""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session ID")
        return self.active_sessions[session_id]["messages"]

    async def end_conversation(self, session_id: str) -> None:
        """End a conversation session and clean up"""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session ID")
        
        # Log conversation summary
        session = self.active_sessions[session_id]
        logger.info(
            f"Ending conversation session {session_id}",
            duration=datetime.utcnow() - session["start_time"],
            message_count=len(session["messages"])
        )
        
        # Remove session
        del self.active_sessions[session_id]

def preferences_are_sufficient(preferences: UserPreferences) -> bool:
    """
    Return True if three or more distinct preference categories are set.
    Categories: dietary_restrictions, favorite_cuisines, price_range, allergies, spice_preference, dislikes
    """
    count = 0
    if preferences.dietary_restrictions:
        count += 1
    if preferences.favorite_cuisines:
        count += 1
    if preferences.price_range and preferences.price_range[0] is not None and preferences.price_range[1] is not None:
        count += 1
    if preferences.allergies:
        count += 1
    if preferences.spice_preference is not None:
        count += 1
    if preferences.dislikes:
        count += 1
    return count >= 3

# Create service instances ONCE at module level
llm_service_instance = LLMService()
menu_service_instance = MenuService()
conversation_manager_instance = ConversationManager(
    llm_service=llm_service_instance,
    menu_service=menu_service_instance
)

def get_conversation_manager():
    return conversation_manager_instance
