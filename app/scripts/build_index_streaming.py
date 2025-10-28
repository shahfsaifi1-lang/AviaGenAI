import pickle
import sys
import gc
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.ingest import load_catalog
from app.utils.text import clean_text, split_into_chunks
from app.services.embed import embed_texts
import pandas as pd
import numpy as np
import faiss

def process_document_streaming(doc, max_chunks=20, chunk_size=1500):
    """Process a single document in small batches"""
    print(f"Processing {doc['title']}...")
    
    # Try pre-processed text first
    processed_file = f"data/processed/{Path(doc['file']).stem}_extracted.txt"
    text_file = Path(processed_file)
    
    if text_file.exists():
        print(f"Using pre-processed text: {processed_file}")
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print(f"PDF file not found: {doc['file']}")
        return []
    
    # Clean and chunk text
    cleaned_text = clean_text(text)
    chunks = split_into_chunks(cleaned_text, max_chars=chunk_size)
    
    # Limit chunks severely
    if len(chunks) > max_chunks:
        print(f"Limiting to {max_chunks} chunks (was {len(chunks)})")
        chunks = chunks[:max_chunks]
    
    # Process in very small batches
    batch_size = 5
    all_chunks = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
        
        # Create chunk metadata
        for j, chunk_text in enumerate(batch):
            chunk_id = f"{doc['id']}_c{i + j}"
            all_chunks.append({
                "doc_id": doc["id"],
                "title": doc.get("title", ""),
                "type": doc.get("type", ""),
                "source": doc.get("source", ""),
                "date": doc.get("date", ""),
                "restrictions": doc.get("restrictions", ""),
                "chunk_id": chunk_id,
                "chunk_text": chunk_text
            })
        
        # Force garbage collection
        gc.collect()
    
    return all_chunks

def build_index_streaming():
    """Build index with extreme memory efficiency"""
    print("🚀 Building T-6II knowledge base (streaming mode)...")
    
    # Load catalog
    cat = load_catalog("corpus/catalog.yaml")
    docs = cat.get("docs", [])
    
    # Create artifacts directory
    Path("artifacts").mkdir(exist_ok=True)
    
    all_chunks = []
    total_chunks = 0
    
    # Process each document separately
    for doc in docs:
        try:
            chunks = process_document_streaming(doc, max_chunks=15, chunk_size=1000)
            all_chunks.extend(chunks)
            total_chunks += len(chunks)
            print(f"  ✅ Added {len(chunks)} chunks (total: {total_chunks})")
            
            # Save intermediate progress
            if total_chunks > 0:
                df = pd.DataFrame(all_chunks)
                df.to_parquet("artifacts/chunks_temp.parquet")
                print(f"  💾 Saved {total_chunks} chunks to temp file")
            
            # Force garbage collection
            gc.collect()
            
        except Exception as e:
            print(f"  ❌ Error processing {doc['title']}: {e}")
            continue
    
    if total_chunks == 0:
        print("❌ No chunks created!")
        return
    
    print(f"\n📊 Total chunks created: {total_chunks}")
    
    # Create final dataframe
    df = pd.DataFrame(all_chunks)
    df.to_parquet("artifacts/chunks.parquet")
    print("✅ Chunks saved to artifacts/chunks.parquet")
    
    # Build embeddings in very small batches
    print("\n🔢 Building embeddings (this will take a while)...")
    all_embeddings = []
    
    batch_size = 3  # Very small batches
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i + batch_size]
        print(f"  Embedding batch {i//batch_size + 1}/{(len(df) + batch_size - 1)//batch_size}")
        
        try:
            batch_embeddings = embed_texts(batch_df["chunk_text"].tolist(), batch_size=1)
            all_embeddings.append(batch_embeddings)
            print(f"    ✅ Embedded {len(batch_embeddings)} chunks")
        except Exception as e:
            print(f"    ❌ Error embedding batch: {e}")
            # Add zero vectors as fallback
            zero_vecs = np.zeros((len(batch_df), 768), dtype="float32")
            all_embeddings.append(zero_vecs)
        
        # Force garbage collection
        gc.collect()
    
    # Combine all embeddings
    if all_embeddings:
        embeddings = np.vstack(all_embeddings)
        print(f"✅ Created {embeddings.shape[0]} embeddings")
        
        # Build FAISS index
        print("🔍 Building search index...")
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        
        # Create retriever
        retriever = type('Retriever', (), {
            'index': index,
            'meta': df.reset_index(drop=True),
            'search': lambda self, query, k=5: self._search(query, k)
        })()
        
        # Add search method
        def _search(self, query, k=5):
            from app.services.embed import embed_texts
            q = embed_texts([query]).astype("float32")
            faiss.normalize_L2(q)
            D, I = self.index.search(q, k)
            hits = []
            for score, idx in zip(D[0], I[0]):
                row = self.meta.iloc[int(idx)].to_dict()
                row["score"] = float(score)
                hits.append(row)
            return hits
        
        retriever._search = _search.__get__(retriever, type(retriever))
        
        # Save retriever
        with open("artifacts/retriever.pkl", "wb") as f:
            pickle.dump(retriever, f)
        
        print("✅ Search index saved to artifacts/retriever.pkl")
        print(f"\n🎉 Successfully built knowledge base with {total_chunks} chunks!")
        
        # Clean up temp file
        if Path("artifacts/chunks_temp.parquet").exists():
            Path("artifacts/chunks_temp.parquet").unlink()
    else:
        print("❌ No embeddings created!")

if __name__ == "__main__":
    build_index_streaming()
