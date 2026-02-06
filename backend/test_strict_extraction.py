import sys
sys.path.append(r"d:\steel(3)\steel\backend")

from app.services.extraction_parser import PDFParser
import json

parser = PDFParser()

# Test with sample PDFs
test_files = [
    r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf",
    r"d:\steel(3)\steel\backend\sample_files\E12 - Rev 1.pdf"
]

print("="*80)
print("TESTING STRICT EXTRACTION (NO FALLBACKS)")
print("="*80)
print("\nExpected Behavior:")
print("- Extract ONLY from labeled fields (DRG No., DWG TITLE, REV., DATE)")
print("- DESCRIPTION from Revision Table ONLY")
print("- Stop after first valid match")
print("- NO dates in drawing numbers")
print("- NO material names in titles")
print("="*80)

for pdf_path in test_files:
    print(f"\n{'='*80}")
    print(f"Testing: {pdf_path}")
    print(f"{'='*80}")
    
    result = parser.extract_metadata(pdf_path)
    
    if result:
        print(f"\n✓ Extraction Result:")
        print(f"  DWG No: {result.get('drawing_no')}")
        print(f"  Title: {result.get('description')}")
        print(f"  REV: {result.get('revision_no')}")
        print(f"  Date: {result.get('date')}")
        print(f"  Remarks: {result.get('remarks')}")
        print(f"  Project: {result.get('project_name')}")
        
        # Validation checks
        print(f"\n✓ Validation:")
        dwg_no = result.get('drawing_no', '')
        if '/' in dwg_no and len(dwg_no.split('/')) == 3:
            print(f"  ❌ FAIL: Drawing number looks like a date: {dwg_no}")
        else:
            print(f"  ✅ PASS: Drawing number format OK")
        
        title = result.get('description', '')
        if title.upper() in ['ANGLE', 'PLATE', 'HSS', 'MATERIAL', 'STEEL GRADE']:
            print(f"  ❌ FAIL: Title is a material name: {title}")
        else:
            print(f"  ✅ PASS: Title is not a material name")
        
        remarks = result.get('remarks', '')
        if remarks.upper() in ['FOR FABRICATION', 'FOR APPROVAL', 'ISSUED FOR CONSTRUCTION']:
            print(f"  ✅ PASS: Remarks from revision table")
        else:
            print(f"  ⚠️  WARNING: Remarks might not be from revision table: {remarks}")
    else:
        print("\n✗ Extraction returned None")

print(f"\n{'='*80}")
print("TEST COMPLETE")
print(f"{'='*80}")
