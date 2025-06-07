import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Restaurant AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # LLM settings
    MODEL_NAME: str = "llama2"  # Default Ollama model
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # API settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Data paths
    MENU_DATA_PATH: str = "data/menu_data.json"
    ALLERGENS_DATA_PATH: str = "data/allergens.json"
    INGREDIENTS_DATA_PATH: str = "data/ingredients.json"
    
    # Session settings
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_ACTIVE_SESSIONS: int = 1000
    
    # Recommendation settings
    MAX_RECOMMENDATIONS: int = 5
    MIN_MATCH_SCORE: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()