from fastapi import APIRouter, HTTPException
from app.api.schemas import AskRequest, AskResponse
from app.services.llm_client import chat_completion
from app.services.retriever_cache import get_retriever

router = APIRouter()

SYSTEM_PROMPT = (
    "You are AviaGenAI, a focused T-6II aviation technical assistant. "
    "Answer based on the provided T-6II procedures and checklists. "
    "Be concise, accurate, and conservative. If unsure, say you are unsure."
)

@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        # Get relevant T-6II procedures
        retriever = get_retriever()
        relevant_docs = retriever.search(req.question, k=3)
        
        # Build context from retrieved documents
        context = ""
        if relevant_docs:
            context = "\n\n".join([
                f"**{doc['title']}**:\n{doc['chunk_text']}"
                for doc in relevant_docs
            ])
        
        # Create enhanced prompt with context
        if context:
            enhanced_prompt = f"""
{context}

Based on the above T-6II procedures, answer this question: {req.question}

Provide a clear, step-by-step answer based on the official procedures above.
"""
        else:
            enhanced_prompt = req.question
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": enhanced_prompt},
        ]
        
        answer = chat_completion(messages)
        if not answer:
            raise HTTPException(status_code=502, detail="Empty response from model.")
        
        return AskResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
