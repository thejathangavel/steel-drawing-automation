
import os
import sys

# Add backend to path
sys.path.append(r"d:\steel\backend")

try:
    from app.services.extraction_parser import PDFParser
except ImportError as e:
    with open("reproduce_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Import Error: {e}")
    sys.exit(1)

def analyze_pdfs():
    output_lines = []
    output_lines.append("Initializing PDFParser...")
    parser = PDFParser()
    sample_dir = r"d:\steel\backend\sample_files"
    
    if not os.path.exists(sample_dir):
        output_lines.append(f"Directory not found: {sample_dir}")
        with open("reproduce_output.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        return

    files = [f for f in os.listdir(sample_dir) if f.lower().endswith('.pdf')]
    output_lines.append(f"Found {len(files)} PDF files.")
    
    for f in files:
        path = os.path.join(sample_dir, f)
        output_lines.append(f"\n--- Analyzing: {repr(f)} ---")


        try:
            # Always dump blocks for debugging
            if True:
                import fitz
                doc = fitz.open(path)
                num_pages = len(doc)
                output_lines.append(f"\n--- BLOCKS for {f} (Pages: {num_pages}) ---")
                
                for p_idx in range(num_pages):
                    page = doc[p_idx]
                    blocks = page.get_text("blocks", sort=True)
                    output_lines.append(f"\n  -- Page {p_idx+1} --")
                    for i, b in enumerate(blocks):
                         output_lines.append(f"Block {i}: {repr(b[4])}")
                doc.close()

            metadata = parser.extract_metadata(path)
            output_lines.append("Extracted Metadata:")
            if metadata:
                for k, v in metadata.items():
                    output_lines.append(f"  {k}: {repr(v)}")
            else:
                output_lines.append("  None")
        except Exception as e:
            output_lines.append(f"Error: {e}")
            import traceback
            output_lines.append(traceback.format_exc())

    with open("reproduce_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

if __name__ == "__main__":
    analyze_pdfs()
