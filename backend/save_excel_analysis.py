import openpyxl

# Read the sample transmittal Excel to see what the CORRECT format should be
excel_path = r"d:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx"

wb = openpyxl.load_workbook(excel_path)
ws = wb.active

output_file = r"d:\steel(3)\steel\backend\sample_excel_analysis.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write(f"SAMPLE TRANSMITTAL EXCEL: {excel_path}\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"Sheet Name: {ws.title}\n\n")
    f.write("First 30 rows:\n")
    f.write("-"*80 + "\n")
    
    for i, row in enumerate(list(ws.rows)[:30], 1):
        values = [str(cell.value) if cell.value is not None else "" for cell in row]
        f.write(f"Row {i:2d}: {' | '.join(values[:8])}\n")  # Show first 8 columns

wb.close()

print(f"Analysis saved to: {output_file}")
print("Please check the file to see the correct format.")
