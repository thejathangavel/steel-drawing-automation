import sys
sys.path.append(r"d:\steel(3)\steel\backend")

import fitz  # PyMuPDF
import os

# Let's inspect the actual PDF structure to see what labels exist
sample_files = [
    r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf",
    r"d:\steel(3)\steel\backend\sample_files\E12 - Rev 1.pdf"
]

for pdf_path in sample_files:
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        continue
        
    print("="*80)
    print(f"PDF: {os.path.basename(pdf_path)}")
    print("="*80)
    
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Get all text
    text = page.get_text("text")
    lines = text.split("\n")
    
    print("\nSearching for key labels:")
    print("-"*80)
    
    key_labels = ["DRG No", "DWG No", "DWG TITLE", "REV", "DATE", "DESCRIPTION", "SHEET NO", "DRAWING NO"]
    
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        for label in key_labels:
            if label.upper() in line_upper:
                # Show context (3 lines before and after)
                start = max(0, i-2)
                end = min(len(lines), i+5)
                print(f"\nFound '{label}' at line {i}:")
                for j in range(start, end):
                    prefix = ">>> " if j == i else "    "
                    print(f"{prefix}{j}: {lines[j]}")
                break
    
    doc.close()
    print("\n")
