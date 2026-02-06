import pandas as pd
import openpyxl

def analyze_excel(file_path):
    print(f"--- ANALYZING: {file_path} ---")
    try:
        # 1. Read with openpyxl to get cell values directly (helps with merged headers)
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active
        
        print("First 10 rows:")
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            if i > 10: break
            print(f"Row {i}: {row}")
            
        # Check merged cells
        print("\nMerged Ranges:")
        for rng in ws.merged_cells.ranges:
            print(str(rng))
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    analyze_excel(r"d:\steel\backend\sample_files\Transmittal #62.xlsx")
    print("\n" + "="*50 + "\n")
    analyze_excel(r"d:\steel\backend\sample_files\dwng_log.xlsx")
