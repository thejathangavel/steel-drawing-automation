import re

def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    """
    return [ int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text) ]

drawings = [
    {'drawing_no': '1AL1'},
    {'drawing_no': '1AL10'},
    {'drawing_no': '1AL2'},
    {'drawing_no': '1AL20'},
    {'drawing_no': '1AL3'},
    {'drawing_no': 'E12'},
    {'drawing_no': 'E13'},
    {'drawing_no': '2AL46'},
    {'drawing_no': '2AL47'}
]

print("--- Original Sort (Incorrect) ---")
sorted_drawings = sorted(drawings, key=lambda x: x.get('drawing_no', ''))
for d in sorted_drawings:
    print(d['drawing_no'])

print("\n--- Natural Sort (Correct) ---")
sorted_drawings_natural = sorted(drawings, key=lambda x: natural_keys(x.get('drawing_no', '')))
for d in sorted_drawings_natural:
    print(d['drawing_no'])
