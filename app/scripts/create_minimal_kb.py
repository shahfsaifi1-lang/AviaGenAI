import pickle
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
import faiss
from app.services.embed import embed_texts

def create_minimal_knowledge_base():
    """Create a minimal knowledge base with hardcoded T-6II procedures"""
    print("🚀 Creating minimal T-6II knowledge base...")
    
    # Hardcoded T-6II procedures (small and focused)
    procedures = [
        {
            "doc_id": "t6_engine_start",
            "title": "T-6II Engine Start Procedure",
            "type": "checklist",
            "source": "hardcoded",
            "date": "2025-01-01",
            "restrictions": "public",
            "chunk_id": "t6_engine_start_c0",
            "chunk_text": "T-6II Engine Start Procedure: 1. Check fuel quantity minimum 50 gallons. 2. Verify engine instruments normal. 3. Set throttle to idle. 4. Turn on master switch. 5. Press start button. 6. Monitor engine parameters during start."
        },
        {
            "doc_id": "t6_landing",
            "title": "T-6II Landing Procedure", 
            "type": "checklist",
            "source": "hardcoded",
            "date": "2025-01-01",
            "restrictions": "public",
            "chunk_id": "t6_landing_c0",
            "chunk_text": "T-6II Landing Procedure: 1. Reduce power to 2000 RPM. 2. Lower landing gear. 3. Extend flaps to approach position. 4. Maintain approach speed 80-85 knots. 5. Touch down on main gear first. 6. Apply brakes gently after nose wheel touchdown."
        },
        {
            "doc_id": "t6_preflight",
            "title": "T-6II Pre-flight Inspection",
            "type": "checklist", 
            "source": "hardcoded",
            "date": "2025-01-01",
            "restrictions": "public",
            "chunk_id": "t6_preflight_c0",
            "chunk_text": "T-6II Pre-flight Inspection: 1. Check fuel quantity and quality. 2. Inspect engine for leaks. 3. Check control surfaces for damage. 4. Verify landing gear operation. 5. Test flight controls. 6. Check instruments and avionics."
        },
        {
            "doc_id": "t6_emergency",
            "title": "T-6II Emergency Procedures",
            "type": "emergency",
            "source": "hardcoded", 
            "date": "2025-01-01",
            "restrictions": "public",
            "chunk_id": "t6_emergency_c0",
            "chunk_text": "T-6II Emergency Procedures: 1. Engine failure - maintain airspeed 80 knots minimum. 2. Electrical failure - check circuit breakers. 3. Landing gear failure - follow emergency extension procedures. 4. Fire - shut down engine immediately. 5. Emergency landing - select suitable field."
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(procedures)
    print(f"✅ Created {len(df)} procedure chunks")
    
    # Create artifacts directory
    Path("artifacts").mkdir(exist_ok=True)
    
    # Save chunks
    df.to_parquet("artifacts/chunks.parquet")
    print("✅ Saved chunks to artifacts/chunks.parquet")
    
    # Create embeddings (very small batch)
    print("🔢 Creating embeddings...")
    try:
        texts = df["chunk_text"].tolist()
        embeddings = embed_texts(texts, batch_size=1)
        print(f"✅ Created {embeddings.shape[0]} embeddings")
        
        # Build FAISS index
        print("🔍 Building search index...")
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        
        # Use the existing Retriever class
        from app.services.retrieve import Retriever
        retriever = Retriever()
        retriever.index = index
        retriever.meta = df.reset_index(drop=True)
        
        # Save retriever
        with open("artifacts/retriever.pkl", "wb") as f:
            pickle.dump(retriever, f)
        
        print("✅ Search index saved to artifacts/retriever.pkl")
        
        # Test the retriever
        print("\n🧪 Testing search...")
        results = retriever.search("How do I start the engine?", k=2)
        print(f"Found {len(results)} results for 'engine start'")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['title']} (score: {result['score']:.3f})")
        
        print(f"\n🎉 Minimal knowledge base created successfully!")
        print(f"📊 Contains {len(df)} T-6II procedure chunks")
        print("🔍 Ready for semantic search!")
        
    except Exception as e:
        print(f"❌ Error creating embeddings: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_minimal_knowledge_base()
