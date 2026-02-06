import sys
sys.path.append(r"d:\steel(3)\steel\backend")

from app.services.extraction_parser import PDFParser

# Test with the uploaded image - we need to find actual PDFs
# Let's first check if there are any PDFs in the project storage
import os

print("="*80)
print("SEARCHING FOR PDF FILES")
print("="*80)

# Check common locations
search_paths = [
    r"d:\steel(3)\steel\storage",
    r"d:\steel(3)",
    r"d:\steel\storage"
]

pdf_files = []
for path in search_paths:
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
                    if len(pdf_files) >= 5:  # Limit to 5 PDFs
                        break
            if len(pdf_files) >= 5:
                break

if pdf_files:
    print(f"\nFound {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"  - {pdf}")
else:
    print("\n✗ No PDF files found in storage directories")
    print("\nPlease provide the path to a PDF file to test extraction.")
    sys.exit(1)

# Test extraction
parser = PDFParser()

for pdf_path in pdf_files[:2]:  # Test first 2 PDFs
    print(f"\n{'='*80}")
    print(f"Testing: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    try:
        result = parser.extract_metadata(pdf_path)
        
        if result:
            if result.get("is_transmittal"):
                print(f"\n✓ Detected as TRANSMITTAL")
                print(f"  Drawings found: {len(result.get('drawings', []))}")
                for idx, drawing in enumerate(result.get('drawings', []), 1):
                    print(f"\n  Drawing {idx}:")
                    print(f"    DWG No: {drawing.get('drawing_no')}")
                    print(f"    Title: {drawing.get('description')}")
                    print(f"    REV: {drawing.get('revision_no')}")
                    print(f"    Date: {drawing.get('date')}")
                    print(f"    Remarks: {drawing.get('remarks')}")
            else:
                print(f"\n✓ Detected as INDIVIDUAL DRAWING")
                print(f"  DWG No: {result.get('drawing_no')}")
                print(f"  Title: {result.get('description')}")
                print(f"  REV: {result.get('revision_no')}")
                print(f"  Date: {result.get('date')}")
                print(f"  Remarks: {result.get('remarks')}")
        else:
            print("\n✗ Extraction returned None")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
