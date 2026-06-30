from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_run_readonly_rejects_unsafe_sql_before_db_execution() -> None:
    response = client.post("/api/sql/run-readonly", json={"sql": "DROP TABLE users"})
    assert response.status_code == 400


def test_validation_contract_shape() -> None:
    response = client.post("/api/sql/validate", json={"sql": "SELECT * FROM users LIMIT 10", "allow_write": False})
    assert response.status_code == 200
    body = response.json()
    assert "is_valid" in body
    assert "risk_level" in body
    assert "detected_statement_type" in body
