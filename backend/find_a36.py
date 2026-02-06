import openpyxl

# Find where "A36 UNO" appears in the wrong output
wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\Transmittal (55).xlsx")
ws = wb.active

print("="*100)
print("SEARCHING FOR 'A36 UNO' IN WRONG OUTPUT")
print("="*100)

print("\nAll rows (first 50):")
for i, row in enumerate(list(ws.rows)[:50], 1):
    vals = [str(c.value) if c.value else "" for c in row[:7]]
    # Check if A36 UNO appears in any column
    if any("A36" in str(v).upper() for v in vals):
        print(f">>> Row {i} (CONTAINS A36): {vals}")
    else:
        print(f"    Row {i}: {vals}")

wb.close()

print("\n" + "="*100)
print("Now let's see the CORRECT output for comparison")
print("="*100)

wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx")
ws = wb.active

print("\nAll rows (first 50):")
for i, row in enumerate(list(ws.rows)[:50], 1):
    vals = [str(c.value) if c.value else "" for c in row[:7]]
    print(f"Row {i}: {vals}")

wb.close()
