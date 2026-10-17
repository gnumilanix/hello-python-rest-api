"""Tests for the FastAPI app."""

from fastapi.testclient import TestClient

from necktie.main import app


def test_health() -> None:
    # Context manager runs the lifespan (cache init) around the requests.
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
