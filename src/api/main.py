import io
import uuid
import time
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse

from src.api.schemas import (
    UploadResponse,
    CompareResponse,
    DeltaReportResponse,
    ChatRequest,
    HealthResponse
)
from src.api.dependencies import get_orchestrator, get_chat_engine, get_retriever
from src.pipeline.orchestrator import PipelineOrchestrator
from src.rag.chat import GroundedChatEngine, ChatResponse
from src.eval.metrics import EvaluationSuite, Scorecard
from src.visualization.render import DocumentRenderer
from src.observability.logger import configure_logger, logger
from src.observability.tracer import PipelineTracer

# Configure structured JSON logging
configure_logger()

app = FastAPI(
    title="DeltaDoc AI",
    description="AI-powered engineering document comparison, revision intelligence, and grounded conversational analysis.",
    version="1.0.0"
)

# CORS middleware for React frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory storage for active session contexts and telemetry logs
ACTIVE_SESSIONS: Dict[str, Any] = {}
LATEST_TELEMETRY: Dict[str, Any] = {}

@app.middleware("http")
async def trace_and_log_middleware(request, call_next):
    trace_id = request.headers.get("X-Trace-ID", f"tr-{uuid.uuid4().hex[:8]}")
    t0 = time.perf_counter()
    response = await call_next(request)
    dt_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    response.headers["X-Trace-ID"] = trace_id
    response.headers["X-Response-Time-MS"] = str(dt_ms)
    logger.info(f"Method={request.method} Path={request.url.path} Status={response.status_code} Latency={dt_ms}ms TraceID={trace_id}")
    return response

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    import os
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        llm_provider=os.getenv("LLM_PROVIDER", "gemini"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )

@app.post("/api/upload", response_model=UploadResponse, tags=["Ingestion"])
async def upload_document(
    file: UploadFile = File(...),
    adapter_type: str = Form("pdf")
):
    """
    Ingests an engineering document (Native PDF, Scanned PDF, or DWG) and outputs Canonical Objects.
    """
    try:
        content = await file.read()
        orchestrator = get_orchestrator()
        adapter = orchestrator._get_adapter(adapter_type)
        canonical_objects = await adapter.process(content)

        return UploadResponse(
            filename=file.filename or "document.pdf",
            adapter_type=adapter_type,
            object_count=len(canonical_objects),
            canonical_objects=canonical_objects
        )
    except Exception as e:
        logger.error(f"Error during upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare", response_model=CompareResponse, tags=["Delta Engine"])
async def compare_documents(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    adapter_type: str = Form("pdf"),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator)
):
    """
    Runs the full Delta Engine comparison between Revision A and Revision B.
    """
    try:
        content_a = await file_a.read()
        content_b = await file_b.read()

        context = await orchestrator.execute(
            doc_a_bytes=content_a,
            doc_b_bytes=content_b,
            adapter_type=adapter_type
        )

        ACTIVE_SESSIONS[context.session_id] = {
            "context": context,
            "raw_a": content_a,
            "raw_b": content_b
        }
        LATEST_TELEMETRY[context.session_id] = context.telemetry

        return CompareResponse(
            session_id=context.session_id,
            ai_summary=context.ai_summary or "",
            delta_result=context.delta_result,
            telemetry=context.telemetry
        )
    except Exception as e:
        logger.error(f"Error during comparison pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/delta", response_model=DeltaReportResponse, tags=["Delta Engine"])
async def get_delta_report(
    session_id: str = Query(..., description="Active comparison session ID"),
    format: str = Query("json", description="Output format: json, markdown, or html")
):
    """
    Retrieves the generated Delta Report for a given session.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Session ID not found. Run /api/compare first.")

    context = ACTIVE_SESSIONS[session_id]["context"]

    if format.lower() == "html":
        return HTMLResponse(content=context.html_report, status_code=200)
    elif format.lower() == "markdown":
        return Response(content=context.markdown_report, media_type="text/markdown")

    return DeltaReportResponse(
        session_id=context.session_id,
        ai_summary=context.ai_summary or "",
        markdown_report=context.markdown_report or "",
        html_report=context.html_report or "",
        delta_result=context.delta_result
    )

@app.post("/api/chat", response_model=ChatResponse, tags=["RAG Chat"])
async def grounded_chat(
    req: ChatRequest,
    chat_engine: GroundedChatEngine = Depends(get_chat_engine)
):
    """
    Grounded RAG Chat with Revision A, Revision B, and Delta Report context.
    """
    try:
        response = await chat_engine.ask(
            query=req.query,
            collection_name=req.session_id,
            top_k=req.top_k
        )
        return response
    except Exception as e:
        logger.error(f"Error during grounded chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visual-diff", tags=["Visualization"])
async def get_visual_diff(
    session_id: str = Query(...)
):
    """
    Returns side-by-side PNG image visual diff with Green (Added), Red (Removed), and Yellow (Modified) bounding box overlays.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Session ID not found.")

    sess_data = ACTIVE_SESSIONS[session_id]
    context = sess_data["context"]
    raw_a = sess_data["raw_a"]
    raw_b = sess_data["raw_b"]

    try:
        imgs_a = DocumentRenderer.render_pdf_to_images(raw_a)
        imgs_b = DocumentRenderer.render_pdf_to_images(raw_b)

        img_a = imgs_a[0] if imgs_a else DocumentRenderer.render_pdf_to_images(b"%PDF-mock")[0]
        img_b = imgs_b[0] if imgs_b else DocumentRenderer.render_pdf_to_images(b"%PDF-mock")[0]

        combined = DocumentRenderer.generate_side_by_side_overlay(
            img_a=img_a,
            img_b=img_b,
            delta_items=context.delta_result.items
        )

        buf = io.BytesIO()
        combined.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        logger.error(f"Error generating visual diff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics", tags=["Observability"])
async def get_metrics():
    """
    Returns latest telemetry traces, latency metrics, and token usage data.
    """
    return {
        "active_sessions": list(ACTIVE_SESSIONS.keys()),
        "telemetry_traces": LATEST_TELEMETRY
    }

@app.get("/api/eval", response_model=Scorecard, tags=["Evaluation"])
async def run_evaluation(
    session_id: Optional[str] = Query(None),
    chat_engine: GroundedChatEngine = Depends(get_chat_engine)
):
    """
    Runs the quantitative AI Evaluation suite and returns performance scorecard.
    """
    detected_items = []
    sess = session_id or (list(ACTIVE_SESSIONS.keys())[0] if ACTIVE_SESSIONS else "demo-sess")
    
    if sess in ACTIVE_SESSIONS:
        detected_items = ACTIVE_SESSIONS[sess]["context"].delta_result.items

    scorecard = await EvaluationSuite.run_full_evaluation(
        detected_items=detected_items,
        chat_engine=chat_engine,
        session_id=sess
    )
    return scorecard
