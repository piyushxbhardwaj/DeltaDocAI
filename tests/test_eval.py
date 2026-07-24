import pytest
from src.eval.metrics import EvaluationSuite
from src.rag.chat import GroundedChatEngine

@pytest.mark.asyncio
async def test_evaluation_suite():
    chat_engine = GroundedChatEngine()
    scorecard = await EvaluationSuite.run_full_evaluation(
        detected_items=[],
        chat_engine=chat_engine,
        session_id="eval-test-sess"
    )

    assert scorecard.delta_precision >= 0.0
    assert scorecard.groundedness_score >= 0.0
    assert scorecard.avg_response_latency_ms >= 0.0
    assert scorecard.total_cost_usd >= 0.0
