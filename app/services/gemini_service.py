import google.generativeai as genai
from typing import Optional
from ..core.config import settings
from loguru import logger

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
    async def generate(self, prompt: str, context: Optional[str] = None) -> str:
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise