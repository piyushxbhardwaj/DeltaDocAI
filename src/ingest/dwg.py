from typing import Any, List, Union
from src.ingest.base import BaseAdapter
from src.ingest.canonical import CanonicalObject
from src.observability.logger import logger

class DWGAdapter(BaseAdapter):
    """
    Adapter stub for DWG CAD drawings.
    Simulates parsing DWG layers, block attributes, and CAD text entities.
    """

    async def load(self, source: Union[bytes, str]) -> dict:
        filename = source if isinstance(source, str) else "uploaded_drawing.dwg"
        return {"filename": filename, "source": source}

    async def extract(self, doc_data: dict) -> List[dict]:
        # Simulated extraction of DWG entities from CAD blocks and layers
        return [
            {
                "text": "DRAWING NO: DWG-2026-ENG-001",
                "tag": None,
                "bbox": [50.0, 50.0, 300.0, 100.0],
                "page": 1,
                "layer": "TITLE_BLOCK",
                "rotation": 0.0,
                "confidence": 1.0,
                "type": "Title Block"
            },
            {
                "text": "26-PIT-9055 Pressure Transmitter",
                "tag": "26-PIT-9055",
                "bbox": [150.0, 200.0, 280.0, 230.0],
                "page": 1,
                "layer": "INSTRUMENTS",
                "rotation": 0.0,
                "confidence": 0.99,
                "type": "Instrument"
            },
            {
                "text": "V-102 Ball Valve 4-Inch",
                "tag": "V-102",
                "bbox": [320.0, 210.0, 410.0, 240.0],
                "page": 1,
                "layer": "VALVES",
                "rotation": 0.0,
                "confidence": 0.98,
                "type": "Valve"
            },
            {
                "text": "MAIN PROCESS PIPELINE 6\"-CS-150",
                "tag": "6\"-CS-150",
                "bbox": [100.0, 220.0, 600.0, 225.0],
                "page": 1,
                "layer": "PIPING",
                "rotation": 0.0,
                "confidence": 0.97,
                "type": "Pipeline"
            },
            {
                "text": "GENERAL NOTES: ALL DIMENSIONS IN MM UNLESS NOTED OTHERWISE",
                "tag": None,
                "bbox": [50.0, 700.0, 500.0, 750.0],
                "page": 1,
                "layer": "NOTES",
                "rotation": 0.0,
                "confidence": 1.0,
                "type": "Notes"
            }
        ]

    async def normalize(self, raw_elements: List[dict]) -> List[CanonicalObject]:
        canonical_list = []
        for elem in raw_elements:
            obj = CanonicalObject(
                type=elem.get("type", "Text"),
                tag=elem.get("tag"),
                text=elem["text"],
                page=elem.get("page", 1),
                bbox=elem.get("bbox", [0.0, 0.0, 0.0, 0.0]),
                rotation=elem.get("rotation", 0.0),
                layer=elem.get("layer", "0"),
                confidence=elem.get("confidence", 1.0),
                metadata={"source_adapter": "DWGAdapter", "is_cad_stub": True}
            )
            canonical_list.append(obj)

        logger.info(f"DWGAdapter normalized {len(canonical_list)} canonical objects.")
        return canonical_list
