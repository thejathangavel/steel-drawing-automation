import sys
sys.path.append(r"d:\steel(3)\steel\backend")

from app.services.extraction_parser import PDFParser

# Test with the uploaded transmittal PDF image
# Since we only have an image, we'll need the actual PDF file
# For now, let's create a test that shows the structure

parser = PDFParser()

# You'll need to provide the actual PDF file path
pdf_path = r"d:\steel(3)\test_transmittal.pdf"  # Update this path

print("Testing Transmittal Extraction...")
print("=" * 60)

try:
    result = parser.extract_metadata(pdf_path)
    
    if result and result.get("is_transmittal"):
        print(f"✓ Detected as TRANSMITTAL PDF")
        print(f"✓ Extracted {len(result['drawings'])} drawings")
        print("\nDrawings extracted:")
        print("-" * 60)
        
        for idx, drawing in enumerate(result['drawings'], 1):
            print(f"\n{idx}. Drawing No: {drawing.get('drawing_no')}")
            print(f"   Title: {drawing.get('description')}")
            print(f"   Revision: {drawing.get('revision_no')}")
            print(f"   Date: {drawing.get('date')}")
            print(f"   Remarks: {drawing.get('remarks')}")
    else:
        print("✗ Not detected as transmittal or extraction failed")
        if result:
            print(f"Single drawing extracted: {result.get('drawing_no')}")
        
except FileNotFoundError:
    print(f"ERROR: PDF file not found at {pdf_path}")
    print("\nPlease update the pdf_path variable with the actual transmittal PDF location.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
