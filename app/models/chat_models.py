from pydantic import BaseModel
from typing import Optional, Literal

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    use_fallback: bool = True
    preferred_provider: Optional[Literal["gemini", "ollama"]] = None

class ChatResponse(BaseModel):
    response: str
    provider: str
    success: bool
    fallback_used: bool = False
    processing_time: Optional[float] = None