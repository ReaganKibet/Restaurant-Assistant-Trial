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

        # Add user message to history
        session["messages"].append(
            ChatMessage(role="user", content=message)
        )

        # Process message with LLM
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
