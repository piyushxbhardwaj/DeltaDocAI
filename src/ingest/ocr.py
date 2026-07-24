import io
import fitz  # PyMuPDF
from PIL import Image
from typing import Any, List, Union
from src.ingest.base import BaseAdapter
from src.ingest.canonical import CanonicalObject
from src.ingest.pdf import extract_tag, classify_object_type
from src.observability.logger import logger

class ScannedPDFAdapter(BaseAdapter):
    """Adapter for scanned documents requiring Optical Character Recognition (OCR)."""

    def __init__(self, use_easyocr: bool = True):
        self.use_easyocr = use_easyocr
        self.ocr_reader = None

    def _init_ocr(self):
        if self.use_easyocr and self.ocr_reader is None:
            try:
                import easyocr
                self.ocr_reader = easyocr.Reader(['en'], gpu=False)
                logger.info("EasyOCR initialized successfully.")
            except Exception as e:
                logger.warning(f"EasyOCR initialization failed ({e}). Falling back to PyMuPDF image text extraction.")
                self.ocr_reader = None

    async def load(self, source: Union[bytes, str]) -> dict:
        if isinstance(source, str):
            with open(source, "rb") as f:
                content = f.read()
        else:
            content = source

        doc = fitz.open(stream=content, filetype="pdf")
        return {"doc": doc, "content": content}

    async def extract(self, doc_data: dict) -> List[dict]:
        self._init_ocr()
        doc = doc_data["doc"]
        raw_elements = []

        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            
            if self.ocr_reader:
                try:
                    results = self.ocr_reader.readtext(img_bytes)
                    for (bbox, text, conf) in results:
                        text_str = text.strip()
                        if not text_str:
                            continue
                        xs = [pt[0] for pt in bbox]
                        ys = [pt[1] for pt in bbox]
                        norm_bbox = [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))]
                        raw_elements.append({
                            "text": text_str,
                            "bbox": norm_bbox,
                            "page": page_num,
                            "confidence": float(conf),
                            "layer": "OCR_Text"
                        })
                except Exception as e:
                    logger.warning(f"EasyOCR page execution failed: {e}. Using PyMuPDF text fallback.")
                    self._extract_pymupdf_fallback(page, page_num, raw_elements)
            else:
                self._extract_pymupdf_fallback(page, page_num, raw_elements)

        return raw_elements

    def _extract_pymupdf_fallback(self, page, page_num: int, raw_elements: List[dict]):
        text_page = page.get_text("blocks")
        for b in text_page:
            x0, y0, x1, y1, text, block_no, block_type = b[:7]
            text_clean = text.strip()
            if text_clean:
                raw_elements.append({
                    "text": text_clean,
                    "bbox": [float(x0), float(y0), float(x1), float(y1)],
                    "page": page_num,
                    "confidence": 0.90,
                    "layer": "OCR_Fallback"
                })

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
                confidence=elem["confidence"],
                layer=elem["layer"],
                metadata={"source_adapter": "ScannedPDFAdapter"}
            )
            canonical_list.append(obj)

        logger.info(f"ScannedPDFAdapter normalized {len(canonical_list)} canonical objects.")
        return canonical_list
