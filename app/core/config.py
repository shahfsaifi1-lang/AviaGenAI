import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from a .env file at project root

class Settings:
    # OpenAI Direct API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Google AI Studio (Free tier available)
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    GOOGLE_AI_MODEL: str = os.getenv("GOOGLE_AI_MODEL", "gemini-2.0-flash")
    
    # LLM Client Settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")  # Alias for compatibility
    GEMINI_MODEL: str = os.getenv("GOOGLE_AI_MODEL", "gemini-2.0-flash")  # Alias for compatibility
    REQUEST_TEMPERATURE: float = float(os.getenv("REQUEST_TEMPERATURE", "0.7"))
    REQUEST_MAX_OUTPUT_TOKENS: int = int(os.getenv("REQUEST_MAX_OUTPUT_TOKENS", "1000"))
    
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Azure OpenAI (Alternative)
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01-preview")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

settings = Settings()
