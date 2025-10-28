import pickle
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.services.ingest import build_chunk_df
from app.services.retrieve import Retriever

def main():
    print("Building T-6II knowledge base...")
    
    print("Step 1: Extracting and chunking text...")
    df = build_chunk_df("corpus/catalog.yaml")
    print(f"Created {len(df)} text chunks")
    
    print("Step 2: Creating artifacts directory...")
    Path("artifacts").mkdir(exist_ok=True)
    
    print("Step 3: Saving chunks to parquet...")
    df.to_parquet("artifacts/chunks.parquet")
    print("Chunks saved to artifacts/chunks.parquet")
    
    print("Step 4: Building search index (this may take a while)...")
    r = Retriever()
    r.build(df)
    
    print("Step 5: Saving search index...")
    with open("artifacts/retriever.pkl", "wb") as f:
        pickle.dump(r, f)
    
    print(f"✅ Successfully indexed {len(df)} chunks!")
    print("Files created:")
    print("  - artifacts/chunks.parquet")
    print("  - artifacts/retriever.pkl")

if __name__ == "__main__":
    main()
