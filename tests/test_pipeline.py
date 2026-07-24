import pytest
from src.pipeline.orchestrator import PipelineOrchestrator
from src.rag.retrieve import ChromaDBRetriever

@pytest.mark.asyncio
async def test_pipeline_orchestrator():
    retriever = ChromaDBRetriever(persist_directory="./data/test_chroma_pipeline")
    orchestrator = PipelineOrchestrator(retriever=retriever)

    context = await orchestrator.execute(
        doc_a_bytes="sample_drawing_a.dwg",
        doc_b_bytes="sample_drawing_b.dwg",
        adapter_type="dwg",
        session_id="test-pipeline-sess"
    )

    assert context.session_id == "test-pipeline-sess"
    assert len(context.canonical_a) > 0
    assert len(context.canonical_b) > 0
    assert context.delta_result is not None
    assert context.ai_summary is not None
    assert context.telemetry is not None
