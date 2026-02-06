import openpyxl
import os

# Compare wrong output vs correct output
wrong_file = None
correct_file = r"d:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx"

# Find Transmittal(55) file
sample_dir = r"d:\steel(3)\steel\backend\sample_files"
for file in os.listdir(sample_dir):
    if "Transmittal" in file and "55" in file and file.endswith(".xlsx"):
        wrong_file = os.path.join(sample_dir, file)
        break

if not wrong_file:
    print("ERROR: Could not find Transmittal(55) file")
    exit(1)

print("="*80)
print("COMPARING WRONG vs CORRECT OUTPUT")
print("="*80)

# Read WRONG output
print(f"\n{'='*80}")
print(f"WRONG OUTPUT: {os.path.basename(wrong_file)}")
print(f"{'='*80}\n")

wb_wrong = openpyxl.load_workbook(wrong_file)
ws_wrong = wb_wrong.active

print("First 15 data rows:")
for i, row in enumerate(list(ws_wrong.rows)[:15], 1):
    values = [str(cell.value)[:30] if cell.value else "" for cell in row[:6]]
    print(f"Row {i:2d}: {' | '.join(values)}")

wb_wrong.close()

# Read CORRECT output
print(f"\n{'='*80}")
print(f"CORRECT OUTPUT: {os.path.basename(correct_file)}")
print(f"{'='*80}\n")

wb_correct = openpyxl.load_workbook(correct_file)
ws_correct = wb_correct.active

print("First 15 data rows:")
for i, row in enumerate(list(ws_correct.rows)[:15], 1):
    values = [str(cell.value)[:30] if cell.value else "" for cell in row[:6]]
    print(f"Row {i:2d}: {' | '.join(values)}")

wb_correct.close()

print(f"\n{'='*80}")
print("ANALYSIS")
print(f"{'='*80}")
print("\nCompare the 'Sheet No.' column in both files:")
print("- WRONG: What appears in Sheet No.?")
print("- CORRECT: What should appear in Sheet No.?")
