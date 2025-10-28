#!/usr/bin/env python3
"""
PDF Text Extraction Script for AviaGenAI Corpus
Extracts text from T-6II documentation for AI processing
"""

import os
import sys
from pathlib import Path
from pypdf import PdfReader
import json
from datetime import datetime

def extract_pdf_text(pdf_path: str, output_dir: str = "data/processed") -> dict:
    """
    Extract text from PDF and save as structured data
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Read PDF
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        print(f"Processing PDF: {pdf_path}")
        print(f"Total pages: {total_pages}")
        
        # Extract text from all pages
        full_text = ""
        page_texts = []
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                page_texts.append({
                    "page": page_num,
                    "text": page_text,
                    "char_count": len(page_text)
                })
                full_text += f"\n--- PAGE {page_num} ---\n{page_text}\n"
                print(f"Processed page {page_num}/{total_pages}")
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                page_texts.append({
                    "page": page_num,
                    "text": "",
                    "char_count": 0,
                    "error": str(e)
                })
        
        # Create metadata
        metadata = {
            "source_file": pdf_path,
            "extraction_date": datetime.now().isoformat(),
            "total_pages": total_pages,
            "total_characters": len(full_text),
            "pages_processed": len([p for p in page_texts if p.get("text")]),
            "pages_with_errors": len([p for p in page_texts if p.get("error")])
        }
        
        # Save full text
        output_file = Path(output_dir) / f"{Path(pdf_path).stem}_extracted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Save structured data
        json_file = Path(output_dir) / f"{Path(pdf_path).stem}_structured.json"
        structured_data = {
            "metadata": metadata,
            "pages": page_texts
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Extraction complete!")
        print(f"📄 Full text saved to: {output_file}")
        print(f"📊 Structured data saved to: {json_file}")
        print(f"📈 Total characters: {len(full_text):,}")
        
        return metadata
        
    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return {"error": str(e)}

def main():
    """Main function to process T-6II PDF"""
    pdf_path = "corpus/t6ii_checklists/519613250-Beechcraft-T-6B-Texan-II-Flight-Training-Instructions.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print("🛩️ AviaGenAI PDF Text Extraction")
    print("=" * 50)
    
    result = extract_pdf_text(pdf_path)
    
    if "error" not in result:
        print(f"\n🎯 Ready for next steps:")
        print(f"   • Vector embeddings")
        print(f"   • Document search")
        print(f"   • RAG system")
        print(f"   • AI training")

if __name__ == "__main__":
    main()

