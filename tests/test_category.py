"""Tests for GET /category."""

from fastapi.testclient import TestClient


def test_list_categories_default_language(client: TestClient) -> None:
    response = client.get("/category")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 58
    assert categories[0]["name"] == "Anaesthesiology"
    assert categories[0]["name_key"] == "anaesthesiology"


def test_list_categories_cantonese(client: TestClient) -> None:
    response = client.get("/category", params={"language": "yue"})
    assert response.status_code == 200
    assert response.json()[2]["name"] == "心臟科"  # cardiology, id=3


def test_list_categories_invalid_language(client: TestClient) -> None:
    response = client.get("/category", params={"language": "de"})
    assert response.status_code == 422
