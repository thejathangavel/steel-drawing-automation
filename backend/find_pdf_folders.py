import os
from pathlib import Path

folders = []
for root, dirs, files in os.walk(r'd:\steel(3)\steel\storage'):
    pdfs = [f for f in files if f.endswith('.pdf')]
    if pdfs:
        folders.append((root, len(pdfs), pdfs[:3]))

for path, count, samples in sorted(folders):
    print(f'{path}: {count} PDFs')
    for sample in samples:
        print(f'  - {sample}')
