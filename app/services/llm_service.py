from typing import List, Dict, Any, Optional
import json
import asyncio
import time
import re
import os
from enum import Enum
from dataclasses import dataclass
from loguru import logger
import ollama
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.models.schemas import ChatMessage, UserPreferences
from app.services.gemini_service import clean_llm_json

class LLMProvider(Enum):
    GEMINI = "gemini"
    OLLAMA = "ollama"

@dataclass
class LLMResponse:
    content: str
    provider: LLMProvider
    response_time: float
    success: bool = True
    fallback_used: bool = False
    tokens_used: Optional[int] = None

class LLMService:
    def __init__(self):
        # Initialize Gemini and Ollama clients here
        self.gemini_service = None
        self.ollama_service = None
        self._init_services()
        
        # Fallback tracking
        self.consecutive_errors = 0
        self.current_provider = LLMProvider.GEMINI
        self.last_health_check = 0
        self.gemini_healthy = True
        self.ollama_healthy = True
        
        # Ollama client for direct usage
        self.ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.MODEL_NAME

        # Load menu data once at startup
        menu_path = os.path.join(os.path.dirname(__file__), '../../data/menu_data.json')
        with open(menu_path, 'r', encoding='utf-8') as f:
            self.menu_data = json.load(f)["items"]

    def _init_services(self):
        """Initialize Gemini and Ollama services"""
        try:
            from .gemini_service import GeminiService
            self.gemini_service = GeminiService()
            logger.info("Gemini service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini service: {e}")
            
        try:
            from .ollama_service import OllamaService
            self.ollama_service = OllamaService()
            logger.info("Ollama service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama service: {e}")

    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Generate response using Gemini as primary, Ollama as fallback
        """
        start_time = time.time()
        
        # Check if we should use fallback due to consecutive errors
        if (self.consecutive_errors >= settings.fallback_threshold_errors and 
            settings.use_ollama_fallback):
            self.current_provider = LLMProvider.OLLAMA
            
        # Try primary provider first (unless we're in fallback mode)
        if self.current_provider == LLMProvider.GEMINI and self.gemini_service:
            try:
                logger.info("Attempting Gemini API call")
                response = await self.gemini_service.generate(prompt, context)
                self.consecutive_errors = 0  # Reset error counter on success
                return {
                    "response": response,
                    "provider": "gemini",
                    "success": True,
                    "response_time": time.time() - start_time
                }
                
            except Exception as gemini_error:
                logger.warning(f"Gemini failed: {gemini_error}")
                self.consecutive_errors += 1
                
                # Try fallback if enabled
                if use_fallback and settings.use_ollama_fallback and self.ollama_service:
                    try:
                        logger.info("Falling back to Ollama")
                        response = await self.ollama_service.generate(prompt, context)
                        return {
                            "response": response,
                            "provider": "ollama",
                            "success": True,
                            "fallback_used": True,
                            "response_time": time.time() - start_time
                        }
                    except Exception as ollama_error:
                        logger.error(f"Both providers failed. Ollama: {ollama_error}")
                        raise Exception("All LLM providers failed")
                else:
                    raise gemini_error
        else:
            # We're in fallback mode or Gemini not available, try Ollama first
            if self.ollama_service:
                try:
                    response = await self.ollama_service.generate(prompt, context)
                    return {
                        "response": response,
                        "provider": "ollama",
                        "success": True,
                        "response_time": time.time() - start_time
                    }
                except Exception as ollama_error:
                    logger.warning(f"Ollama failed: {ollama_error}")
                    # Try Gemini as backup if available
                    if self.gemini_service:
                        try:
                            response = await self.gemini_service.generate(prompt, context)
                            self.consecutive_errors = 0  # Reset if Gemini works
                            self.current_provider = LLMProvider.GEMINI  # Switch back
                            return {
                                "response": response,
                                "provider": "gemini",
                                "success": True,
                                "response_time": time.time() - start_time
                            }
                        except Exception as gemini_error:
                            raise Exception(f"Both LLM providers failed. Ollama: {ollama_error}, Gemini: {gemini_error}")
                    else:
                        raise ollama_error
            else:
                raise Exception("No LLM providers available")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_ollama_response(self, prompt: str) -> str:
        """Generate a response from Ollama with retry logic"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error generating Ollama response: {str(e)}")
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

    def _format_menu_for_prompt(self) -> str:
        """Format menu items for LLM prompt"""
        menu_lines = []
        for item in self.menu_data:
            menu_lines.append(
                f"- {item.get('name', '')}: {item.get('description', '')} "
                f"(Cuisine: {item.get('cuisine_type', '')}, Price: ${item.get('price', '')}, "
                f"Dietary: {', '.join(item.get('dietary_tags', []))}, Allergens: {', '.join(item.get('allergens', []))})"
            )
        return "\n".join(menu_lines)

    async def generate_welcome_message(
        self,
        preferences: Optional[UserPreferences] = None
    ) -> str:
        """Generate a welcome message for new conversations"""
        prompt = f"""You are a friendly and knowledgeable restaurant AI assistant for {settings.APP_NAME}. 
Your goal is to help customers find the perfect meal based on their preferences and needs.

{self._format_preferences(preferences)}

Generate a warm welcome message that:
1. Introduces yourself as the restaurant's AI assistant
2. Acknowledges any provided preferences
3. Invites the customer to start their dining experience
4. Keeps the message concise and friendly

Response:"""

        try:
            result = await self.generate_response(prompt)
            return result["response"]
        except Exception as e:
            logger.error(f"Error generating welcome message: {e}")
            return f"Welcome to {settings.APP_NAME}! I'm your AI assistant, ready to help you find the perfect meal. How can I assist you today?"

    async def process_message(
        self,
        message: str,
        context: List[ChatMessage],
        preferences: Optional[UserPreferences] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate a response"""
        menu_text = self._format_menu_for_prompt()
        prompt = f"""You are a friendly and knowledgeable restaurant AI assistant for {settings.APP_NAME}.
Your goal is to help customers find the perfect meal based on their preferences and needs.

ONLY recommend meals from the menu below. Use the menu properties (ingredients, allergens, dietary tags, nutrition, etc.) to answer questions and explain suitability for health conditions (e.g., ulcers, allergies). Do NOT invent new dishes.

Menu:
{menu_text}

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
        "provider_used": "gemini or ollama",
        "response_time": "response time in seconds"
    }}
}}

