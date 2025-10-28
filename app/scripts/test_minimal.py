import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.ingest import load_catalog
from app.utils.text import clean_text, split_into_chunks
import pandas as pd

def test_minimal():
    """Test with just a few lines of text"""
    print("🧪 Testing minimal pipeline...")
    
    # Create test text
    test_text = """
    T-6II Engine Start Procedure
    1. Check fuel quantity - minimum 50 gallons
    2. Verify engine instruments are normal
    3. Set throttle to idle
    4. Turn on master switch
    5. Press start button
    6. Monitor engine parameters
    
    T-6II Landing Procedure
    1. Reduce power to 2000 RPM
    2. Lower landing gear
    3. Extend flaps to approach
    4. Maintain approach speed
    5. Touch down on main gear first
    6. Apply brakes gently
    """ * 10  # Make it longer
    
    print(f"Test text length: {len(test_text)} characters")
    
    # Clean and chunk
    cleaned = clean_text(test_text)
    chunks = split_into_chunks(cleaned, max_chars=500)
    
    print(f"Created {len(chunks)} chunks")
    print(f"Chunk sizes: {[len(c) for c in chunks[:5]]}")
    
    # Create minimal dataframe
    rows = []
    for i, chunk in enumerate(chunks[:5]):  # Only first 5 chunks
        rows.append({
            "doc_id": "test_doc",
            "title": "T-6II Test Procedures",
            "type": "test",
            "source": "test",
            "date": "2025-01-01",
            "restrictions": "test",
            "chunk_id": f"test_c{i}",
            "chunk_text": chunk
        })
    
    df = pd.DataFrame(rows)
    print(f"DataFrame shape: {df.shape}")
    print("✅ Minimal test successful!")
    
    return df

if __name__ == "__main__":
    test_minimal()
