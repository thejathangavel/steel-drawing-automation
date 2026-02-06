"""
Test script to verify strict PDF field extraction according to user requirements.

Expected extraction from sample PDF:
- DWG No: a146
- DWG TITLE: ANGLE
- REV: 0
- DATE: 03/07/2025
- DESCRIPTION: For Fabrication
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.extraction_parser import PDFParser

def test_strict_extraction():
    """Test strict field extraction from sample PDF"""
    
    # Sample PDF path
    sample_pdf = r"d:\steel(3)\steel\backend\sample_files\2AL46 - LINTEL ANGLE - Rev 0.pdf"
    
    if not os.path.exists(sample_pdf):
        print(f"ERROR: Sample PDF not found at {sample_pdf}")
        return
    
    print("="*80)
    print("TESTING STRICT PDF FIELD EXTRACTION")
    print("="*80)
    print(f"\nProcessing: {os.path.basename(sample_pdf)}")
    print("\nExpected Results (for 2AL46):")
    print("  DWG No:      2AL46")
    print("  DWG TITLE:   LINTEL ANGLE")
    print("  REV:         0")
    print("  DATE:        06/26/2025")
    print("  DESCRIPTION: For Fabrication")
    print("\n" + "="*80)

    
    # Initialize parser
    parser = PDFParser()
    
    # Extract metadata
    result = parser.extract_metadata(sample_pdf)
    
    if not result:
        print("\nERROR: No metadata extracted!")
        return
    
    # Check if it's a transmittal
    if result.get("is_transmittal"):
        print("\nWARNING: PDF detected as transmittal, not a single drawing")
        print(f"Found {len(result.get('drawings', []))} drawings")
        return
    
    # Display extracted results
    print("\nExtracted Results:")
    print(f"  DWG No:      {result.get('drawing_no', 'NOT FOUND')}")
    print(f"  DWG TITLE:   {result.get('description', 'NOT FOUND')}")
    print(f"  REV:         {result.get('revision_no', 'NOT FOUND')}")
    print(f"  DATE:        {result.get('date', 'NOT FOUND')}")
    print(f"  DESCRIPTION: {result.get('remarks', 'NOT FOUND')}")
    print(f"  Project:     {result.get('project_name', 'NOT FOUND')}")
    
    # Validation
    print("\n" + "="*80)
    print("VALIDATION RESULTS:")
    print("="*80)
    
    checks = {
        "DWG No": (result.get('drawing_no'), '2AL46'),
        "DWG TITLE": (result.get('description'), 'LINTEL ANGLE'),
        "REV": (result.get('revision_no'), '0'),
        "DATE": (result.get('date'), '06/26/2025'),
        "DESCRIPTION": (result.get('remarks'), 'For Fabrication')
    }

    
    all_passed = True
    for field, (actual, expected) in checks.items():
        if actual == expected:
            print(f"  ✓ {field}: PASS")
        else:
            print(f"  ✗ {field}: FAIL (got '{actual}', expected '{expected}')")
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ ALL CHECKS PASSED!")
    else:
        print("✗ SOME CHECKS FAILED - Review extraction logic")
    print("="*80)
    
    # Display full metadata for debugging
    print("\nFull Metadata:")
    for key, value in result.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    import io
    import sys
    
    # Capture output
    output = io.StringIO()
    original_stdout = sys.stdout
    
    # Duplicate output to both console and string
    class TeeOutput:
        def __init__(self, *outputs):
            self.outputs = outputs
        def write(self, text):
            for output in self.outputs:
                output.write(text)
        def flush(self):
            for output in self.outputs:
                output.flush()
    
    sys.stdout = TeeOutput(original_stdout, output)
    
    try:
        test_strict_extraction()
    finally:
        sys.stdout = original_stdout
        
        # Save to file with UTF-8 encoding
        with open("test_output.txt", "w", encoding="utf-8") as f:
            f.write(output.getvalue())
        
        print("\nOutput saved to test_output.txt")


