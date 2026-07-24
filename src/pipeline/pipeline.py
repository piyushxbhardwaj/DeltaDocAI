from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.ingest.canonical import CanonicalObject
from src.delta.comparator import DeltaResult
from src.observability.tracer import PipelineTracer

class PipelineContext(BaseModel):
    session_id: str
    adapter_type: str = "pdf"
    canonical_a: List[CanonicalObject] = Field(default_factory=list)
    canonical_b: List[CanonicalObject] = Field(default_factory=list)
    delta_result: Optional[DeltaResult] = None
    ai_summary: Optional[str] = None
    markdown_report: Optional[str] = None
    html_report: Optional[str] = None
    telemetry: Dict[str, Any] = Field(default_factory=dict)
