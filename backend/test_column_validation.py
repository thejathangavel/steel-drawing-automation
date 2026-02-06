import sys
sys.path.append(r"d:\steel(3)\steel\backend")

from app.services.extraction_parser import PDFParser

# Test the fixed column identification
parser = PDFParser()

# Create a mock table that simulates the problem
# Format: Sl. No. | Material | Sheet No. | Drawing Title | Qty | Rev | Date | Remarks
mock_table = [
    ["Sl. No.", "Sheet No.", "Drawing Title", "Revision Mark", "Date", "Remarks"],
    ["1", "A36 UNO", "", "QTY", "10/16/2024", "For Fabrication"],
    ["2", "A36 UNO", "", "QTY", "10/16/2024", "For Fabrication"],
    ["3", "A36 UNO", "", "QTY", "10/16/2024", "For Fabrication"],
]

print("="*80)
print("TESTING COLUMN IDENTIFICATION WITH VALIDATION")
print("="*80)

print("\nMock Table (simulating the problem):")
for row in mock_table:
    print(row)

print("\nIdentifying columns...")
col_indices = parser._identify_columns(mock_table[0], table_data=mock_table)

print(f"\nIdentified column mapping:")
for field, idx in col_indices.items():
    print(f"  {field}: column {idx}")

print("\nExpected:")
print("  sheet_no: column 2 (should skip column 1 which has 'A36 UNO')")
print("  title: column 2")
print("  revision: column 3")
print("  date: column 4")
print("  remarks: column 5")

print("\n" + "="*80)
print("If sheet_no is column 2 or higher, the fix is working!")
print("="*80)
