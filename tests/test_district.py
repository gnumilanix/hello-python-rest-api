"""Tests for GET /district."""

from fastapi.testclient import TestClient


def test_list_districts_default_language(client: TestClient) -> None:
    response = client.get("/district")
    assert response.status_code == 200
    districts = response.json()
    assert len(districts) == 18
    # First district by sort_order is Central and Western.
    assert districts[0]["name"] == "Central and Western"
    assert districts[0]["id"] == 1


def test_list_districts_cantonese(client: TestClient) -> None:
    response = client.get("/district", params={"language": "yue"})
    assert response.status_code == 200
    assert response.json()[0]["name"] == "中西區"


def test_list_districts_mandarin(client: TestClient) -> None:
    response = client.get("/district", params={"language": "zh"})
    assert response.status_code == 200
    assert response.json()[0]["name"] == "中西區"


def test_list_districts_invalid_language(client: TestClient) -> None:
    response = client.get("/district", params={"language": "fr"})
    assert response.status_code == 422
