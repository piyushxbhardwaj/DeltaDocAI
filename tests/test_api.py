import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "llm_provider" in data

def test_metrics_endpoint():
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "active_sessions" in data

def test_eval_endpoint():
    res = client.get("/api/eval")
    assert res.status_code == 200
    data = res.json()
    assert "delta_precision" in data
    assert "groundedness_score" in data
