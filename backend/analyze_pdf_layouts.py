import fitz
import os
import re

def analyze_pdf(file_path):
    print(f"\nAnalyzing: {os.path.basename(file_path)}")
    print("=" * 40)
    doc = fitz.open(file_path)
    page = doc[0]
    blocks = page.get_text("blocks")
    
    # Sort blocks by y then x
    blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
    
    labels = ["DWG No.", "DRG No.", "DWG TITLE", "REV.", "DATE", "DESCRIPTION"]
    
    for i, b in enumerate(blocks):
        text = b[4].strip()
        for label in labels:
            if label.upper() in text.upper():
                print(f"LABEL: {repr(text)} at Block {b[5]} [{b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}]")
                
                # Check 5 nearby blocks (after in sorted list)
                for j in range(1, 10):
                    if i + j < len(blocks):
                        near = blocks[i+j]
                        # Is it vertically below and horizontally aligned?
                        # Or is it very close?
                        print(f"  NEAR {j}: {repr(near[4].strip())} at [{near[0]:.1f}, {near[1]:.1f}, {near[2]:.1f}, {near[3]:.1f}]")
    doc.close()

if __name__ == "__main__":
    analyze_pdf(r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf")
    analyze_pdf(r"d:\steel(3)\steel\backend\sample_files\E12 - Rev 1.pdf")
