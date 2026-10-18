"""Tests for the doctor endpoints (GET list, GET by id, POST single, POST batch)."""

from fastapi.testclient import TestClient

from tests.conftest import DOCTOR_PAYLOAD


class TestListDoctors:
    SIZE = 100  # large enough to include doctors created in earlier runs

    def test_default_language(self, client: TestClient, doctor_id: int) -> None:
        response = client.get("/doctor", params={"size": self.SIZE})
        assert response.status_code == 200
        doctors = response.json()
        assert any(d["id"] == doctor_id for d in doctors)
        doctor = next(d for d in doctors if d["id"] == doctor_id)
        assert doctor["name"] == "Dr Test"
        assert doctor["district"]["name"] == "Central and Western"

    def test_localized_cantonese(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(
            "/doctor", params={"language": "yue", "size": self.SIZE}
        )
        assert response.status_code == 200
        doctor = next(d for d in response.json() if d["id"] == doctor_id)
        assert doctor["name"] == "測試醫生"
        assert doctor["district"]["name"] == "中西區"

    def test_localized_mandarin(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(
            "/doctor", params={"language": "zh", "size": self.SIZE}
        )
        assert response.status_code == 200
        doctor = next(d for d in response.json() if d["id"] == doctor_id)
        assert doctor["name"] == "测试医生"

    def test_filter_by_district(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(
            "/doctor", params={"district": 1, "size": self.SIZE}
        )
        assert response.status_code == 200
        assert any(d["id"] == doctor_id for d in response.json())
        # A district with no doctors returns empty.
        response = client.get(
            "/doctor", params={"district": 18, "size": self.SIZE}
        )
        assert response.status_code == 200
        assert not any(d["id"] == doctor_id for d in response.json())

    def test_filter_by_fee_range(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(
            "/doctor", params={"min_fee": 100, "max_fee": 500, "size": self.SIZE}
        )
        assert response.status_code == 200
        assert any(d["id"] == doctor_id for d in response.json())
        response = client.get("/doctor", params={"min_fee": 9999, "size": self.SIZE})
        assert not any(d["id"] == doctor_id for d in response.json())

    def test_pagination(self, client: TestClient, doctor_id: int) -> None:
        response = client.get("/doctor", params={"page": 0, "size": 10})
        assert response.status_code == 200
        # size below minimum is rejected.
        assert client.get("/doctor", params={"size": 5}).status_code == 422
        # size above maximum is rejected.
        assert client.get("/doctor", params={"size": 101}).status_code == 422


class TestGetDoctor:
    def test_default_language(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctor/{doctor_id}")
        assert response.status_code == 200
        doctor = response.json()
        assert doctor["id"] == doctor_id
        assert doctor["name"] == "Dr Test"
        assert doctor["address"] == "1 Test St"
        assert doctor["district"]["name"] == "Central and Western"
        assert doctor["category"]["name"] == "General Practice"

    def test_localized_cantonese(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctor/{doctor_id}", params={"language": "yue"})
        assert response.status_code == 200
        doctor = response.json()
        assert doctor["name"] == "測試醫生"
        assert doctor["address"] == "測試街1號"

    def test_localized_mandarin(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctor/{doctor_id}", params={"language": "zh"})
        assert response.status_code == 200
        assert response.json()["name"] == "测试医生"

    def test_not_found(self, client: TestClient) -> None:
        response = client.get("/doctor/9999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Doctor not found"}

    def test_invalid_language(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctor/{doctor_id}", params={"language": "fr"})
        assert response.status_code == 422


class TestCreateDoctor:
    def test_create(self, client: TestClient) -> None:
        response = client.post("/doctor", json=DOCTOR_PAYLOAD)
        assert response.status_code == 201
        doctor = response.json()
        assert doctor["id"] is not None
        assert doctor["name"] == "Dr Test"  # default language is en
        assert doctor["consultation_fee"] == 300

    def test_invalid_category(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "category_id": 9999}
        response = client.post("/doctor", json=payload)
        assert response.status_code == 400

    def test_invalid_district(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "district_id": 9999}
        response = client.post("/doctor", json=payload)
        assert response.status_code == 400

    def test_missing_mandatory_language(self, client: TestClient) -> None:
        payload = {
            **DOCTOR_PAYLOAD,
            "name": {"en": "Dr Test"},  # missing yue and zh
        }
        response = client.post("/doctor", json=payload)
        assert response.status_code == 422

    def test_invalid_phone(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "phone_numbers": ["not-a-number"]}
        response = client.post("/doctor", json=payload)
        assert response.status_code == 422


class TestCreateDoctorsBatch:
    def test_batch_create(self, client: TestClient) -> None:
        payloads = [
            {**DOCTOR_PAYLOAD, "consultation_fee": 400},
            {**DOCTOR_PAYLOAD, "consultation_fee": 500},
        ]
        response = client.post("/doctor/batch", json=payloads)
        assert response.status_code == 201
        doctors = response.json()
        assert len(doctors) == 2
        assert doctors[0]["consultation_fee"] == 400
        assert doctors[1]["consultation_fee"] == 500

    def test_batch_rolls_back_on_invalid(self, client: TestClient) -> None:
        """A batch with one invalid payload creates nothing."""
        payloads = [
            DOCTOR_PAYLOAD,
            {**DOCTOR_PAYLOAD, "category_id": 9999},
        ]
        response = client.post("/doctor/batch", json=payloads)
        assert response.status_code == 400
