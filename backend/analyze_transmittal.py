import openpyxl
import sys

# Force utf-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

def analyze(path):
    print(f"Reading: {path}")
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        if i > 15: break
        # Replace None with '' for cleaner printing
        clean_row = [str(cell) if cell is not None else '' for cell in row]
        print(f"R{i}: {clean_row}")

    print("Merged:")
    for m in ws.merged_cells.ranges:
        print(str(m))

if __name__ == "__main__":
    analyze(r"d:\steel\backend\sample_files\Transmittal #62.xlsx")
