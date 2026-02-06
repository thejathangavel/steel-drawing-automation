import fitz
import os

def inspect_layout(file_path):
    doc = fitz.open(file_path)
    page = doc[0]
    blocks = page.get_text("blocks")
    
    print(f"Layout for {os.path.basename(file_path)}")
    print("-" * 50)
    for b in blocks:
        # b = (x0, y0, x1, y1, "text", block_no, block_type)
        print(f"Block {b[5]} [{b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}]: {repr(b[4])}")
    doc.close()

if __name__ == "__main__":
    pdf_path = r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf"
    inspect_layout(pdf_path)
