import google.generativeai as genai
import numpy as np
from typing import List
from app.core.config import settings
import time

genai.configure(api_key=settings.GOOGLE_API_KEY)
EMBED_MODEL = "text-embedding-004"

def embed_texts(texts: List[str], batch_size: int = 10) -> np.ndarray:
    """Embed texts in batches to avoid memory issues"""
    vecs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        for t in batch:
            try:
                resp = genai.embed_content(model=EMBED_MODEL, content=t)
                vecs.append(resp["embedding"])
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Error embedding text: {e}")
                # Add zero vector as fallback
                vecs.append([0.0] * 768)  # text-embedding-004 has 768 dimensions
        
        # Small delay between batches
        time.sleep(0.5)
    
    return np.array(vecs, dtype="float32")
