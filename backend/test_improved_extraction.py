import sys
sys.path.append(r"d:\steel(3)\steel\backend")

from app.services.extraction_parser import PDFParser
import json

parser = PDFParser()

# Test with a sample PDF
test_files = [
    r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf",
]

print("="*80)
print("TESTING IMPROVED EXTRACTION LOGIC")
print("="*80)

for pdf_path in test_files:
    print(f"\nTesting: {pdf_path}")
    print("-"*80)
    
    result = parser.extract_metadata(pdf_path)
    
    if result:
        if result.get("is_transmittal"):
            print(f"\n✓ Type: TRANSMITTAL")
            print(f"  Drawings extracted: {len(result.get('drawings', []))}")
            
            for idx, drawing in enumerate(result.get('drawings', [])[:5], 1):  # Show first 5
                print(f"\n  Drawing {idx}:")
                print(f"    DWG No: {drawing.get('drawing_no')}")
                print(f"    Title: {drawing.get('description')}")
                print(f"    REV: {drawing.get('revision_no')}")
                print(f"    Date: {drawing.get('date')}")
                print(f"    Remarks: {drawing.get('remarks')}")
                
                # Validation check
                dwg_no = drawing.get('drawing_no', '')
                if '/' in dwg_no and len(dwg_no.split('/')) == 3:
                    print(f"    ⚠️  WARNING: Drawing number looks like a date!")
        else:
            print(f"\n✓ Type: INDIVIDUAL DRAWING")
            print(f"  DWG No: {result.get('drawing_no')}")
            print(f"  Title: {result.get('description')}")
            print(f"  REV: {result.get('revision_no')}")
            print(f"  Date: {result.get('date')}")
            print(f"  Remarks: {result.get('remarks')}")
            
            # Validation check
            dwg_no = result.get('drawing_no', '')
            if '/' in dwg_no and len(dwg_no.split('/')) == 3:
                print(f"  ⚠️  WARNING: Drawing number looks like a date!")
            else:
                print(f"  ✓ Drawing number format OK")
    else:
        print("\n✗ Extraction returned None")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
