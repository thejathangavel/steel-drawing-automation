import re
import pdfplumber
import ezdxf
import os
from datetime import datetime
from typing import Dict, Any, Optional

from .extraction_parser import PDFParser

class ExtractionService:
    def __init__(self):
        self.parser = PDFParser()

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                # Use the new robust block-based parser
                return self.parser.extract_metadata(file_path)
            elif file_ext == '.dxf':
                 # Keep legacy DXF logic if needed, or implement DXF parser later
                 # For now, return None or implement simple text extraction if critical
                 # The user only cares about PDF right now.
                 return None
            else:
                print(f"Unsupported file type: {file_ext}")
                return None

        except Exception as e:
            print(f"Error extracting {file_path}: {e}")
            return None

    def _extract_dxf_text(self, file_path: str) -> str:
        # Retention of DXF helper just in case, though unused by PDF path
        text_content = []
        try:
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            for entity in msp.query('TEXT MTEXT INSERT'):
                if entity.dxftype() == 'INSERT':
                    if entity.attribs:
                        for attrib in entity.attribs:
                             text_content.append(attrib.dxf.text)
                elif hasattr(entity.dxf, 'text'):
                    text_content.append(entity.dxf.text)
        except Exception as e:
            print(f"DXF Read Error {file_path}: {e}")
        return "\n".join(text_content)
