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
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    REQUEST_TEMPERATURE: float = float(os.getenv("REQUEST_TEMPERATURE", "0.2"))
    REQUEST_MAX_OUTPUT_TOKENS: int = int(os.getenv("REQUEST_MAX_OUTPUT_TOKENS", "600"))
    
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Weather Services
    METSERVICE_BASE_URL: str = os.getenv("METSERVICE_BASE_URL", "")
    METSERVICE_API_KEY: str = os.getenv("METSERVICE_API_KEY", "")
    METSERVICE_METAR_PATH: str = os.getenv("METSERVICE_METAR_PATH", "/aviation/metar")
    METSERVICE_TAF_PATH: str = os.getenv("METSERVICE_TAF_PATH", "/aviation/taf")
    
    # MET Norway fallback
    METNO_USER_AGENT: str = os.getenv("METNO_USER_AGENT", "AviaGenAI/0.1 (contact: you@example.com)")
    
    # Decision engine defaults (tune to your authority/corresponding AIP)
    VFR_MIN_VIS_KM: float = float(os.getenv("VFR_MIN_VIS_KM", "5"))
    VFR_MIN_CEILING_FT: int = int(os.getenv("VFR_MIN_CEILING_FT", "3000"))
    MVFR_MIN_VIS_KM: float = float(os.getenv("MVFR_MIN_VIS_KM", "5"))
    MVFR_MIN_CEILING_FT: int = int(os.getenv("MVFR_MIN_CEILING_FT", "1000"))
    T6_MAX_XWIND_KT: str = os.getenv("T6_MAX_XWIND_KT", "")  # Optional T-6 specific limit
    
    # Azure OpenAI (Alternative)
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01-preview")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

settings = Settings()
