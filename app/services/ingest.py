import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List
from pypdf import PdfReader
from app.utils.text import clean_text, split_into_chunks

def load_catalog(path: str = "corpus/catalog.yaml") -> Dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def pdf_to_text(pdf_path: str, max_pages: int = 10) -> str:
    """Extract text from PDF with page limit for testing"""
    reader = PdfReader(pdf_path)
    pages = []
    total_pages = len(reader.pages)
    pages_to_process = min(max_pages, total_pages)
    
    print(f"Processing {pages_to_process} pages out of {total_pages} total pages")
    
    for i, p in enumerate(reader.pages[:pages_to_process]):
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return clean_text("\n\n".join(pages))

def build_chunk_df(catalog_path: str = "corpus/catalog.yaml", max_chunks_per_doc: int = 100) -> pd.DataFrame:
    cat = load_catalog(catalog_path)
    rows: List[Dict] = []
    
    for doc in cat.get("docs", []):
        # Try to use pre-processed text file first
        processed_file = f"data/processed/{Path(doc['file']).stem}_extracted.txt"
        text_file = Path(processed_file)
        
        if text_file.exists():
            print(f"Using pre-processed text: {processed_file}")
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            # Fallback to PDF processing
            f = Path(doc["file"])
            if not f.exists():
                continue
            print(f"Processing PDF: {doc['title']}...")
            text = pdf_to_text(str(f))
        
        chunks = split_into_chunks(text)
        
        # Limit chunks to prevent memory issues
        if len(chunks) > max_chunks_per_doc:
            print(f"Limiting {doc['title']} to {max_chunks_per_doc} chunks (was {len(chunks)})")
            chunks = chunks[:max_chunks_per_doc]
        
        for idx, ch in enumerate(chunks):
            rows.append({
                "doc_id": doc["id"],
                "title": doc.get("title", ""),
                "type": doc.get("type", ""),
                "source": doc.get("source", ""),
                "date": doc.get("date", ""),
                "restrictions": doc.get("restrictions", ""),
                "chunk_id": f"{doc['id']}_c{idx}",
                "chunk_text": ch
            })
    
    return pd.DataFrame(rows)
