import ollama
from typing import Optional
from app.config import settings
from loguru import logger

class OllamaService:
    def __init__(self):
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        
    async def generate(self, prompt: str, context: Optional[str] = None) -> str:
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = await self.client.generate(
                model=settings.OLLAMA_BASE_URL,
                prompt=full_prompt,
                options={
                    'temperature': 0.7,
                    'num_predict': 1000,
                }
            )
            
            return response['response']
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise