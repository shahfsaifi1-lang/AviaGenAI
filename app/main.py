from fastapi import FastAPI
from app.api.routes.ask import router as ask_router
from app.api.routes.weather import router as weather_router
from app.api.routes.weather_simple import router as weather_simple_router
from app.api.routes.briefing import router as briefing_router

app = FastAPI(
    title="AviaGenAI",
    description="Aviation Technical Assistant with T-6II Knowledge Base, Weather Services, and Pre-Flight Briefing System",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "AviaGenAI API is running ✅",
        "features": [
            "T-6II Technical Assistant (RAG)",
            "Weather Services (METAR/TAF)",
            "Pre-Flight Briefing System",
            "Aviation Decision Support"
        ],
        "docs": "/docs"
    }

app.include_router(ask_router, prefix="/api", tags=["llm"])
app.include_router(weather_router, prefix="/api", tags=["weather"])
app.include_router(weather_simple_router, prefix="/api", tags=["weather-simple"])
app.include_router(briefing_router, prefix="/api", tags=["briefing"])
