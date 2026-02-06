import openpyxl
import sys

def analyze(path, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Reading: {path}\n")
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            if i > 20: break
            clean_row = [str(cell) if cell is not None else '' for cell in row]
            f.write(f"R{i}: {clean_row}\n")

        f.write("Merged:\n")
        for m in ws.merged_cells.ranges:
            f.write(str(m) + "\n")

if __name__ == "__main__":
    analyze(r"d:\steel\backend\sample_files\Transmittal #62.xlsx", "transmittal_analysis.txt")
    analyze(r"d:\steel\backend\sample_files\dwng_log.xlsx", "log_analysis.txt")
