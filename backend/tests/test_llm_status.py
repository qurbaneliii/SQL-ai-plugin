from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_llm_status_without_openai_or_ollama() -> None:
    response = client.get("/api/llm/status")
    assert response.status_code == 200
    body = response.json()
    assert body["fallback_available"] is True


def test_provider_test_falls_back_when_unavailable() -> None:
    response = client.post("/api/llm/test-openai", json={"providerMode": "openai"})
    assert response.status_code == 200
    body = response.json()
    assert body["provider_metadata"]["selected_provider"] == "fallback"
