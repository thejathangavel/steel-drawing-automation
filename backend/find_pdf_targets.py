import fitz
import os

def find_targets(file_path):
    doc = fitz.open(file_path)
    page = doc[0]
    blocks = page.get_text("blocks")
    
    targets = ["DWG No.", "DWG TITLE", "REV.", "DATE", "DESCRIPTION", "2AL46", "LINTEL ANGLE"]
    
    print(f"Target findings for {os.path.basename(file_path)}:")
    for b in blocks:
        text = b[4].strip()
        for target in targets:
            if target.upper() in text.upper():
                print(f"Block {b[5]} [{b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}]: {repr(text)}")
                break
    doc.close()

if __name__ == "__main__":
    pdf_path = r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf"
    find_targets(pdf_path)
