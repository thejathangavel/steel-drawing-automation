import openpyxl

# Read the WRONG output and show ALL rows to understand the structure
wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\Transmittal (55).xlsx")
ws = wb.active

print("COMPLETE WRONG OUTPUT FILE")
print("="*100)

all_rows = list(ws.rows)
print(f"Total rows: {len(all_rows)}\n")

for i, row in enumerate(all_rows, 1):
    vals = [str(c.value) if c.value else "" for c in row[:7]]
    # Highlight rows with A36
    if any("A36" in str(v).upper() for v in vals):
        print(f">>> Row {i:3d} [HAS A36]: {vals}")
    else:
        print(f"    Row {i:3d}: {vals}")

wb.close()
