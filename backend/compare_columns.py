import openpyxl

# Show rows 10-25 from WRONG output to see the pattern
wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\Transmittal (55).xlsx")
ws = wb.active

print("WRONG OUTPUT - Rows 10-30")
print("="*120)

for i, row in enumerate(list(ws.rows)[9:30], 10):
    vals = [str(c.value)[:25] if c.value else "" for c in row[:7]]
    marker = ">>> " if any("A36" in str(v).upper() for v in vals) else "    "
    print(f"{marker}Row {i:3d}: {' | '.join(vals)}")

wb.close()

print("\n" + "="*120)
print("CORRECT OUTPUT - Rows 10-30")
print("="*120)

wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx")
ws = wb.active

for i, row in enumerate(list(ws.rows)[9:30], 10):
    vals = [str(c.value)[:25] if c.value else "" for c in row[:7]]
    print(f"    Row {i:3d}: {' | '.join(vals)}")

wb.close()

print("\n" + "="*120)
print("ANALYSIS:")
print("="*120)
print("Compare the column structure:")
print("- WRONG: What's in column 2 (Sheet No.)?")
print("- CORRECT: What should be in column 2 (Sheet No.)?")
