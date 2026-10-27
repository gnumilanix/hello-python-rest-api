"""Integration tests for localized doctor reads and CRUD operations."""

import asyncio
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from necktie.db.session import DATABASE_URL
from necktie.models import OperatingHour
from tests.conftest import DOCTOR_PAYLOAD


@pytest.fixture
def mutable_doctor(client: TestClient) -> Iterator[int]:
    response = client.post("/doctors", json=DOCTOR_PAYLOAD)
    assert response.status_code == 201
    doctor_id = response.json()["id"]
    yield doctor_id
    client.delete(f"/doctors/{doctor_id}")


async def stored_hours(doctor_id: int) -> list[OperatingHour]:
    engine = create_async_engine(DATABASE_URL)
    try:
        async with AsyncSession(engine) as session:
            result = await session.exec(
                select(OperatingHour).where(OperatingHour.doctor_id == doctor_id)
            )
            return list(result.all())
    finally:
        await engine.dispose()


class TestListDoctors:
    SIZE = 100  # large enough to include doctors created in earlier runs

    def test_plural_route_contract(self, client: TestClient) -> None:
        paths = client.get("/openapi.json").json()["paths"]
        assert set(paths["/doctors"]) == {"get", "post"}
        assert set(paths["/doctors/{doctor_id}"]) == {"get", "put", "patch", "delete"}
        assert set(paths["/doctors/batch"]) == {"post"}
        assert not any(
            path == "/doctor" or path.startswith("/doctor/") for path in paths
        )
        assert client.get("/doctor").status_code == 404

    def test_default_language(self, client: TestClient, doctor_id: int) -> None:
        response = client.get("/doctors", params={"size": self.SIZE})
        assert response.status_code == 200
        doctors = response.json()
        assert any(d["id"] == doctor_id for d in doctors)
        doctor = next(d for d in doctors if d["id"] == doctor_id)
        assert doctor["name"] == "Dr Test"
        assert doctor["district"]["name"] == "Central and Western"

    def test_localized_cantonese(self, client: TestClient, doctor_id: int) -> None:
        response = client.get("/doctors", params={"language": "yue", "size": self.SIZE})
        assert response.status_code == 200
        doctor = next(d for d in response.json() if d["id"] == doctor_id)
        assert doctor["name"] == "測試醫生"
        assert doctor["district"]["name"] == "中西區"

    def test_localized_mandarin(self, client: TestClient, doctor_id: int) -> None:
        response = client.get("/doctors", params={"language": "zh", "size": self.SIZE})
        assert response.status_code == 200
        doctor = next(d for d in response.json() if d["id"] == doctor_id)
        assert doctor["name"] == "测试医生"

    def test_filter_by_district(self, client: TestClient, doctor_id: int) -> None:
        response = client.get("/doctors", params={"district": 1, "size": self.SIZE})
        assert response.status_code == 200
        assert any(d["id"] == doctor_id for d in response.json())
        # A district with no doctors returns empty.
        response = client.get("/doctors", params={"district": 18, "size": self.SIZE})
        assert response.status_code == 200
        assert not any(d["id"] == doctor_id for d in response.json())

    def test_filter_by_fee_range(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(
            "/doctors", params={"min_fee": 100, "max_fee": 500, "size": self.SIZE}
        )
        assert response.status_code == 200
        assert any(d["id"] == doctor_id for d in response.json())
        response = client.get("/doctors", params={"min_fee": 9999, "size": self.SIZE})
        assert not any(d["id"] == doctor_id for d in response.json())

    def test_pagination(self, client: TestClient, doctor_id: int) -> None:
        response = client.get("/doctors", params={"page": 0, "size": 10})
        assert response.status_code == 200
        # size below minimum is rejected.
        assert client.get("/doctors", params={"size": 5}).status_code == 422
        # size above maximum is rejected.
        assert client.get("/doctors", params={"size": 101}).status_code == 422


class TestGetDoctor:
    def test_default_language(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctors/{doctor_id}")
        assert response.status_code == 200
        doctor = response.json()
        assert doctor["id"] == doctor_id
        assert doctor["name"] == "Dr Test"
        assert doctor["address"] == "1 Test St"
        assert doctor["district"]["name"] == "Central and Western"
        assert doctor["category"]["name"] == "General Practice"

    def test_localized_cantonese(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctors/{doctor_id}", params={"language": "yue"})
        assert response.status_code == 200
        doctor = response.json()
        assert doctor["name"] == "測試醫生"
        assert doctor["address"] == "測試街1號"

    def test_localized_mandarin(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctors/{doctor_id}", params={"language": "zh"})
        assert response.status_code == 200
        assert response.json()["name"] == "测试医生"

    def test_not_found(self, client: TestClient) -> None:
        response = client.get("/doctors/9999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Doctor not found"}

    def test_invalid_language(self, client: TestClient, doctor_id: int) -> None:
        response = client.get(f"/doctors/{doctor_id}", params={"language": "fr"})
        assert response.status_code == 422


class TestCreateDoctor:
    def test_create(self, client: TestClient) -> None:
        response = client.post("/doctors", json=DOCTOR_PAYLOAD)
        assert response.status_code == 201
        doctor = response.json()
        assert doctor["id"] is not None
        assert doctor["name"] == "Dr Test"  # default language is en
        assert doctor["consultation_fee"] == 300

    def test_invalid_category(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "category_id": 9999}
        response = client.post("/doctors", json=payload)
        assert response.status_code == 400

    def test_invalid_district(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "district_id": 9999}
        response = client.post("/doctors", json=payload)
        assert response.status_code == 400

    def test_missing_mandatory_language(self, client: TestClient) -> None:
        payload = {
            **DOCTOR_PAYLOAD,
            "name": {"en": "Dr Test"},  # missing yue and zh
        }
        response = client.post("/doctors", json=payload)
        assert response.status_code == 422

    def test_invalid_phone(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "phone_numbers": ["not-a-number"]}
        response = client.post("/doctors", json=payload)
        assert response.status_code == 422

    def test_overlong_place_id_rejected(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "place_id": "x" * 256}
        response = client.post("/doctors", json=payload)
        assert response.status_code == 422

    def test_overlong_name_rejected(self, client: TestClient) -> None:
        payload = {**DOCTOR_PAYLOAD, "name": {"en": "x" * 256, "yue": "y", "zh": "z"}}
        response = client.post("/doctors", json=payload)
        assert response.status_code == 422


class TestDoctorMutations:
    def test_patch_preserves_fields_and_invalidates_detail_cache(
        self, client: TestClient
    ) -> None:
        created = client.post("/doctors", json=DOCTOR_PAYLOAD).json()
        path = f"/doctors/{created['id']}"
        assert client.get(path).json()["consultation_fee"] == 300
        response = client.patch(path, json={"consultation_fee": 450})
        assert response.status_code == 200
        assert response.json()["consultation_fee"] == 450
        assert response.json()["name"] == created["name"]
        assert client.get(path).json()["consultation_fee"] == 450

    def test_put_replaces_hours_and_resets_defaults(self, client: TestClient) -> None:
        created = client.post(
            "/doctors",
            json={
                **DOCTOR_PAYLOAD,
                "member_exclusive_fee": 100,
                "is_open_on_public_holidays": True,
                "operating_hours": [
                    {
                        "day_of_week": "monday",
                        "open_time": "09:00",
                        "close_time": "18:00",
                    }
                ],
            },
        )
        assert created.status_code == 201
        path = f"/doctors/{created.json()['id']}"
        response = client.put(path, json={**DOCTOR_PAYLOAD, "consultation_fee": 500})
        assert response.status_code == 200
        assert response.json()["consultation_fee"] == 500
        assert response.json()["operating_hours"] == []
        assert response.json()["member_exclusive_fee"] is None
        assert response.json()["is_open_on_public_holidays"] is False

    def test_delete_invalidates_cached_detail(self, client: TestClient) -> None:
        created = client.post("/doctors", json=DOCTOR_PAYLOAD).json()
        path = f"/doctors/{created['id']}"
        assert client.get(path).status_code == 200
        response = client.delete(path)
        assert response.status_code == 204
        assert response.content == b""
        assert client.get(path).status_code == 404
        assert client.delete(path).status_code == 404


class TestDoctorUpdateContracts:
    def test_patch_translations_merge(
        self, client: TestClient, mutable_doctor: int
    ) -> None:
        path = f"/doctors/{mutable_doctor}"
        response = client.patch(
            path, json={"name": {"en": "Updated"}, "address": {"en": "New address"}}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"
        assert response.json()["address"] == "New address"
        for language in ("yue", "zh"):
            localized = client.get(path, params={"language": language}).json()
            assert localized["name"] == DOCTOR_PAYLOAD["name"][language]
            assert localized["address"] == DOCTOR_PAYLOAD["address"][language]

    def test_patch_nullable_fields_and_empty_lists(
        self, client: TestClient, mutable_doctor: int
    ) -> None:
        path = f"/doctors/{mutable_doctor}"
        assert (
            client.patch(
                path,
                json={
                    "place_id": "some-place",
                    "member_exclusive_fee": 0,
                    "fee_detail": {"en": "Medicine extra", "yue": "Fee details"},
                    "is_open_on_public_holidays": True,
                    "operating_hours": [
                        {
                            "day_of_week": "sunday",
                            "open_time": "10:00",
                            "close_time": "17:00",
                        }
                    ],
                },
            ).status_code
            == 200
        )
        response = client.patch(
            path,
            json={
                "place_id": None,
                "member_exclusive_fee": None,
                "fee_detail": {"en": None},
                "operating_hours": [],
                "is_open_on_public_holidays": False,
                "consultation_fee": 0,
            },
        )
        assert response.status_code == 200
        doctor = client.get(path).json()
        assert doctor["place_id"] is None
        assert doctor["member_exclusive_fee"] is None
        assert doctor["fee_detail"] is None
        assert doctor["operating_hours"] == []
        assert doctor["consultation_fee"] == 0
        assert doctor["is_open_on_public_holidays"] is False
        assert client.get(path, params={"language": "yue"}).json()["fee_detail"]
        assert client.patch(path, json={"fee_detail": None}).status_code == 200
        assert client.get(path, params={"language": "yue"}).json()["fee_detail"] is None

    def test_patch_replaces_hours_and_phone_lists(
        self, client: TestClient, mutable_doctor: int
    ) -> None:
        path = f"/doctors/{mutable_doctor}"
        for day in ("monday", "saturday"):
            response = client.patch(
                path,
                json={
                    "phone_numbers": ["23456789", "91234567"],
                    "operating_hours": [
                        {
                            "day_of_week": day,
                            "open_time": "09:00",
                            "close_time": "18:00",
                        }
                    ],
                },
            )
            assert response.status_code == 200
            assert response.json()["phone_numbers"] == ["23456789", "91234567"]
            assert [
                hour["day_of_week"] for hour in response.json()["operating_hours"]
            ] == [day]
        rows = asyncio.run(stored_hours(mutable_doctor))
        assert len(rows) == 1
        assert rows[0].day_of_week.value == "saturday"
        assert client.delete(path).status_code == 204
        assert asyncio.run(stored_hours(mutable_doctor)) == []

    @pytest.mark.parametrize("method", ["put", "patch"])
    @pytest.mark.parametrize("reference", ["category_id", "district_id"])
    def test_invalid_reference_does_not_change_listing(
        self, client: TestClient, mutable_doctor: int, method: str, reference: str
    ) -> None:
        path = f"/doctors/{mutable_doctor}"
        payload = DOCTOR_PAYLOAD if method == "put" else {}
        before = client.get(path).json()
        response = client.request(
            method, path, json={**payload, reference: 9999, "consultation_fee": 999}
        )
        assert response.status_code == 400
        assert client.get(path).json() == before

    @pytest.mark.parametrize(
        "payload",
        [
            {"consultation_fee": None},
            {"category_id": None},
            {"district_id": None},
            {"name": None},
            {"name": {"en": None}},
            {"name": {"en": ""}},
            {"name": {"en": "a" * 256}},
            {"address": {"en": None}},
            {"phone_numbers": None},
            {"phone_numbers": []},
            {"phone_numbers": ["not-a-number"]},
            {"operating_hours": None},
            {"is_open_on_public_holidays": None},
            {"place_id": "x" * 256},
            {"unknown_field": 1},
        ],
    )
    def test_invalid_patch_is_rejected(
        self, client: TestClient, mutable_doctor: int, payload: dict
    ) -> None:
        path = f"/doctors/{mutable_doctor}"
        before = client.get(path).json()
        assert client.patch(path, json=payload).status_code == 422
        assert client.get(path).json() == before

    def test_empty_patch_is_noop(self, client: TestClient, mutable_doctor: int) -> None:
        path = f"/doctors/{mutable_doctor}"
        before = client.get(path).json()
        assert client.patch(path, json={}).json() == before

    def test_put_requires_full_payload(
        self, client: TestClient, mutable_doctor: int
    ) -> None:
        assert (
            client.put(
                f"/doctors/{mutable_doctor}", json={"consultation_fee": 400}
            ).status_code
            == 422
        )

    @pytest.mark.parametrize("method", ["put", "patch", "delete"])
    def test_missing_listing_returns_404(self, client: TestClient, method: str) -> None:
        payload = DOCTOR_PAYLOAD if method == "put" else {}
        response = client.request(method, "/doctors/2147483647", json=payload)
        assert response.status_code == 404

    def test_put_replaces_all_translations(
        self, client: TestClient, mutable_doctor: int
    ) -> None:
        path = f"/doctors/{mutable_doctor}"
        names = {language: f"Doctor {language}" for language in ("en", "yue", "zh")}
        addresses = {language: f"Address {language}" for language in names}
        response = client.put(
            path,
            json={
                **DOCTOR_PAYLOAD,
                "name": names,
                "address": addresses,
                "category_id": 1,
                "district_id": 2,
            },
        )
        assert response.status_code == 200
        assert response.json()["id"] == mutable_doctor
        assert response.json()["category"]["id"] == 1
        assert response.json()["district"]["id"] == 2
        for language in names:
            localized = client.get(path, params={"language": language}).json()
            assert localized["name"] == names[language]
            assert localized["address"] == addresses[language]

    @pytest.mark.parametrize("method", ["put", "patch", "delete"])
    def test_write_invalidates_cached_lists(
        self, client: TestClient, mutable_doctor: int, method: str
    ) -> None:
        path = f"/doctors/{mutable_doctor}"
        assert client.patch(path, json={"consultation_fee": 1973}).status_code == 200
        params = {"min_fee": 1973, "max_fee": 1973, "language": "yue"}
        assert mutable_doctor in [
            doctor["id"] for doctor in client.get("/doctors", params=params).json()
        ]
        payload = DOCTOR_PAYLOAD if method == "put" else {}
        response = client.request(
            method, path, json={**payload, "consultation_fee": 1974}
        )
        assert response.status_code == (204 if method == "delete" else 200)
        assert mutable_doctor not in [
            doctor["id"] for doctor in client.get("/doctors", params=params).json()
        ]


class TestWeekdayContract:
    @pytest.mark.parametrize(
        "day",
        ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    )
    def test_create_and_read_named_weekday(self, client: TestClient, day: str) -> None:
        response = client.post(
            "/doctors",
            json={
                **DOCTOR_PAYLOAD,
                "operating_hours": [
                    {"day_of_week": day, "open_time": "09:00", "close_time": "18:00"}
                ],
            },
        )
        assert response.status_code == 201
        path = f"/doctors/{response.json()['id']}"
        try:
            assert response.json()["operating_hours"][0]["day_of_week"] == day
            for language in ("en", "yue", "zh"):
                doctor = client.get(path, params={"language": language}).json()
                assert doctor["operating_hours"][0]["day_of_week"] == day
        finally:
            client.delete(path)

    @pytest.mark.parametrize("day", [0, 1, 7, 8, "Monday", "funday"])
    @pytest.mark.parametrize("method", ["post", "put", "patch"])
    def test_rejects_non_enum_weekdays(
        self, client: TestClient, mutable_doctor: int, day: object, method: str
    ) -> None:
        path = "/doctors" if method == "post" else f"/doctors/{mutable_doctor}"
        response = client.request(
            method,
            path,
            json={
                **DOCTOR_PAYLOAD,
                "operating_hours": [
                    {"day_of_week": day, "open_time": "09:00", "close_time": "18:00"}
                ],
            },
        )
        assert response.status_code == 422

    def test_openapi_exposes_named_enum(self, client: TestClient) -> None:
        schema = client.get("/openapi.json").json()["components"]["schemas"]
        assert schema["DayOfWeek"]["type"] == "string"
        assert schema["DayOfWeek"]["enum"] == [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for model in ("OperatingHour", "OperatingHourInput"):
            assert schema[model]["properties"]["day_of_week"] == {
                "$ref": "#/components/schemas/DayOfWeek"
            }


class TestCreateDoctorsBatch:
    def test_batch_create(self, client: TestClient) -> None:
        payloads = [
            {**DOCTOR_PAYLOAD, "consultation_fee": 400},
            {**DOCTOR_PAYLOAD, "consultation_fee": 500},
        ]
        response = client.post("/doctors/batch", json=payloads)
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
        response = client.post("/doctors/batch", json=payloads)
        assert response.status_code == 400