Response:"""

        try:
            result = await self.generate_response(prompt)
            response_text = result["response"]
            # Clean the LLM response before parsing
            response_text = clean_llm_json(response_text)
            try:
                parsed_response = json.loads(response_text)
                # Add provider metadata
                parsed_response["metadata"] = parsed_response.get("metadata", {})
                parsed_response["metadata"]["provider_used"] = result["provider"]
                parsed_response["metadata"]["response_time"] = result.get("response_time", 0)
                parsed_response["metadata"]["fallback_used"] = result.get("fallback_used", False)
                
                return parsed_response
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {response_text}")
                return {
                    "message": "I apologize, but I'm having trouble processing your request. Could you please rephrase it?",
                    "should_recommend_meals": False,
                    "context": {"intent": "error", "key_preferences": []},
                    "metadata": {
                        "provider_used": result["provider"],
                        "response_time": result.get("response_time", 0),
                        "fallback_used": result.get("fallback_used", False),
                        "error": "json_parse_error"
                    }
                }
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "message": "I'm sorry, I'm experiencing technical difficulties. Please try again in a moment.",
                "should_recommend_meals": False,
                "context": {"intent": "error", "key_preferences": []},
                "metadata": {"error": str(e)}
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

        try:
            result = await self.generate_response(prompt)
            response_text = result["response"]
            # Clean the LLM response before parsing
            response_text = clean_llm_json(response_text)
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse follow-up questions as JSON: {response_text}")
                return [
                    "What type of cuisine are you interested in?",
                    "Do you have any dietary restrictions?",
                    "What's your preferred price range?"
                ]
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            return [
                "What type of cuisine are you interested in?",
                "Do you have any dietary restrictions or allergies?",
                "Are you looking for something light or a full meal?"
            ]

    async def health_check(self) -> Dict[str, bool]:
        """Check health of both LLM providers"""
        current_time = time.time()
        
        # Only run health check every N minutes
        if current_time - self.last_health_check < (settings.health_check_interval_minutes * 60):
            return {"gemini": self.gemini_healthy, "ollama": self.ollama_healthy}
        
        self.last_health_check = current_time
        
        # Test Gemini
        if self.gemini_service:
            try:
                await self.gemini_service.generate("Health check", None)
                self.gemini_healthy = True
            except Exception:
                self.gemini_healthy = False
                logger.warning("Gemini health check failed")
        
        # Test Ollama
        if self.ollama_service:
            try:
                await self.ollama_service.generate("Health check", None)
                self.ollama_healthy = True
            except Exception:
                self.ollama_healthy = False
                logger.warning("Ollama health check failed")
        
        return {"gemini": self.gemini_healthy, "ollama": self.ollama_healthy}

    def get_current_provider(self) -> LLMProvider:
        """Get currently active provider"""
        return self.current_provider
        
    def reset_error_count(self):
        """Reset consecutive error count"""
        self.consecutive_errors = 0
        self.current_provider = LLMProvider.GEMINI

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about provider usage"""
        return {
            "current_provider": self.current_provider.value,
            "consecutive_errors": self.consecutive_errors,
            "gemini_healthy": self.gemini_healthy,
            "ollama_healthy": self.ollama_healthy,
            "last_health_check": self.last_health_check
        }

    def clean_llm_json(text: str) -> str:
        # Remove code block markers and language tags
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)