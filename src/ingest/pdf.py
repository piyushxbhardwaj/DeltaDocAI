import re
import fitz  # PyMuPDF
import pdfplumber
import io
from typing import Any, List, Union
from src.ingest.base import BaseAdapter
from src.ingest.canonical import CanonicalObject, ObjectType
from src.observability.logger import logger

TAG_PATTERNS = [
    re.compile(r'\b\d{2}-[A-Z]{2,4}-\d{3,5}[A-Z]?\b'),  # e.g., 26-PIT-9055, 10-V-101
    re.compile(r'\b[VCPET]-\d{3,4}[A-Z]?\b'),           # e.g., V-101, C-201, P-301
    re.compile(r'\b[A-Z]{2,4}-\d{3,5}\b'),              # e.g., PIT-9055, XV-1001
]

def classify_object_type(text: str, tag: str | None) -> ObjectType:
    """Classify object type based on text structure and tag."""
    text_upper = text.upper()
    if tag:
        if any(v in tag for v in ["PIT", "TIT", "FIT", "LIT", "PT", "TT", "FT", "LT", "PI", "TI"]):
            return "Instrument"
        if any(v in tag for v in ["V-", "XV", "HV", "PSV", "CV", "VALVE"]):
            return "Valve"
        if any(v in tag for v in ["C-", "P-", "E-", "T-", "K-", "COMPRESSOR", "PUMP", "VESSEL", "TANK"]):
            return "Equipment"
    
    if "NOTES:" in text_upper or "GENERAL NOTES" in text_upper:
        return "Notes"
    if "TITLE" in text_upper or "DRAWING NO" in text_upper or "REVISION" in text_upper or "PROJECT:" in text_upper:
        return "Title Block"
    if re.search(r'\b\d+(\.\d+)?\s*(mm|cm|m|in|ft|")\b', text, re.IGNORECASE) or re.search(r'^\d+\.?\d*$', text):
        return "Dimension"
    if "VALVE" in text_upper:
        return "Valve"
    if "INSTRUMENT" in text_upper or "TRANSMITTER" in text_upper or "GAUGE" in text_upper:
        return "Instrument"
    if "PIPE" in text_upper or "LINE" in text_upper or re.search(r'\b\d+"-[A-Z]+-\d+\b', text):
        return "Pipeline"
    
    return "Text"

def extract_tag(text: str) -> str | None:
    """Extract engineering tag from string text."""
    for pat in TAG_PATTERNS:
        match = pat.search(text)
        if match:
            return match.group(0)
    return None

class NativePDFAdapter(BaseAdapter):
    """Adapter for native digital engineering PDFs."""

    async def load(self, source: Union[bytes, str]) -> dict:
        if isinstance(source, str):
            with open(source, "rb") as f:
                content = f.read()
        else:
            content = source

        fitz_doc = fitz.open(stream=content, filetype="pdf")
        plumber_doc = pdfplumber.open(io.BytesIO(content))
        return {"content": content, "fitz_doc": fitz_doc, "plumber_doc": plumber_doc}

    async def extract(self, doc_data: dict) -> List[dict]:
        raw_elements = []
        plumber_doc = doc_data["plumber_doc"]
        
        for page_idx, page in enumerate(plumber_doc.pages):
            page_num = page_idx + 1
            # Extract words / text elements with bounding boxes
            words = page.extract_words(extra_attrs=["fontname", "size"])
            
            # Combine words into lines / blocks if close
            for w in words:
                text = w["text"].strip()
                if not text:
                    continue
                x0, y0, x1, y1 = float(w["x0"]), float(w["top"]), float(w["x1"]), float(w["bottom"])
                font_size = float(w.get("size", 10.0))
                
                raw_elements.append({
                    "text": text,
                    "bbox": [x0, y0, x1, y1],
                    "page": page_num,
                    "font_size": font_size,
                    "confidence": 1.0,
                    "layer": "PDF_Text"
                })
                
        return raw_elements

    async def normalize(self, raw_elements: List[dict]) -> List[CanonicalObject]:
        canonical_list = []
        for elem in raw_elements:
            text = elem["text"]
            tag = extract_tag(text)
            obj_type = classify_object_type(text, tag)
            
            obj = CanonicalObject(
                type=obj_type,
                tag=tag,
                text=text,
                page=elem["page"],
                bbox=elem["bbox"],
                font_size=elem.get("font_size"),
                confidence=elem.get("confidence", 1.0),
                layer=elem.get("layer", "0"),
                metadata={"source_adapter": "NativePDFAdapter"}
            )
            canonical_list.append(obj)
            
        logger.info(f"NativePDFAdapter normalized {len(canonical_list)} canonical objects.")
        return canonical_list
