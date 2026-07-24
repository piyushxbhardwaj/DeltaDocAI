import time
import uuid
from typing import Union, List, Dict, Any, Optional
from src.ingest.base import BaseAdapter
from src.ingest.pdf import NativePDFAdapter
from src.ingest.ocr import ScannedPDFAdapter
from src.ingest.dwg import DWGAdapter
from src.ingest.canonical import CanonicalObject
from src.delta.comparator import DeltaComparator, DeltaResult
from src.delta.report import DeltaReportGenerator
from src.visualization.render import DocumentRenderer
from src.rag.retrieve import ChromaDBRetriever
from src.observability.tracer import PipelineTracer
from src.observability.logger import logger
from src.pipeline.pipeline import PipelineContext

class PipelineOrchestrator:
    """
    End-to-End Workflow Orchestrator:
    Upload -> Ingest -> Canonical -> Match -> Delta -> Report & AI Summary -> Visual Render -> Vector Indexing.
    """

    def __init__(self, retriever: Optional[ChromaDBRetriever] = None):
        self.comparator = DeltaComparator()
        self.retriever = retriever or ChromaDBRetriever()

    def _get_adapter(self, adapter_type: str) -> BaseAdapter:
        atype = adapter_type.lower()
        if atype in ["ocr", "scanned", "scanned_pdf"]:
            return ScannedPDFAdapter()
        elif atype in ["dwg", "cad"]:
            return DWGAdapter()
        return NativePDFAdapter()

    async def execute(
        self,
        doc_a_bytes: Union[bytes, str],
        doc_b_bytes: Union[bytes, str],
        adapter_type: str = "pdf",
        session_id: Optional[str] = None
    ) -> PipelineContext:
        session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        tracer = PipelineTracer()
        adapter = self._get_adapter(adapter_type)

        # 1. Ingestion Phase
        t0 = time.perf_counter()
        canonical_a = await adapter.process(doc_a_bytes)
        canonical_b = await adapter.process(doc_b_bytes)
        dt_ingest = (time.perf_counter() - t0) * 1000.0
        tracer.record_step("ingestion", dt_ingest, details={"adapter": adapter_type, "count_a": len(canonical_a), "count_b": len(canonical_b)})

        # 2. Delta Engine Comparison
        t0 = time.perf_counter()
        delta_result = self.comparator.compare(canonical_a, canonical_b)
        dt_delta = (time.perf_counter() - t0) * 1000.0
        tracer.record_step("delta_matching", dt_delta, details={"changes_found": delta_result.summary["total_changes"]})

        # 3. Report Generation
        t0 = time.perf_counter()
        report_gen = DeltaReportGenerator(delta_result)
        ai_summary = report_gen.generate_ai_summary()
        markdown_rep = report_gen.to_markdown()
        html_rep = report_gen.to_html()
        dt_report = (time.perf_counter() - t0) * 1000.0
        tracer.record_step("report_generation", dt_report)

        # 4. Vector Indexing into ChromaDB
        t0 = time.perf_counter()
        vector_docs = []
        for item in canonical_a:
            vector_docs.append({
                "id": f"revA-{item.id}",
                "text": f"Revision A Page {item.page}: {item.type} '{item.tag or item.text}' at bbox {item.bbox}. Text: '{item.text}'",
                "metadata": {"revision": "Revision A", "page": item.page, "tag": item.tag or "", "type": item.type}
            })
        for item in canonical_b:
            vector_docs.append({
                "id": f"revB-{item.id}",
                "text": f"Revision B Page {item.page}: {item.type} '{item.tag or item.text}' at bbox {item.bbox}. Text: '{item.text}'",
                "metadata": {"revision": "Revision B", "page": item.page, "tag": item.tag or "", "type": item.type}
            })
        vector_docs.append({
            "id": f"delta-summary-{session_id}",
            "text": f"Delta Report AI Summary:\n{ai_summary}\n\nFull Delta Report Markdown:\n{markdown_rep}",
            "metadata": {"revision": "Delta Report", "page": 1, "type": "Summary"}
        })

        await self.retriever.index_documents(vector_docs, collection_name=session_id)
        dt_index = (time.perf_counter() - t0) * 1000.0
        tracer.record_step("vector_indexing", dt_index, details={"indexed_chunks": len(vector_docs)})

        telemetry = tracer.get_summary()
        logger.info(f"Pipeline executed successfully for session {session_id} in {telemetry['total_latency_ms']} ms.")

        return PipelineContext(
            session_id=session_id,
            adapter_type=adapter_type,
            canonical_a=canonical_a,
            canonical_b=canonical_b,
            delta_result=delta_result,
            ai_summary=ai_summary,
            markdown_report=markdown_rep,
            html_report=html_rep,
            telemetry=telemetry
        )
