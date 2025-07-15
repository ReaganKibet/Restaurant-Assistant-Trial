import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List, Optional

# Decide which .env file to load
env = os.getenv("ENV", "local")
env_file = ".env.production" if env == "production" else ".env.local"
load_dotenv(env_file)

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Restaurant AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Primary LLM - Gemini API Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    gemini_model: str = "gemini-1.5-flash"
    
    # Fallback LLM - Ollama Configuration
    MODEL_NAME: str = "llama2"  # For backward compatibility
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # LLM Fallback Strategy Settings
    use_ollama_fallback: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    fallback_threshold_errors: int = 2  # Switch to fallback after N consecutive errors
    
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
    
    # LLM Performance Settings
    max_tokens: Optional[int] = 1000
    temperature: float = 0.7
    
    # Health Check Settings
    health_check_interval_minutes: int = 5
    gemini_health_endpoint: Optional[str] = None
    
    # Retry Settings (for tenacity)
    retry_attempts: int = 3
    retry_min_wait: int = 4
    retry_max_wait: int = 10
    
    class Config:
        env_file = ".env"
        extra = "allow"

# Create global settings instance
settings = Settings()