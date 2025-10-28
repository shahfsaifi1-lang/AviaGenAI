from fastapi import FastAPI
from app.api.routes.ask import router as ask_router

app = FastAPI(title="AviaGenAI")

@app.get("/")
def root():
    return {"message": "AviaGenAI API is running ✅"}

app.include_router(ask_router, prefix="/api", tags=["llm"])
