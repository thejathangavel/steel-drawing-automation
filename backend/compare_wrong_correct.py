import openpyxl

# Compare wrong output vs correct output
wrong_file = r"D:\steel(3)\steel\backend\Transmittal (55).xlsx"
correct_file = r"D:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx"

print("="*100)
print("COMPARING WRONG vs CORRECT OUTPUT")
print("="*100)

# Read WRONG output
print(f"\n{'='*100}")
print(f"WRONG OUTPUT: {wrong_file}")
print(f"{'='*100}\n")

try:
    wb_wrong = openpyxl.load_workbook(wrong_file)
    ws_wrong = wb_wrong.active
    
    print(f"Sheet Name: {ws_wrong.title}\n")
    print("First 20 rows:")
    print("-"*100)
    
    for i, row in enumerate(list(ws_wrong.rows)[:20], 1):
        values = [str(cell.value)[:25] if cell.value else "" for cell in row[:7]]
        print(f"Row {i:2d}: {' | '.join(values)}")
    
    wb_wrong.close()
except Exception as e:
    print(f"ERROR reading wrong file: {e}")

# Read CORRECT output
print(f"\n{'='*100}")
print(f"CORRECT OUTPUT: {correct_file}")
print(f"{'='*100}\n")

try:
    wb_correct = openpyxl.load_workbook(correct_file)
    ws_correct = wb_correct.active
    
    print(f"Sheet Name: {ws_correct.title}\n")
    print("First 20 rows:")
    print("-"*100)
    
    for i, row in enumerate(list(ws_correct.rows)[:20], 1):
        values = [str(cell.value)[:25] if cell.value else "" for cell in row[:7]]
        print(f"Row {i:2d}: {' | '.join(values)}")
    
    wb_correct.close()
except Exception as e:
    print(f"ERROR reading correct file: {e}")

print(f"\n{'='*100}")
print("KEY DIFFERENCES TO IDENTIFY")
print(f"{'='*100}")
print("\n1. What appears in 'Sheet No.' column in WRONG vs CORRECT?")
print("2. What appears in 'Drawing Title' column in WRONG vs CORRECT?")
print("3. What appears in 'Revision Mark' column in WRONG vs CORRECT?")
