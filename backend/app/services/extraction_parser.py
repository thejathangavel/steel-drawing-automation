import fitz  # PyMuPDF
import pdfplumber
import os
import re
from datetime import datetime

class PDFParser:
    def __init__(self):
        pass

    def extract_metadata(self, file_path: str):
        """
        Extracts metadata using layout-preserving block analysis.
        First checks if PDF is a transmittal table, if yes extracts all rows.
        Otherwise extracts single drawing metadata.
        """
        filename_only = os.path.basename(file_path)
        
        # 0. Check for Transmittal by Filename (Fastest/Safest)
        if "TRANSMITTAL" in filename_only.upper():
             transmittal_data = self.detect_and_extract_transmittal(file_path)
             if transmittal_data: return transmittal_data

        # 1. Parse Filename (Primary source of truth for structural steel drawings)
        # Format A: "DRAWING_NO - TITLE - Rev X.pdf"
        # Format B: "DRAWING_NO - Rev X.pdf" (e.g. E-Sheets)
        # Format C: "DRAWING_NO - TITLE.pdf" (No Rev)
        
        file_meta = {}
        name_no_ext = os.path.splitext(filename_only)[0]
        
        # Try Format A
        fn_match = re.match(r'^(.+?)\s*-\s*(.+?)\s*-\s*Rev\s*([A-Z0-9]+)', name_no_ext, re.IGNORECASE)
        if fn_match:
            file_meta["drawing_no"] = fn_match.group(1).strip()
            file_meta["description"] = fn_match.group(2).strip()
            file_meta["revision_no"] = fn_match.group(3).strip()
        else:
            # Try Format B
            fn_match2 = re.match(r'^(.+?)\s*-\s*Rev\s*([A-Z0-9]+)', name_no_ext, re.IGNORECASE)
            if fn_match2:
                file_meta["drawing_no"] = fn_match2.group(1).strip()
                file_meta["revision_no"] = fn_match2.group(2).strip()
            else:
                # Try Format C (Simple "DWG - TITLE")
                # Exclude if it looks like a transmittal check
                fn_match3 = re.match(r'^(.+?)\s*-\s*(.+)', name_no_ext)
                if fn_match3:
                     file_meta["drawing_no"] = fn_match3.group(1).strip()
                     file_meta["description"] = fn_match3.group(2).strip()
        
        # Check if this is a transmittal table PDF
        # KEY CHANGE: Only check for transmittal if we DID NOT find a valid drawing number in the filename.
        # If the filename looks like "E12 - Title - Rev 0.pdf", it is definitely a drawing, not a transmittal.
        if not file_meta.get("drawing_no"):
            transmittal_data = self.detect_and_extract_transmittal(file_path)
            if transmittal_data:
                return transmittal_data
        
        # Double check: Even if we have a filename match, if the file content explicitly screams "TRANSMITTAL" in the text
        # we might want to consider it. BUT, given the user's issue with BOMs being detected as transmittals,
        # relying on the filename (which is very specific) is much safer.
        # So we skip transmittal detection if file_meta has drawing_no.
        
        # Otherwise, proceed with single drawing extraction
        doc = fitz.open(file_path)
        if len(doc) == 0:
            return None
            
        page = doc[0]
        
        # --- Strict Extraction Strategy (User Request) ---
        blocks = page.get_text("blocks", sort=True)
        strict_data = self._extract_strict_data(blocks)
        # -----------------------------------------------

        # MERGE STRATEGY: Filename > Strict Block Extraction > Defaults
        
        # 1. Drawing Number
        if file_meta.get("drawing_no"):
            final_drawing_no = file_meta["drawing_no"]
        elif strict_data.get("drawing_no"):
            final_drawing_no = strict_data["drawing_no"]
        else:
            # Fallback to base filename
            final_drawing_no = os.path.splitext(filename_only)[0]

        # 2. Revision
        if file_meta.get("revision_no"):
            rev = file_meta["revision_no"]
        elif strict_data.get("revision_no"):
            rev = strict_data["revision_no"]
        else:
            rev = "0"

        # 3. Description/Title
        if file_meta.get("description"):
            desc = file_meta["description"]
        elif strict_data.get("description"):
            desc = strict_data["description"]
        else:
            desc = ""

        # 4. Date
        if strict_data.get("date"):
            date_str = strict_data["date"]
        else:
            date_str = datetime.now().strftime("%m/%d/%Y")

        # 5. Remarks
        if strict_data.get("remarks"):
            remarks = strict_data["remarks"]
        else:
            remarks = "For Fabrication"

        # 6. Project Name
        project_name = self._extract_project_name(blocks)

        # 7. HOLD Detection (Fast Text/Filename)
        # Check if HOLD is visible on the page (Text Layer) or in Filename
        is_hold = self._detect_hold_fast(filename_only, blocks)
        
        if is_hold:
            # Append (HOLD) to remarks if not already there
            if remarks:
                if "(HOLD)" not in remarks.upper():
                    remarks = f"{remarks} (HOLD)"
            else:
                remarks = "(HOLD)"

        metadata = {
            "drawing_no": final_drawing_no,
            "revision_no": rev,
            "description": desc, 
            "drawing_type": "UNKNOWN",
            "date": date_str, 
            "quantity": 1,
            "remarks": remarks,
            "project_name": project_name
        }
        
        doc.close()
        return metadata

    def _detect_hold_fast(self, filename, blocks):
        """
        Fast detection of 'HOLD' using filename and extracted text blocks.
        Avoids OCR.
        """
        # 1. Check Filename
        if "HOLD" in filename.upper():
            return True
            
        # 2. Check Text Content (regex for whole word to avoid false positives)
        for b in blocks:
            text = b[4].upper()
            # Look for standalone HOLD or (HOLD)
            if re.search(r"\bHOLD\b", text): 
                return True
                
        return False

    def _detect_hold_watermark(self, page):
        """
        Legacy: Renders page to image and uses OCR to find 'HOLD' watermark.
        """
        return False # Disabled for performance

    def _extract_strict_data(self, blocks):
        """
        STRICT extraction from labeled fields ONLY.
        """
        data = {}
        
        # 1. DWG No.
        # Dump shows: Block 51: CONTRACT No.\nDWG No. (y=1665)
        #             Block 57: 24050\nE12 (y=1661) - Text is right next to it or aligned
        dwg_no = self._find_value_for_label(["DWG NO", "DRG NO", "DRAWING NO", "JOB NO"], blocks)
        if dwg_no:
            data["drawing_no"] = dwg_no

        # 2. DWG TITLE
        # Added "DESCRIPTION" as label (as per Image 1), but must be careful not to pick up Rev Table Desc.
        # We prioritize "DWG TITLE" / "TITLE" first.
        title = self._find_value_for_label(["DWG TITLE", "TITLE"], blocks, search_below=True)
        if not title:
            # Fallback: Check for "DESCRIPTION" in Title Block area (usually bottom right)
            # Logic: If we find "DESCRIPTION", we check if the value looks like a title (not a Rev Desc)
            title = self._find_value_for_label(["DESCRIPTION"], blocks, search_below=True)
        
        if title:
            # Clean title
            title = self._clean_title(title)
            data["description"] = title

        # 3. Revision Table
        # Search for blocks that contain revision data (Number + Date + Text)
        revisions = []
        for b in blocks:
            text = b[4].strip()
            # Try to parse lines individually first (Handles multiple revisions in one block)
            lines = text.split('\n')
            block_revs = []
            for line in lines:
                 # Skip short noise lines to save regex time
                 if len(line) < 3: continue
                 rev_entry = self._parse_revision_block(line)
                 if rev_entry:
                     block_revs.append(rev_entry)
            
            if block_revs:
                revisions.extend(block_revs)
            else:
                # Fallback: Try whole block parsed as one (Handles wrap-around descriptions)
                rev_entry = self._parse_revision_block(text)
                if rev_entry:
                    revisions.append(rev_entry)

        # Sort revisions to get the "latest"
        if revisions:
            # Sort by Rev No. assuming it can be converted to int, else str
            def sort_key(x):
                try:
                    return int(x['rev'])
                except:
                    # Handle 'A', 'B' etc
                    return ord(x['rev'][0]) if x['rev'] else 0
            
            revisions.sort(key=sort_key, reverse=True)
            
            # --- STRICT FILTERING RULES (User Request) ---
            # 1. Keep ONLY Rev A (Approval) and Rev 0 (Fabrication/Field Use)
            # 2. Reject mismatched rows
            filtered_revs = []
            for r in revisions:
                r_num = str(r['rev']).upper()
                r_desc = str(r['desc']).upper()
                
                keep = False
                if r_num == 'A':
                    if "APPROVAL" in r_desc:
                        keep = True
                elif r_num == '0':
                    if any(x in r_desc for x in ["FABRICATION", "FIELD USE", "CONSTRUCTION"]):
                        keep = True
                        
                if keep:
                    filtered_revs.append(r)
            
            revisions = filtered_revs
            
            if revisions:
                latest = revisions[0]
                data["revision_no"] = latest["rev"]
                data["date"] = latest["date"]
                data["remarks"] = latest["desc"]
        

        
        data["all_revisions"] = revisions
        return data

    def _parse_revision_block(self, text):
        """
        Tries to parse a text block as a revision row.
        Formats:
        - "1\n06/26/2025\nRevised As Noted"
        - "A 06/26/2025 For Approval"
        - "A 24 Mar 2025 For Approval"
        """
        # Normalize newlines to spaces for regex
        clean_text = text.replace('\n', ' ').strip()
        
        # Regex: Rev (1-3 chars), Space, Date (Flexible), Space, Desc
        # Date supports: 06/26/25, 06-26-2025, 24 Mar 2025, 24.03.25
        pattern = r'^([A-Z0-9]{1,3})\s+((?:\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})|(?:\d{1,2}\s+[a-zA-Z]{3}\s+\d{2,4})|(?:\d{2,4}-\d{2}-\d{2}))\s+(.+)$'
        
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            rev_no = match.group(1)
            date_str = match.group(2)
            desc = match.group(3).strip()
            
            if self._is_noise(desc): return None
            
            # Normalize Date
            norm_date = self._normalize_date(date_str)
            if not norm_date: norm_date = date_str # Fallback

            return {"rev": rev_no, "date": norm_date, "desc": desc}

        # Fallback for lines WITHOUT Revision Number (e.g., "06/26/2025 For Approval")
        # Regex: Start with Date, Space, Desc
        pattern_no_rev = r'^((?:\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})|(?:\d{1,2}\s+[a-zA-Z]{3}\s+\d{2,4})|(?:\d{2,4}-\d{2}-\d{2}))\s+(.+)$'
        match_no_rev = re.search(pattern_no_rev, clean_text, re.IGNORECASE)
        if match_no_rev:
            date_str = match_no_rev.group(1)
            desc = match_no_rev.group(2).strip()
            
            if self._is_noise(desc): return None
            
            # Normalize Date
            norm_date = self._normalize_date(date_str)
            if not norm_date: norm_date = date_str

            # Infer Rev
            rev_no = None
            if "APPROVAL" in desc.upper(): rev_no = "A"
            elif any(x in desc.upper() for x in ["FABRICATION", "FIELD USE", "CONSTRUCTION"]): rev_no = "0"
            
            if rev_no:
                return {"rev": rev_no, "date": norm_date, "desc": desc}
            else:
                return None

        # Fallback 2: Description THEN Date (e.g. "For Approval 11-04-2025")
        pattern_desc_date = r'^(.+)\s+((?:\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})|(?:\d{1,2}\s+[a-zA-Z]{3}\s+\d{2,4})|(?:\d{2,4}-\d{2}-\d{2}))$'
        match_desc_date = re.search(pattern_desc_date, clean_text, re.IGNORECASE)
        if match_desc_date:
            desc = match_desc_date.group(1).strip()
            date_str = match_desc_date.group(2)
            
            if self._is_noise(desc): return None
            
            # Normalize Date
            norm_date = self._normalize_date(date_str)
            if not norm_date: norm_date = date_str

            # Infer Rev
            rev_no = None
            if "APPROVAL" in desc.upper(): rev_no = "A"
            elif any(x in desc.upper() for x in ["FABRICATION", "FIELD USE", "CONSTRUCTION"]): rev_no = "0"
            
            if rev_no:
                return {"rev": rev_no, "date": norm_date, "desc": desc}

            # Filter noise
            desc_upper = desc.upper()
            if any(x in desc_upper for x in ["MATERIAL", "ANGLE", "HSS", "GRADE", "QTY", "TOTAL", "DWG TITLE", "CONTRACT", "DRAWN"]):
                return None
            if "REV." in desc_upper and "DATE" in desc_upper: # Header row
                return None
                
            return {
                "rev": rev_no,
                "date": date_str, 
                "desc": desc
            }
        return None

    def _find_value_for_label(self, labels, blocks, search_below=False):
        """
        Finds a block containing one of the labels, then looks for value.
        """
        for i, b in enumerate(blocks):
            text = b[4].strip()
            
            # Check if block contains label
            matched_label = None
            matched_line_idx = -1
            
            lines = text.split('\n')
            for li, line in enumerate(lines):
                 for label in labels:
                    if label in line.upper():
                        matched_label = label
                        matched_line_idx = li
                        break
                 if matched_label: break
            
            if matched_label:
                # 1. OPTION A: Check if value is in the SAME block line after the label
                label_line = lines[matched_line_idx]
                pattern = re.escape(matched_label) + r"[\.:]?\s*(.+)$"
                match = re.search(pattern, label_line, re.IGNORECASE)
                if match:
                    val = match.group(1).strip()
                    if self._is_valid_strict(val):
                         return val

                # 1. OPTION B: Check if value is in the NEXT line of the SAME block (Below, same object)
                # This handles cases where PDF groups "DATE DRAWN" and "10/16/2024" into one block
                if search_below and matched_line_idx + 1 < len(lines):
                    val = lines[matched_line_idx + 1].strip()
                    if self._is_valid_strict(val):
                        return val

                # 2. Check blocks nearby
                label_rect = b[:4]
                
                # Candidates
                for cb in blocks:
                    if cb == b: continue
                    
                    c_rect = cb[:4]
                    c_text = cb[4].strip()
                    if not c_text: continue
                    
                    # Horizontal Right: c_x > l_x, similar y
                    # For multi-line label blocks, extract the corresponding line from value block
                    if c_rect[0] > label_rect[0] - 10 and abs(c_rect[1] - label_rect[1]) < 20:
                         c_lines = c_text.split('\n')
                         
                         # Try to get the line at the same index as the matched label
                         if matched_line_idx < len(c_lines):
                             val = c_lines[matched_line_idx].strip()
                             if self._is_valid_strict(val):
                                 return val
                         
                         # Fallback: try all lines in the value block
                         for c_line in c_lines:
                             val = c_line.strip()
                             if self._is_valid_strict(val):
                                 return val
                             
                    # Vertical Below: similar x, c_y > l_y
                    # Vertical Below: similar x, c_y > l_y
                    # Relaxed X tolerance to 200 (approx 2.5 inches) as labels can be small "DATE" and value "10/16/2024" wider
                    # Added Y limit to avoid picking up footer noise far below
                    vertical_dist = c_rect[1] - label_rect[1]
                    if search_below and vertical_dist > 0 and vertical_dist < 150 and abs(c_rect[0] - label_rect[0]) < 200:
                         # For title, we want the full text, cleaned
                         val = c_text.replace('\n', ' ').strip()
                         # Clean the title
                         val = self._clean_title(val)
                         if self._is_valid_strict(val):
                             return val
                    
        return None

    def _is_valid_strict(self, val):
        if not val or len(val) < 2: return False
        val = val.strip()
        
        # Reject obvious non-values
        if val in ["--", "..."]: return False
        
        val_up = val.upper()
        
        # Reject label-like text (exact matches)
        if any(val_up == x for x in ["PROJECT", "TITLE", "DWG", "REV", "DATE", "SCALE", "CHECKED", "DRAWN", "DGSTS", "CONTRACT", "LOCATION", "CONTRACTOR"]): return False
        
        # Reject if contains label keywords (but not as part of actual content)
        if any(x in val_up for x in ["DWG NO", "DRG NO", "CONTRACT NO", "REV.", "DATE DRAWN", "PLOT DATE", "PROJECT NAME"]): return False
        
        # Specific exclusions for initials or contractor names found in headers
        if val == "24050": return False  # Project number
        if val_up in ["HSR", "SMS", "DRK", "ABJ", "MRP", "SMS", "HSR"]: return False  # Initials
        if "BUILDING ENVELOPE SYSTEMS" in val_up: return False # Contractor Name
        
        return True
    
    def _clean_title(self, text):
        # 1. Basic Cleaning
        text = text.replace("WELDS", "").replace("E70XX", "")
        text = re.sub(r"DWG\s*TITLE", "", text, flags=re.IGNORECASE)
        clean = text.strip()

        # 2. Remove leading quantity/number prefixes
        clean = re.sub(r'^(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|\d+)\s*[-–]\s*', '', clean, flags=re.IGNORECASE)

        # 3. Remove trailing drawing number
        clean = re.sub(r'\s*[-–]\s*[A-Z0-9]+$', '', clean)

        return clean.strip()





    def _extract_from_blocks(self, blocks, keys, field_type):
        for i, b in enumerate(blocks):
            block_text = b[4].strip()
            
            # Check keys
            for key in keys:
                if key.upper() in block_text.upper():
                    # Strategy 1: Key and Value in same block line?
                    # e.g. "DWG NO: 123"
                    pattern = re.escape(key) + r"[:\.]?\s*([A-Za-z0-9\-\/]+)"
                    match = re.search(pattern, block_text, re.IGNORECASE)
                    if match:
                        val = match.group(1).strip()
                        if self._is_valid_value(val, field_type):
                            return val
                            
                    # Strategy 2: Value in next block?
                    if i + 1 < len(blocks):
                        next_block_text = blocks[i+1][4].strip()
                        
                        # Sub-strategy: Line Mapping
                        # Block A: "CONTRACT No.\nDWG No."
                        # Block B: "24050\n2AL46"
                        # We want to match the line index of "DWG No." to the line index in Block B.
                        key_lines = block_text.split('\n')
                        val_lines = next_block_text.split('\n')
                        
                        # Find which line index contains the key
                        key_idx = -1
                        for idx, line in enumerate(key_lines):
                            if key.upper() in line.upper():
                                key_idx = idx
                                break
                        
                        if key_idx != -1 and key_idx < len(val_lines):
                            candidate = val_lines[key_idx].strip()
                            if self._is_valid_value(candidate, field_type):
                                return candidate
                                
                        # Fallback: Just check the whole text if not multiline structured
                        if self._is_valid_value(next_block_text, field_type):
                             return next_block_text
                             
        return None

    def _extract_title_block(self, blocks):
        # Look for DWG TITLE
        start_idx = -1
        for i, b in enumerate(blocks):
            if "DWG TITLE" in b[4].upper():
                start_idx = i
                break
        
        if start_idx == -1: return ""
        
        # Look ahead up to 6 blocks
        for offset in range(1, 7):
            if start_idx + offset >= len(blocks): break
            
            text = blocks[start_idx + offset][4].strip()
            # Skip noise
            if not text: continue
            if "WELDS" in text.upper(): continue
            if "E70XX" in text.upper(): continue
            if "BILL OF" in text.upper(): continue
            if "QTY" in text.upper(): continue
            if "DGSTS" in text.upper(): continue
            if "CHECKED" in text.upper(): continue
            if "DRAWN" in text.upper(): continue
            
            # Found a candidate?
            clean = self._clean_title(text)
            # Found a candidate?
            clean = self._clean_title(text)
            if clean:
                # Check for Revision Block data which often gets picked up
                # e.g. "0\n04/18/2025\nFor Construction"
                if re.search(r"\d{2}[/\.-]\d{2}[/\.-]\d{4}", text): continue # Has date
                if "FOR CONSTRUCTION" in text.upper(): continue
                if "FOR APPROVAL" in text.upper(): continue
                if "REVISED AS NOTED" in text.upper(): continue
                
                # Exclude notes that might mistakenly be picked up
                # e.g. "1.U.N.O ALL WINDOW LOCATIONS..."
                if "U.N.O" in text.upper(): continue 
                if re.match(r"^\d+\.", text): continue # Starts with "1." or similar
                if "ELEVATIONS ARE" in text.upper(): continue
                if "VERIFIED WITH" in text.upper(): continue
                if "MEASURED PER" in text.upper(): continue
                if "REFER " in text.upper(): continue
                if "STEEL" in text.upper() and "GRADE" in text.upper(): continue
                if text.strip().upper() == "COLUMN": continue
                if text.strip().upper() == "PLATE": continue
                if "REV" in text.upper() and "NO" in text.upper(): continue # REV NO.
                if "DRG" in text.upper() and "NO" in text.upper(): continue # DRG NO.
                
                # Heuristic: Titles are rarely very long notes.
                # If text is > 100 chars or > 3 lines, it's likely a note.
                if len(text) > 100: continue
                if text.count('\n') > 3: continue

                # Check vertical proximity if possible
                # The 'blocks' structure is (x0, y0, x1, y1, "text", block_no, block_type)
                # Ensure the candidate is physically below the title label
                title_block = blocks[start_idx]
                candidate_block = blocks[start_idx + offset]
                
                # title_block[3] is bottom-y of title label
                # candidate_block[1] is top-y of candidate text
                # We expect candidate to be below title
                if candidate_block[1] > title_block[3] - 5: # Allow slight overlap/tolerance
                     return clean
                
                # If it's way above or simply elsewhere, maybe skipping it is safer?
                # But for now, let's trust the block order + exclusions slightly more.
                return clean
                
        return ""

    def _clean_title(self, text):
        # 1. Basic Cleaning
        text = text.replace("WELDS", "").replace("E70XX", "")
        text = re.sub(r"DWG\s*TITLE", "", text, flags=re.IGNORECASE)
        clean = text.strip()

        # 2. Remove leading quantity/number prefixes
        # e.g. "ONE - ", "2 - ", "10 - "
        # Pattern: Start of string, number word or digits, optional space, hyphen, optional space
        clean = re.sub(r'^(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|\d+)\s*[-–]\s*', '', clean, flags=re.IGNORECASE)

        # 3. Remove trailing drawing number
        # e.g. " - 1B12", " - 2AL46"
        # Pattern: Hyphen, optional space, alphanumeric (usually uppercase + nums), end of string
        # Heuristic: The drawing number usually contains at least one digit or is shorter than the title
        clean = re.sub(r'\s*[-–]\s*[A-Z0-9]+$', '', clean)

        return clean.strip()

    def _is_valid_value(self, val, field_type):
        if not val: return False
        val = val.strip()
        if field_type == "Drawing-No":
            if re.match(r"^\(?\d{3}\)?\s*\d{3}-\d{4}", val): return False # (508) ...
            if re.match(r"^\d{3}-\d{4}$", val): return False # 381-0429
            if len(val) < 2: return False
            
            # Strict Exclusions for BOM headers (Noise from Shop Drawings)
            noise_words = ["FACE", "SHAPE", "TOTAL", "REMARKS", "ADV", "MILL", "SURFACE", "QTY", "DESCRIPTION", "LENGTH", "WEIGHT", "PROJECT NAME", "PROJECT"]
            if val.upper() in noise_words: return False

        if "PHONE" in val.upper(): return False
        if "REV" in val.upper() and "NO" in val.upper(): return False
        if "DRG" in val.upper() and "NO" in val.upper(): return False
        if "SHEET" in val.upper() and "NO" in val.upper(): return False
        if val == "24050": return False # Hardcode exclude known project no if ambiguous
        if field_type == "Drawing-No": # This check is needed because the previous `return True` was removed
            return True
        if field_type == "Rev":
            if len(val) > 3: return False 
            if val.upper() in ["DATE", "DESCRIPTION", "REV."]: return False
            # Reject Part Numbers (e.g. 1C8) mistakenly picked up as Rev
            if len(val) > 1 and any(c.isalpha() for c in val) and any(c.isdigit() for c in val): return False
            return True
        return True

    def _regex_drawing_no(self, text):
        match = re.search(r"DWG\s*No\.?\s*([A-Za-z0-9\-\/]+)", text, re.IGNORECASE)
        if match: return match.group(1).strip()
        return None

    def _extract_date(self, blocks):
        # 1. Try finding DATE DRAWN using spatial logic (Search Below = True)
        # This handles cases where "DATE DRAWN" is a header and the value is physically under it
        date_text = self._find_value_for_label(["DATE DRAWN", "DATE:", "DATE", "PLOT DATE"], blocks, search_below=True)
        if date_text:
             # Normalize valid date found spatially
             norm = self._normalize_date(date_text)
             # Additional check: ensure normalization returned a date and not just empty string
             # and check if it returned original text which might be garbage
             if norm and (len(norm) == 10 or "-" in norm): # Simple validity check
                 return norm

        # 2. Fallback: standard regex scan (unchanged)
        for b in blocks:
            # Regex to catch DD-MM-YYYY, MM/DD/YYYY, YYYY-MM-DD
            # Matches: 11-04-2025, 11/04/2025, 2025-11-04
            match = re.search(r"(\d{2,4}[/\.-]\d{1,2}[/\.-]\d{2,4})", b[4])
            if match: 
                 # Validate it's not a phone number (simple len check + normalize)
                 candidate = match.group(1)
                 norm = self._normalize_date(candidate)
                 if norm: return norm
            
        return datetime.now().strftime("%d-%m-%Y")

    def _normalize_date(self, date_str):
        if not date_str: return ""
        date_str = date_str.strip()
        
        try:
            # 1. MM/DD/YYYY or DD/MM/YYYY with slashes
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                     # Assume input is MM/DD/YYYY for US context, but code before swapped to parts[1]-parts[0] (DD-MM)
                     # Let's verify standard: usually 06/26/2025 -> 2025-06-26 or 26-06-2025?
                     # Previous code was swapping 0 and 1.
                     return f"{parts[1]}-{parts[0]}-{parts[2]}"
            
            # 2. DD-MM-YYYY or MM-DD-YYYY or YYYY-MM-DD
            if '-' in date_str:
                # Check if it's already YYYY-MM-DD
                if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                    return date_str
                # Check for DD-MM-YYYY (11-04-2025)
                parts = date_str.split('-')
                if len(parts) == 3:
                     # If first part is day (or month) and last is year
                     if len(parts[2]) == 4:
                         return date_str # Keep as is (11-04-2025) which Excel logic handles via 'val' direct write
            
            # 3. DD Mon YYYY or Mon DD YYYY
            # Clean spaces
            date_str = re.sub(r'\s+', ' ', date_str) 
            match = re.search(r'(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})', date_str) # 24 Mar 2025
            if match:
                 # Convert to YYYY-MM-DD
                 d, m_str, y = match.groups()
                 try:
                     m = datetime.strptime(m_str, "%b").month
                     return f"{y}-{m:02d}-{int(d):02d}"
                 except: pass

            return date_str
        except:
            return date_str

    def _extract_remarks(self, blocks, rev_no):
        # Strategy: Look for block starting with Rev No, then find date, then description
        rev_str = str(rev_no).strip()
        for b in blocks:
            text = b[4].strip()
            # If the block starts with the rev number (e.g. "1\n..." or "1 ...")
            if text.startswith(rev_str):
                # Check if this block contains a date
                date_match = re.search(r"(\d{2}[/\.-]\d{2}[/\.-]\d{4})", text)
                if date_match:
                    # The remark is likely after the date (or on next line)
                    # Example: "1\n06/26/2025\nRevised As Noted"
                    # Split by the date string
                    parts = text.split(date_match.group(0))
                    if len(parts) > 1:
                        remark_candidate = parts[1].strip()
                        # Clean up
                        return remark_candidate if remark_candidate else "For Fabrication"
        
        # Fallback: Look for lines in any block (old method)
        for b in blocks:
            text = b[4].strip()
            lines = text.split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 3:
                    if parts[0] == rev_str:
                         if re.match(r"\d{2}[/\.-]\d{2}[/\.-]\d{4}", parts[1]):
                             return " ".join(parts[2:])
        return "For Fabrication"

    def _extract_project_name(self, blocks):
        # Look for "PROJECT NAME" block
        start_idx = -1
        for i, b in enumerate(blocks):
            if "PROJECT NAME" in b[4].upper():
                start_idx = i
                break
        

        if start_idx != -1:
            # Look ahead for a valid project name
            # Typically 1-3 blocks after
            for offset in range(1, 4):
                 if start_idx + offset >= len(blocks): break
                 text = blocks[start_idx + offset][4].strip()
                 if not text: continue
                 if "LOCATION" in text.upper(): break # Went too far
                 if "REV." in text.upper() and "DATE" in text.upper(): continue # Skip headers
                 
                 # Heuristic: Uppercase, length > 5
                 if len(text) > 5 and not text[0].isdigit():
                     return text.replace('\n', ' ').strip()
        return "Project"

    KEYWORDS = {
        "transmittal_no": ["TRANSMITTAL", "TRANSMITTAL NO"],
        "date": ["DT.", "DATE"],
        "sheet_no": ["SHEET NO", "SHEET NO."],
        "drawing_title": ["DRAWING TITLE", "TITLE"],
        "revision": ["REVISION MARK", "REV"],
        "remarks": ["REMARKS"],
        "category": ["PART DRAWINGS", "SHOP DRAWINGS", "ERECTION DRAWINGS"]
    }

    def detect_and_extract_transmittal(self, file_path: str):
        """
        Robust Industry-Grade Transmittal Extraction.
        Step 1: Normalize Text (Critical)
        Step 2: Keyword Dictionary
        Step 3: Header-level extraction
        Step 4: Table detection without trusting borders
        Step 5: Smart row parsing
        Step 6: Fallback logic
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                if not pdf.pages: return None
                page = pdf.pages[0]
                
                # Step 1: Normalize Text
                lines = self._normalize_text_lines(page)
                if not lines: return None
                
                # Check for Transmittal intent
                full_text_upper = "\n".join(lines).upper()
                is_transmittal = "TRANSMITTAL" in full_text_upper
                
                # Step 3: Header-level extraction (Metadata)
                metadata = self._extract_header_metadata(lines)
                
                # Step 4.0: TABLE EXTRACTION (New Strategy)
                # Try to extract actual tables first as this handles column separation much better
                # than regex on text lines, specifically for "Sent for Rev A | Sent for Rev 0" layouts.
                extracted_tables = page.extract_tables()
                if extracted_tables:
                    # Flatten tables if multiple? Usually main table is what we want.
                    # We look for the table that has specific headers.
                    for table in extracted_tables:
                        # Try to extract from this table
                        table_drawings = self._extract_drawings_from_table(table)
                        if len(table_drawings) > 0:
                            return {
                                "is_transmittal": True,
                                "metadata": metadata,
                                "drawings": table_drawings
                            }

                # Step 4.1: Fallback to Text Line Analysis (Original Strategy)
                table_start_idx = -1
                for i, line in enumerate(lines):
                    u_line = line.upper()
                    # Find header line: SHEET NO ... DRAWING TITLE ... REVISION
                    if ("SHEET NO" in u_line or "DWG NO" in u_line) and \
                       ("TITLE" in u_line or "DESCRIPTION" in u_line):
                        table_start_idx = i
                        break
                
                drawings = []
                
                if table_start_idx != -1:
                    # Strict parsing below header
                    drawings = self._extract_transmittal_rows(lines[table_start_idx+1:], strict=True)
                elif is_transmittal:
                    # Step 6: Fallback logic (try line-by-line regex on whole doc)
                    drawings = self._extract_transmittal_rows(lines, strict=False)
                
                # If we found valid drawings or it's a strongly identified transmittal
                if (drawings and len(drawings) > 0) or (is_transmittal and len(drawings) > 0):
                    return {
                        "is_transmittal": True,
                        "metadata": metadata,
                        "drawings": drawings
                    }
                    
        except Exception as e:
            print(f"Error detecting transmittal: {e}")
            return None
        
        return None

    def _normalize_text_lines(self, page):
        """Step 1: Convert PDF -> plain text line by line, remove extra spaces"""
        text = page.extract_text(layout=True)
        if not text: return []
        
        normalized_lines = []
        for line in text.split('\n'):
            clean = line.strip()
            if clean:
                # Replace multiple internal spaces with single space to normalize
                clean = re.sub(r'\s+', ' ', clean)
                normalized_lines.append(clean)
        return normalized_lines

    def _extract_header_metadata(self, lines):
        """Step 3: Header-level extraction"""
        metadata = {}
        # Scan first few lines
        for line in lines[:20]:
            u_line = line.upper()
            
            # Transmittal No
            if "TRANSMITTAL" in u_line:
                m = re.search(r"TRANSMITTAL\s*(?:NO\.?|#)?\s*([A-Z0-9\-]+)", u_line)
                if m: metadata["transmittal_no"] = m.group(1)
            
            # Date
            if "DT." in u_line or "DATE" in u_line:
                m = re.search(r"(?:DT\.|DATE)[:\.]?\s*(\d{2}[/\.-]\d{2}[/\.-]\d{2,4})", u_line)
                if m: metadata["date"] = self._normalize_date(m.group(1))
            
            # Project No
            if "PROJECT NO" in u_line:
                m = re.search(r"PROJECT NO[:\.]?\s*([A-Z0-9\-]+)", u_line)
                if m: metadata["project_no"] = m.group(1)

        return metadata

    def _extract_transmittal_rows(self, lines, strict=False):
        """
        Step 5: Smart row parsing (Right-to-Left Strategy)
        Robustly handles variable title lengths by anchoring on Date/Rev at the end.
        """
        drawings = []
        
        for line in lines:
            u_line = line.upper()
            
            # Stop markers (Footer)
            # Check if line STARTS with footer kws to avoid false positives in titles
            if any(u_line.startswith(x) for x in ["PREPARED BY", "SENT BY", "DRAWN BY", "CHECKED BY", "APPROVED BY", "PAGE"]):
                if strict: break # Stop completely in strict mode
                continue       # Skip line in fallback mode
                
            # Skip Headers/Section Titles if encountered in rows
            # Strict check: Must match the headers exactly or be in the exclusion list
            if "SHEET NO" in u_line and "REV" in u_line: continue
            if u_line in ["SHOP DRAWINGS", "PART DRAWINGS", "ERECTION DRAWINGS", "E SHEET", "DRAWING LOG"]: continue
            
            # 1. Parse content into: [SL] [SHEET] [TAIL]
            # Tail contains: TITLE + REV + DATE + REMARKS
            # Match optional Sl No, Mandatory Sheet, Mandatory Tail
            # We use atomic groups or strict matching to ensure Sl is just digits
            head_match = re.match(r"^(?:(?P<sl>\d+)\s+)?(?P<sheet>[^\s]+)\s+(?P<tail>.+)$", line)
            
            if head_match:
                sheet = head_match.group("sheet").strip()
                tail = head_match.group("tail").strip()
                
                # Check for footer keywords in Sheet No (e.g. if regex matched "DRAWN" as sheet)
                if sheet.upper() in ["DRAWN", "CHECKED", "APPROVED", "MYCOMPANY", "BY", "PREPARED", "SENT", "DATE"]: continue
                
                # 2. Parse TAIL from Right-to-Left
                # Pattern: (Rev) (Date) (Remarks optional) $
                # Rev: 1-3 alphanum chars. Date: DD/MM/YYYY etc.
                # Update: Date regex widened to match fallback logic (24 Mar 2025, YYYY-MM-DD)
                
                # Regex part for date: (\d{2,4}[/\.-]\d{1,2}[/\.-]\d{2,4}|\d{1,2}\s+[a-zA-Z]{3}\s+\d{2,4})
                tail_pattern = r"\s+(?P<rev>[A-Z0-9]{1,3})\s+(?P<date>\d{2,4}[/\.-]\d{1,2}[/\.-]\d{2,4}|\d{1,2}\s+[a-zA-Z]{3}\s+\d{2,4})(?:\s+(?P<remarks>.*))?$"
                
                tail_match = re.search(tail_pattern, tail)
                if tail_match:
                    rev = tail_match.group("rev").strip()
                    date_str = tail_match.group("date").strip()
                    remarks = tail_match.group("remarks").strip() if tail_match.group("remarks") else ""
                    
                    # Title is everything before the match
                    # tail_match.start() gives index where Rev starts (including the leading space \s+)
                    title = tail[:tail_match.start()].strip()
                    
                    # Validation: "If a value is missing, leave the Excel cell blank."
                    # If title is empty, it remains empty ""
                    
                    if "DATE" in title.upper(): continue # Header bleed (e.g. "Drawing Title Revision Date")
                    
                    drawings.append({
                        "drawing_no": sheet,
                        "description": title,
                        "revision_no": rev,
                        "date": self._normalize_date(date_str),
                        "remarks": remarks # No default "For Fabrication"
                    })
                else:
                    # STRICT MODE requirement: "If a value is missing... do NOT guess values."
                    # If we can't find a Date/Rev structure, we cannot reliability separate Title from the rest.
                    # e.g. "5 COLUMN" -> Missing Rev/Date? 
                    # We skip it to avoid guessing.
                    pass
        
        return drawings
    
    def _extract_drawings_from_table(self, table):
        """
        Extracts drawing data from transmittal table.
        Expected columns: Sl. No., Sheet No., Drawing Title, Revision Mark, Date, Remarks
        """
        if len(table) < 2:
            return []
        
        # Identify header row and column indices
        header_row = table[0]
        col_indices = self._identify_columns(header_row, table_data=table)
        
        if not col_indices:
            return []
        
        drawings = []
        
        # Process data rows (skip header and section headers)
        for row_idx, row in enumerate(table[1:], start=1):
            if not row or len(row) < 3:
                continue
            
            # Skip section headers (e.g., "SHOP DRAWINGS", "E SHEET")
            first_cell = str(row[0] or "").strip().upper()
            if not first_cell or first_cell in ["SHOP DRAWINGS", "E SHEET", "PART DRAWINGS", "ERECTION"]:
                continue
            
            # Skip if first cell is not a number (serial number)
            if not first_cell.isdigit():
                continue
            
            # Extract drawing data
            drawing = self._extract_row_data(row, col_indices)
            if drawing and drawing.get("drawing_no"):
                drawings.append(drawing)
        
        return drawings
    
    def _identify_columns(self, header_row, table_data=None):
        """
        Identifies column indices from header row.
        Returns dict mapping field names to column indices.
        Uses multiple strategies to handle various table formats.
        Validates columns by checking actual data to avoid mapping material/project columns as Sheet No.
        """
        col_map = {}
        
        # Strategy 1: Try to match header text
        for idx, cell in enumerate(header_row):
            if not cell:
                continue
            
            cell_upper = str(cell).upper().strip()
            
            # Sheet No / Drawing No
            if not col_map.get("sheet_no"):
                if any(pattern in cell_upper for pattern in ["SHEET NO", "SHEET  NO", "DWG NO", "DRG NO", "DRAWING NO"]):
                    col_map["sheet_no"] = idx
            
            # Drawing Title
            if not col_map.get("title"):
                if any(pattern in cell_upper for pattern in ["DRAWING TITLE", "DWG TITLE", "TITLE", "DESCRIPTION"]):
                    col_map["title"] = idx
            
            # Revision
            if not col_map.get("revision"):
                if any(pattern in cell_upper for pattern in ["REVISION MARK", "REVISION", "REV MARK", "REV."]):
                    # Make sure it's not "REVISED" or similar
                    if "REVISED" not in cell_upper:
                        col_map["revision"] = idx
            
            # Date
            if not col_map.get("date"):
                if "DATE" in cell_upper and "UPDATE" not in cell_upper:
                    col_map["date"] = idx
            
            # Remarks
            if not col_map.get("remarks"):
                if any(pattern in cell_upper for pattern in ["REMARK", "STATUS", "DESCRIPTION"]):
                    col_map["remarks"] = idx

            # Rev A / Rev 0 Dates (Special Layout)
            if not col_map.get("date_rev_a"):
                if "REV A" in cell_upper or ("SENT FOR" in cell_upper and "REV A" in cell_upper):
                    col_map["date_rev_a"] = idx
            
            if not col_map.get("date_rev_0"):
                if "REV 0" in cell_upper or ("SENT FOR" in cell_upper and "REV 0" in cell_upper):
                    col_map["date_rev_0"] = idx
        
        # Strategy 2: Validate the identified columns by checking actual data
        if "sheet_no" in col_map and table_data and len(table_data) > 1:
            sheet_col_idx = col_map["sheet_no"]
            
            # print(f"[DEBUG] Initial sheet_no column index: {sheet_col_idx}") # Reduced noise
            
            # Check first few data rows to see if this column contains drawing numbers
            # or if it contains material names/project names
            material_keywords = ["A36", "HSS", "PLATE", "ANGLE", "BEAM", "CHANNEL", "TUBE", "UNO", "GALV"]
            project_keywords = ["GSC", "JUNIPER", "RBP", "PHASE", "PROJECT"]
            
            is_valid_sheet_col = True
            sample_rows = table_data[1:min(6, len(table_data))]  # Check first 5 data rows
            
            print(f"[DEBUG] Checking {len(sample_rows)} sample rows for validation...")
            
            for row_idx, row in enumerate(sample_rows, 1):
                if len(row) > sheet_col_idx:
                    cell_value = str(row[sheet_col_idx] or "").strip().upper()
                    
                    print(f"[DEBUG] Row {row_idx}, Column {sheet_col_idx}: '{cell_value}'")
                    
                    # Skip empty cells and serial numbers
                    if not cell_value or cell_value.isdigit():
                        print(f"[DEBUG]   -> Skipped (empty or digit)")
                        continue
                    
                    # Check if this looks like a material name
                    if any(keyword in cell_value for keyword in material_keywords):
                        print(f"[DEBUG]   -> INVALID! Contains material keyword")
                        is_valid_sheet_col = False
                        break
                    
                    # Check if this looks like a project name (long text with spaces)
                    if any(keyword in cell_value for keyword in project_keywords):
                        print(f"[DEBUG]   -> INVALID! Contains project keyword")
                        is_valid_sheet_col = False
                        break
                    
                    # Check if it's just a material type
                    if cell_value in ["ANGLE", "PLATE", "BEAM", "CHANNEL", "HSS", "TUBE"]:
                        print(f"[DEBUG]   -> INVALID! Is material type")
                        is_valid_sheet_col = False
                        break
                    
                    print(f"[DEBUG]   -> Valid")
            
            # If the identified sheet_no column contains materials/projects, try next column
            if not is_valid_sheet_col and sheet_col_idx + 1 < len(header_row):
                print(f"[DEBUG] Column {sheet_col_idx} is INVALID, trying next column {sheet_col_idx + 1}")
                # Try the next column
                col_map["sheet_no"] = sheet_col_idx + 1
                print(f"[DEBUG] New sheet_no column index: {col_map['sheet_no']}")
            else:
                print(f"[DEBUG] Column {sheet_col_idx} validation result: {'VALID' if is_valid_sheet_col else 'INVALID (but no next column)'}")
        
        # Strategy 3: If we found sheet_no and title, we're good
        if "sheet_no" in col_map and "title" in col_map:
             # Check if we have date info (either standard or split)
             if "date" in col_map or "date_rev_a" in col_map or "date_rev_0" in col_map:
                 return col_map

        
        # Strategy 4: Positional fallback for standard transmittal format
        # Typical format: Sl. No. | Sheet No. | Drawing Title | Revision | Date | Remarks
        # Try to detect this pattern
        if len(header_row) >= 5:
            # Check if first column looks like serial number
            first_cell = str(header_row[0] or "").upper().strip()
            if "SL" in first_cell or "NO" in first_cell or "SR" in first_cell:
                # Assume standard format
                col_map = {
                    "sheet_no": 1,  # Second column
                    "title": 2,      # Third column
                    "revision": 3,   # Fourth column (if exists)
                    "date": 4,       # Fifth column (if exists)
                    "remarks": 5 if len(header_row) > 5 else None  # Sixth column (if exists)
                }
                # Remove None values
                col_map = {k: v for k, v in col_map.items() if v is not None}
                return col_map
        
        # Strategy 4: If we still don't have sheet_no and title, return None
        if "sheet_no" not in col_map or "title" not in col_map:
            return None
        
        return col_map
    
    def _extract_row_data(self, row, col_indices):
        """
        Extracts drawing data from a single table row.
        Validates data to ensure correct extraction.
        """
        drawing = {}
        
        # Sheet No (Drawing No)
        if "sheet_no" in col_indices:
            sheet_no = str(row[col_indices["sheet_no"]] or "").strip()
            
            # Validation: Drawing number should NOT be a date
            # Reject if it looks like a date (DD/MM/YYYY, MM/DD/YYYY, etc.)
            if re.match(r'^\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}$', sheet_no):
                # This is a date, not a drawing number - column mapping is wrong!
                return None
            
            # Validation: Drawing number should not be empty
            if not sheet_no:
                return None
                
            drawing["drawing_no"] = sheet_no
        else:
            return None  # Must have drawing number
        
        # Drawing Title (Description)
        if "title" in col_indices:
            title = str(row[col_indices["title"]] or "").strip()
            drawing["description"] = title
        else:
            drawing["description"] = ""
        
        # Remarks (Fetch early for logic)
        remarks = "For Fabrication"
        if "remarks" in col_indices:
            val = str(row[col_indices["remarks"]] or "").strip()
            if val: remarks = val
        drawing["remarks"] = remarks

        # Revision & Date Logic
        # CASE A: Split Rev Columns (Rev A / Rev 0)
        if "date_rev_a" in col_indices or "date_rev_0" in col_indices:
             date_a = ""
             date_0 = ""
             
             if "date_rev_a" in col_indices:
                 val = str(row[col_indices["date_rev_a"]] or "").strip()
                 if len(val) > 6 and any(c.isdigit() for c in val):
                     date_a = self._normalize_date(val)
            
             if "date_rev_0" in col_indices:
                 val = str(row[col_indices["date_rev_0"]] or "").strip()
                 if len(val) > 6 and any(c.isdigit() for c in val):
                     date_0 = self._normalize_date(val)
            
             if date_a:
                 drawing["revision_no"] = "A"
                 drawing["date"] = date_a
             elif date_0:
                 drawing["revision_no"] = "0"
                 drawing["date"] = date_0
             else:
                 # Both dates empty - Infer from Remarks
                 if "APPROVAL" in remarks.upper():
                      drawing["revision_no"] = "A"
                      drawing["date"] = "" # Allow inference
                 else:
                      drawing["revision_no"] = "0"
                      drawing["date"] = "" # Allow inference

        # CASE B: Standard Rev & Date Columns
        else:
            if "revision" in col_indices:
                rev = str(row[col_indices["revision"]] or "0").strip()
                drawing["revision_no"] = rev if rev else "0"
            else:
                drawing["revision_no"] = "0"
            
            if "date" in col_indices:
                date_str = str(row[col_indices["date"]] or "").strip()
                drawing["date"] = self._normalize_date(date_str) if date_str else datetime.now().strftime("%d-%m-%Y")
            else:
                drawing["date"] = datetime.now().strftime("%d-%m-%Y")
        

        
        # Default values
        drawing["drawing_type"] = "UNKNOWN"
        drawing["quantity"] = 1
        drawing["project_name"] = "Project"
        
        return drawing

    def _is_noise(self, text):
        t = text.upper()
        # Reject Title Block labels and other noise
        noise = ["DATE", "DRAWN", "CHECKED", "SCALE", "JOB", "CONTRACT", "DRG NO", "SHEET", "PROJECT", "DWG TITLE", "REV.", "REVISION", "DESCRIPTION", "TOTAL", "QTY", "MATERIAL"]
        # Check if text IS strictly a noise word or starts with noise word + colon
        # e.g. "DATE:"
        for n in noise:
            if t == n: return True
            if t.startswith(n + ":") or t.startswith(n + " :"): return True
            if t.startswith(n + "."): return True
        return False
