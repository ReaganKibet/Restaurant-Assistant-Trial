import ollama
from app.config import settings

class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.MODEL_NAME

    async def generate_response(self, prompt: str) -> str:
        response = self.client.generate(model=self.model, prompt=prompt)
        return response['response']