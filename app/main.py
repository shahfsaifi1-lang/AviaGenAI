from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AviaGenAI API is running ✅"}
