import pandas as pd
import sys
import os

def inspect_excel(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    try:
        df = pd.read_excel(file_path)
        print(f"Columns in {os.path.basename(file_path)}:")
        print(df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head())
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    inspect_excel(r"d:\steel(3)\steel\backend\Transmittal (55).xlsx")
