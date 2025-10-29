from fastapi import FastAPI
from app.api.routes.ask import router as ask_router
from app.api.routes.weather import router as weather_router

app = FastAPI(
    title="AviaGenAI",
    description="Aviation Technical Assistant with T-6II Knowledge Base and Weather Services",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "AviaGenAI API is running ✅",
        "features": [
            "T-6II Technical Assistant (RAG)",
            "Weather Services (METAR/TAF)",
            "Aviation Decision Support"
        ],
        "docs": "/docs"
    }

app.include_router(ask_router, prefix="/api", tags=["llm"])
app.include_router(weather_router, prefix="/api", tags=["weather"])
