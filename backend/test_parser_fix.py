import sys
import os
import fitz

# Add backend to path so we can import app.services
sys.path.append(r"d:\steel\backend")

from app.services.extraction_parser import PDFParser

def test_parsing():
    file_path = r"d:\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf"
    
    print(f"Testing PDFParser on: {file_path}")
    if not os.path.exists(file_path):
        print("File not found!")
        return

    parser = PDFParser()
    
    # DEBUG: Print blocks around title
    # DEBUG: Print blocks around title
    doc = fitz.open(file_path)
    page = doc[0]
    blocks = page.get_text("blocks", sort=True)
    
    with open("blocks_dump.txt", "w", encoding="utf-8") as f:
        f.write(f"--- Blocks Analysis for {file_path} ---\n")
        for i, b in enumerate(blocks):
            text = b[4].strip().replace('\n', ' | ')
            f.write(f"[{i}] {text}\n")

    # Debug: Text Dump
    text_content = page.get_text("text")
    with open("text_dump.txt", "w", encoding="utf-8") as f:
        f.write(text_content)

    metadata = parser.extract_metadata(file_path)
    print("MetaData Extracted to console (check locally)")
    with open("metadata_dump.txt", "w", encoding="utf-8") as f:
        for k, v in metadata.items():
            f.write(f"{k}: {v}\n")
        
    print("\n--------------------------")

if __name__ == "__main__":
    test_parsing()
