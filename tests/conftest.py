"""Shared fixtures for endpoint tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from necktie.main import app

# A valid create payload reused across tests.
DOCTOR_PAYLOAD = {
    "category_id": 19,  # general_practice
    "district_id": 1,  # Central and Western
    "consultation_fee": 300,
    "phone_numbers": ["23456789"],
    "name": {"en": "Dr Test", "yue": "測試醫生", "zh": "测试医生"},
    "address": {"en": "1 Test St", "yue": "測試街1號", "zh": "测试街1号"},
}


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Yield a TestClient that runs the app lifespan (cache + Redis)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def doctor_id(client: TestClient) -> int:
    """Create one doctor and return its id, for detail/get tests."""
    response = client.post("/doctors", json=DOCTOR_PAYLOAD)
    assert response.status_code == 201
    return response.json()["id"]
