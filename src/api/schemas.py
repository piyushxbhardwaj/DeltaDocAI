from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.ingest.canonical import CanonicalObject
from src.delta.comparator import DeltaResult
from src.rag.chat import ChatResponse
from src.eval.metrics import Scorecard

class UploadResponse(BaseModel):
    filename: str
    adapter_type: str
    object_count: int
    canonical_objects: List[CanonicalObject]

class CompareRequest(BaseModel):
    doc_a_canonical: Optional[List[CanonicalObject]] = None
    doc_b_canonical: Optional[List[CanonicalObject]] = None
    adapter_type: str = "pdf"
    session_id: Optional[str] = None

class CompareResponse(BaseModel):
    session_id: str
    ai_summary: str
    delta_result: DeltaResult
    telemetry: Dict[str, Any]

class DeltaReportResponse(BaseModel):
    session_id: str
    ai_summary: str
    markdown_report: str
    html_report: str
    delta_result: DeltaResult

class ChatRequest(BaseModel):
    session_id: str
    query: str
    top_k: int = 5

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    llm_provider: str
    embedding_model: str
