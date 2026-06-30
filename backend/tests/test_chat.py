from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_endpoint_returns_valid_structure() -> None:
    response = client.post(
        "/api/chat/message",
        json={
            "message": "Generate SQL for top 10 users",
            "databaseUrl": None,
            "currentSql": "",
            "selectedSchemas": [],
            "selectedTables": [],
            "providerMode": "fallback",
            "autoRun": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "assistant_message" in body
    assert body["intent"] == "sql_generate"
    assert "provider_metadata" in body
