import sys
import os
sys.path.append(r"d:\steel\backend")
from app.services.excel_manager import ExcelManager

em = ExcelManager()
drawings = [
    {'drawing_no': '1AL1'},
    {'drawing_no': '1AL10'},
    {'drawing_no': '1AL2'},
    {'drawing_no': '1AL20'},
    {'drawing_no': 'E2'},
    {'drawing_no': 'E12'},
    {'drawing_no': 'E1'},
]

print("Testing ExcelManager natural sort...")
try:
    drawings.sort(key=lambda x: em._natural_keys(x.get('drawing_no', '')))
    results = [d['drawing_no'] for d in drawings]
    print("Sorted Results:", results)
    
    expected = ['1AL1', '1AL2', '1AL10', '1AL20', 'E1', 'E2', 'E12']
    if results == expected:
        print("SUCCESS: Sorting is correct.")
    else:
        print("FAILURE: Sorting is incorrect.")
        print("Expected:", expected)

except Exception as e:
    print(f"Error: {e}")
