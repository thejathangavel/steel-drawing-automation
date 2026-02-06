import sys
sys.path.append(r"d:\steel(3)\steel\backend")

from app.services.extraction_parser import PDFParser

# Simulate the table from the user's screenshot
test_table = [
    ["Sl. No.", "Sheet No.", "Drawing Title", "Revision Mark", "Date", "Remarks"],
    ["1", "A36 UNO", "", "QTY", "10/16/2024", "For Fabrication"],
    ["2", "A36 UNO", "", "QTY", "10/16/2024", "For Fabrication"],
    ["3", "A36 UNO", "", "QTY", "10/16/2024", "For Fabrication"],
]

parser = PDFParser()

print("Testing column validation...")
col_indices = parser._identify_columns(test_table[0], table_data=test_table)

print(f"\nFinal result: {col_indices}")

# Save to file
with open("debug_output.txt", "w") as f:
    f.write(f"Column mapping: {col_indices}\n")
    if col_indices and 'sheet_no' in col_indices:
        f.write(f"Sheet No. column index: {col_indices['sheet_no']}\n")
