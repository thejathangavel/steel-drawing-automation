import sys
sys.path.append(r"d:\steel(3)\steel\backend")

import pdfplumber
import os

# Find a transmittal-like PDF or any PDF with tables
search_paths = [r"d:\steel(3)\steel\storage"]

print("="*80)
print("SEARCHING FOR PDFs WITH TABLES")
print("="*80)

for path in search_paths:
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    
                    try:
                        with pdfplumber.open(pdf_path) as pdf:
                            if len(pdf.pages) > 0:
                                page = pdf.pages[0]
                                tables = page.extract_tables()
                                
                                if tables and len(tables) > 0:
                                    print(f"\n{'='*80}")
                                    print(f"PDF: {file}")
                                    print(f"Tables found: {len(tables)}")
                                    
                                    for t_idx, table in enumerate(tables):
                                        print(f"\nTable {t_idx + 1}:")
                                        print(f"  Rows: {len(table)}")
                                        print(f"  Columns: {len(table[0]) if table else 0}")
                                        
                                        if table and len(table) > 0:
                                            print(f"\n  Header Row:")
                                            for idx, cell in enumerate(table[0]):
                                                print(f"    Col {idx}: {cell}")
                                            
                                            if len(table) > 1:
                                                print(f"\n  First Data Row:")
                                                for idx, cell in enumerate(table[1]):
                                                    print(f"    Col {idx}: {cell}")
                                        
                                        # Only show first table of first PDF with tables
                                        print("\n" + "="*80)
                                        sys.exit(0)
                    except Exception as e:
                        continue

print("\nNo PDFs with tables found")
