import openpyxl

# Compare wrong output vs correct output
wrong_file = r"D:\steel(3)\steel\backend\Transmittal (55).xlsx"
correct_file = r"D:\steel(3)\steel\backend\sample_files\Transmittal #62.xlsx"

output_file = r"D:\steel(3)\steel\backend\comparison_analysis.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("="*100 + "\n")
    f.write("COMPARING WRONG vs CORRECT OUTPUT\n")
    f.write("="*100 + "\n\n")
    
    # Read WRONG output
    f.write("="*100 + "\n")
    f.write(f"WRONG OUTPUT: {wrong_file}\n")
    f.write("="*100 + "\n\n")
    
    try:
        wb_wrong = openpyxl.load_workbook(wrong_file)
        ws_wrong = wb_wrong.active
        
        f.write(f"Sheet Name: {ws_wrong.title}\n\n")
        f.write("First 25 rows:\n")
        f.write("-"*100 + "\n")
        
        for i, row in enumerate(list(ws_wrong.rows)[:25], 1):
            values = [str(cell.value) if cell.value else "" for cell in row[:7]]
            f.write(f"Row {i:2d}: {' | '.join(values)}\n")
        
        wb_wrong.close()
    except Exception as e:
        f.write(f"ERROR reading wrong file: {e}\n")
    
    # Read CORRECT output
    f.write("\n" + "="*100 + "\n")
    f.write(f"CORRECT OUTPUT: {correct_file}\n")
    f.write("="*100 + "\n\n")
    
    try:
        wb_correct = openpyxl.load_workbook(correct_file)
        ws_correct = wb_correct.active
        
        f.write(f"Sheet Name: {ws_correct.title}\n\n")
        f.write("First 25 rows:\n")
        f.write("-"*100 + "\n")
        
        for i, row in enumerate(list(ws_correct.rows)[:25], 1):
            values = [str(cell.value) if cell.value else "" for cell in row[:7]]
            f.write(f"Row {i:2d}: {' | '.join(values)}\n")
        
        wb_correct.close()
    except Exception as e:
        f.write(f"ERROR reading correct file: {e}\n")

print(f"Analysis saved to: {output_file}")
