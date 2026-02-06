import openpyxl

print("="*80)
print("WRONG OUTPUT")
print("="*80)

wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\Transmittal (55).xlsx")
ws = wb.active

for i, row in enumerate(list(ws.rows)[10:16], 11):
    vals = [str(c.value) if c.value else "" for c in row[:6]]
    print(f"Row {i}: {vals}")

wb.close()

print("\n" + "="*80)
print("CORRECT OUTPUT")
print("="*80)

wb = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx")
ws = wb.active

for i, row in enumerate(list(ws.rows)[10:16], 11):
    vals = [str(c.value) if c.value else "" for c in row[:6]]
    print(f"Row {i}: {vals}")

wb.close()
