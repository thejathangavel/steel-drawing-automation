import openpyxl
import sys

# Read the sample transmittal Excel to see what the CORRECT format should be
excel_path = r"d:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx"

wb = openpyxl.load_workbook(excel_path)
ws = wb.active

print("="*80)
print(f"SAMPLE TRANSMITTAL EXCEL: {excel_path}")
print("="*80)

print(f"\nSheet Name: {ws.title}")
print("\nFirst 20 rows:")
print("-"*80)

for i, row in enumerate(list(ws.rows)[:20], 1):
    values = [str(cell.value) if cell.value is not None else "" for cell in row]
    print(f"Row {i:2d}: {' | '.join(values[:7])}")  # Show first 7 columns

wb.close()

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("Look for:")
print("- What appears in 'Sheet No.' column")
print("- What appears in 'Drawing Title' column")
print("- What the correct format should be")
