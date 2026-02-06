import fitz
import sys
import os

def dump_blocks(file_path, output_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    doc = fitz.open(file_path)
    page = doc[0]
    blocks = page.get_text("blocks", sort=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Blocks for {os.path.basename(file_path)}:\n")
        for b in blocks:
            # x0, y0, x1, y1, text, block_no, block_type
            f.write(f"Block {b[5]} ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}):\n")
            f.write(f"  {repr(b[4])}\n")
    
    doc.close()

if __name__ == "__main__":
    dump_blocks(r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf", r"d:\steel(3)\steel\backend\pdf_block_dump_2al46.txt")
    print("Dump completed.")
