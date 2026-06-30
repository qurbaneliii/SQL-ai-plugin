from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_works_without_env() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "provider_mode" in body
