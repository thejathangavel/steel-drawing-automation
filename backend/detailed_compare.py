import openpyxl

print("="*100)
print("DETAILED COMPARISON - WRONG vs CORRECT")
print("="*100)

# WRONG OUTPUT
print("\n" + "="*100)
print("WRONG OUTPUT: Transmittal (55).xlsx")
print("="*100)

wb_wrong = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\Transmittal (55).xlsx")
ws_wrong = wb_wrong.active

print("\nHeader Row:")
header_wrong = list(ws_wrong.rows)[9]  # Row 10 is usually header
print([str(c.value) for c in header_wrong[:7]])

print("\nData Rows 11-20:")
for i, row in enumerate(list(ws_wrong.rows)[10:20], 11):
    vals = [str(c.value)[:30] if c.value else "" for c in row[:7]]
    print(f"Row {i}: {vals}")

wb_wrong.close()

# CORRECT OUTPUT
print("\n" + "="*100)
print("CORRECT OUTPUT: Transmittal #62.xlsx")
print("="*100)

wb_correct = openpyxl.load_workbook(r"D:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx")
ws_correct = wb_correct.active

print("\nHeader Row:")
header_correct = list(ws_correct.rows)[9]  # Row 10 is usually header
print([str(c.value) for c in header_correct[:7]])

print("\nData Rows 11-20:")
for i, row in enumerate(list(ws_correct.rows)[10:20], 11):
    vals = [str(c.value)[:30] if c.value else "" for c in row[:7]]
    print(f"Row {i}: {vals}")

wb_correct.close()

print("\n" + "="*100)
print("ANALYSIS")
print("="*100)
print("\nCompare column by column:")
print("1. Sl. No. - Should be sequential numbers (1, 2, 3...)")
print("2. Sheet No. - Should be drawing numbers (e.g., 2AL46, 1AL1, etc.)")
print("3. Drawing Title - Should be titles (e.g., LINTEL ANGLE, COLUMN, etc.)")
print("4. Revision Mark - Should be revision (0, 1, A, B, etc.)")
print("5. Date - Should be dates")
print("6. Remarks - Should be 'For Fabrication', 'For Approval', etc.")
