from fastapi import APIRouter, HTTPException
from app.api.schemas import AskRequest, AskResponse
from app.services.llm_client import chat_completion

router = APIRouter()

SYSTEM_PROMPT = (
    "You are AviaGenAI, a concise aviation technical assistant. "
    "Answer clearly and conservatively. If unsure, say you are unsure."
)

@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.question},
        ]
        answer = chat_completion(messages)
        if not answer:
            raise HTTPException(status_code=502, detail="Empty response from model.")
        return AskResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
