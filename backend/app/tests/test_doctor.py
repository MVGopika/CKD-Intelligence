from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.db import models
from app.core import security

client = TestClient(app)


def test_patients_endpoint_requires_auth():
    # no auth header -> unauthorized
    response = client.get("/api/doctor/patients")
    assert response.status_code == 401


def test_get_patients_empty_list():
    # override dependency to supply a doctor with no patients; also stub db
    def fake_doctor():
        user = models.User(id=1, email="doc@example.com", full_name="Dr. Test")
        user.role = models.Role(id=2, name="doctor")
        user.doctor_patients = []
        return user

    class DummyQuery:
        def __init__(self, items):
            self.items = items
        def all(self):
            return self.items
        def filter(self, *args, **kwargs):
            return self
        def order_by(self, *args, **kwargs):
            return self
        def first(self):
            return self.items[0] if self.items else None

    class FakeDB:
        def __init__(self, items):
            self.items = items
        def query(self, model):
            if model == models.PatientProfile:
                return DummyQuery(self.items)
            return DummyQuery([])

    # doctor has no linked patients, but DB contains one profile
    fake_db = FakeDB([models.PatientProfile(id=9)])

    app.dependency_overrides[security.get_doctor_user] = fake_doctor
    app.dependency_overrides[functions=app.api.deps.get_db_session] = lambda: fake_db  # type: ignore

    response = client.get("/api/doctor/patients")
    assert response.status_code == 200
    # fallback returned one profile with default fields
    data = response.json()
    assert isinstance(data, dict)
    assert data["patients"] != []

    # cleanup
    app.dependency_overrides.pop(security.get_doctor_user, None)
    app.dependency_overrides.pop(functions=app.api.deps.get_db_session, None)


def test_doctor_patient_fields_included():
    # create a patient profile object with some fields
    pat_user = models.User(id=2, email="pat@example.com", full_name="Patient One")
    patient = models.PatientProfile(
        id=5,
        user=pat_user,
        date_of_birth=datetime(1990, 1, 1),
        sex="M",
        height_cm=172.5,
        weight_kg=68.0,
        medical_history="None",
        medications="None",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    def fake_doctor():
        user = models.User(id=1, email="doc2@example.com", full_name="Dr. Field")
        user.role = models.Role(id=2, name="doctor")
        user.doctor_patients = [patient]
        return user

    app.dependency_overrides[security.get_doctor_user] = fake_doctor
    response = client.get("/api/doctor/patients")
    assert response.status_code == 200
    data = response.json()
    assert data["message"].startswith("assigned patients")
    assert isinstance(data["patients"], list) and len(data["patients"]) == 1
    entry = data["patients"][0]
    # verify that profile fields appear
    assert entry["id"] == 5
    assert entry["full_name"] == "Patient One"
    assert entry["date_of_birth"].startswith("1990-01-01")
    assert entry["sex"] == "M"
    assert entry["height_cm"] == 172.5
    assert entry["weight_kg"] == 68.0
    assert entry["medical_history"] == "None"
    assert entry["medications"] == "None"
    # prediction-related keys should exist even if null
    assert "latest_ckd_stage" in entry
    assert entry["latest_ckd_stage"] is None

    app.dependency_overrides.pop(security.get_doctor_user, None)
