from typing import List, Dict, Any, Optional
import json
from loguru import logger
import ollama
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.models.schemas import ChatMessage, UserPreferences

class LLMService:
    def __init__(self):
        self.model = settings.MODEL_NAME
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM with retry logic"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

    def _format_chat_history(self, messages: List[ChatMessage]) -> str:
        """Format chat history for the LLM prompt"""
        formatted_history = ""
        for msg in messages:
            role = "User" if msg.role == "user" else "Assistant"
            formatted_history += f"{role}: {msg.content}\n"
        return formatted_history

    def _format_preferences(self, preferences: Optional[UserPreferences]) -> str:
        """Format user preferences for the LLM prompt"""
        if not preferences:
            return "No specific preferences provided."
        
        pref_str = "User Preferences:\n"
        if preferences.dietary_restrictions:
            pref_str += f"- Dietary Restrictions: {', '.join(preferences.dietary_restrictions)}\n"
        if preferences.allergies:
            pref_str += f"- Allergies: {', '.join(preferences.allergies)}\n"
        if preferences.price_range:
            pref_str += f"- Price Range: ${preferences.price_range[0]} - ${preferences.price_range[1]}\n"
        if preferences.favorite_cuisines:
            pref_str += f"- Favorite Cuisines: {', '.join(preferences.favorite_cuisines)}\n"
        if preferences.spice_preference:
            pref_str += f"- Spice Preference: Level {preferences.spice_preference}/5\n"
        return pref_str

    async def generate_welcome_message(
        self,
        preferences: Optional[UserPreferences] = None
    ) -> str:
        """Generate a welcome message for new conversations"""
        prompt = f"""You are a friendly and knowledgeable restaurant AI assistant. 
Your goal is to help customers find the perfect meal based on their preferences and needs.

{self._format_preferences(preferences)}

Generate a warm welcome message that:
1. Introduces yourself as the restaurant's AI assistant
2. Acknowledges any provided preferences
3. Invites the customer to start their dining experience
4. Keeps the message concise and friendly

Response:"""

        return await self._generate_response(prompt)

    async def process_message(
        self,
        message: str,
        context: List[ChatMessage],
        preferences: Optional[UserPreferences] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate a response"""
        prompt = f"""You are a friendly and knowledgeable restaurant AI assistant.
Your goal is to help customers find the perfect meal based on their preferences and needs.

{self._format_preferences(preferences)}

Previous conversation:
{self._format_chat_history(context)}

User's latest message: {message}

Generate a response that:
1. Addresses the user's message directly
2. Maintains a friendly and helpful tone
3. Provides relevant information about menu items if appropriate
4. Asks follow-up questions to better understand their needs

Format your response as a JSON object with the following structure:
{{
    "message": "Your response message",
    "should_recommend_meals": true/false,
    "context": {{
        "intent": "user's intent (e.g., 'meal_recommendation', 'menu_inquiry', 'general_question')",
        "key_preferences": ["list", "of", "key", "preferences", "mentioned"]
    }},
    "metadata": {{
        "any": "additional metadata"
    }}
}}

Response:"""

        response = await self._generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {response}")
            return {
                "message": "I apologize, but I'm having trouble processing your request. Could you please rephrase it?",
                "should_recommend_meals": False,
                "context": {"intent": "error", "key_preferences": []},
                "metadata": {}
            }

    async def generate_follow_up_questions(
        self,
        message: str,
        suggested_meals: Optional[List[Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate relevant follow-up questions based on the conversation context"""
        prompt = f"""You are a restaurant AI assistant generating follow-up questions.

User's message: {message}

Context: {json.dumps(context) if context else 'No context provided'}

Suggested meals: {json.dumps(suggested_meals) if suggested_meals else 'No meals suggested'}

Generate 2-3 relevant follow-up questions that will help:
1. Better understand the user's preferences
2. Narrow down meal recommendations
3. Address any unclear aspects of their request

Format your response as a JSON array of strings.

Response:"""

        response = await self._generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse follow-up questions as JSON: {response}")
            return [
                "What type of cuisine are you interested in?",
                "Do you have any dietary restrictions?",
                "What's your preferred price range?"
            ] 