import re
from typing import List

def clean_text(s: str) -> str:
    s = s.replace("\x00", " ").replace("\u200b", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def split_into_chunks(text: str, max_chars: int = 2000, overlap: int = 200) -> List[str]:
    """Split text into larger chunks to reduce total number"""
    chunks, i = [], 0
    n = len(text)
    while i < n:
        end = min(i + max_chars, n)
        chunks.append(text[i:end].strip())
        i = max(0, end - overlap)
    return [c for c in chunks if c]
