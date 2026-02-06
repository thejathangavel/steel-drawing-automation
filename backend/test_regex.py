import re

def parse(filename):
    print(f"Testing: {filename}")
    # Current Regex
    fn_match = re.match(r'^([A-Z0-9]+)\s*-\s*(.+?)\s*-\s*Rev\s*([A-Z0-9]+)', filename, re.IGNORECASE)
    if fn_match:
        print("  MATCH 1 (Full):")
        print(f"  Drawing: {fn_match.group(1)}")
        print(f"  Title:   {fn_match.group(2)}")
        print(f"  Rev:     {fn_match.group(3)}")
        return

    # What we need: Handle "E12 - Rev 1.pdf"
    # Format: Code - Rev X
    fn_match2 = re.match(r'^([A-Z0-9]+)\s*-\s*Rev\s*([A-Z0-9]+)', filename, re.IGNORECASE)
    if fn_match2:
        print("  MATCH 2 (Short):")
        print(f"  Drawing: {fn_match2.group(1)}")
        print(f"  Rev:     {fn_match2.group(2)}")
        return
        
    print("  NO MATCH")

parse("E12 - Rev 1.pdf")
parse("1AL23 - ANGLE - Rev 0.pdf")
