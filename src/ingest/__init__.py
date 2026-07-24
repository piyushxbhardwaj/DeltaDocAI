"""
Ingestion module for DeltaDoc AI.
"""
from src.ingest.canonical import CanonicalObject, ObjectType
from src.ingest.base import BaseAdapter
from src.ingest.pdf import NativePDFAdapter
from src.ingest.ocr import ScannedPDFAdapter
from src.ingest.dwg import DWGAdapter

__all__ = [
    "CanonicalObject",
    "ObjectType",
    "BaseAdapter",
    "NativePDFAdapter",
    "ScannedPDFAdapter",
    "DWGAdapter",
]
