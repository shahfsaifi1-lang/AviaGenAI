from typing import List, Dict
import google.generativeai as genai
from app.core.config import settings

# Configure the Gemini client with API key from .env
if not settings.GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing. Set it in your .env file.")
genai.configure(api_key=settings.GOOGLE_API_KEY)

def chat_completion(messages: List[Dict[str, str]]) -> str:
    """
    Very small wrapper to call Gemini with a system+user message list.
    Expects messages like:
    [{"role":"system","content":"..."}, {"role":"user","content":"..."}]
    Returns the text output.
    """
    # Build a single prompt string from messages
    system = "\n".join(m["content"] for m in messages if m["role"] == "system")
    user = "\n".join(m["content"] for m in messages if m["role"] == "user")

    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    # Gemini prefers "generate_content" with one or more parts
    # We pass system instruction and user content together.
    prompt = f"{system}\n\nUser:\n{user}"

    resp = model.generate_content(
        prompt,
        generation_config={
            "temperature": settings.REQUEST_TEMPERATURE,
            "max_output_tokens": settings.REQUEST_MAX_OUTPUT_TOKENS,
        },
        safety_settings=None,  # use defaults; you can tune later
    )
    # Handle empty or safety-blocked responses
    text = getattr(resp, "text", "") or ""
    return text.strip()
