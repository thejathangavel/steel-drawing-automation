import openpyxl

# Read the WRONG output and show rows with A36
wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\Transmittal (55).xlsx")
ws = wb.active

print("ROWS CONTAINING 'A36' IN WRONG OUTPUT")
print("="*100)

all_rows = list(ws.rows)

for i, row in enumerate(all_rows, 1):
    vals = [str(c.value) if c.value else "" for c in row[:7]]
    # Show rows with A36
    if any("A36" in str(v).upper() for v in vals):
        print(f"Row {i:3d}: {vals}")

print("\n" + "="*100)
print("CONTEXT: Show 5 rows before and after first A36 row")
print("="*100)

# Find first A36 row
first_a36_row = None
for i, row in enumerate(all_rows, 1):
    vals = [str(c.value) if c.value else "" for c in row[:7]]
    if any("A36" in str(v).upper() for v in vals):
        first_a36_row = i
        break

if first_a36_row:
    start = max(1, first_a36_row - 5)
    end = min(len(all_rows), first_a36_row + 5)
    
    for i in range(start - 1, end):
        row = all_rows[i]
        vals = [str(c.value) if c.value else "" for c in row[:7]]
        marker = ">>> " if (i + 1) == first_a36_row else "    "
        print(f"{marker}Row {i+1:3d}: {vals}")

wb.close()
