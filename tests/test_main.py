import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base
from app.database import get_db

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def test_create_person(client):
    payload = {"name": "Alice", "age": 30}
    r = client.post("/api/v1/persons", json=payload)
    assert r.status_code == 201
    assert "Location" in r.headers


def test_get_all_persons_empty(client):
    r = client.get("/api/v1/persons")
    assert r.status_code == 200
    assert r.json() == []


def test_get_person_not_found(client):
    r = client.get("/api/v1/persons/999")
    assert r.status_code == 404


def test_update_person(client):
    payload = {"name": "Bob", "age": 25}
    r = client.post("/api/v1/persons", json=payload)
    assert r.status_code == 201

    person_id = int(r.headers["Location"].rstrip("/").split("/")[-1])

    r = client.patch(
        f"/api/v1/persons/{person_id}",
        json={"name": "Robert", "age": 26},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Robert"


def test_delete_person(client):
    payload = {"name": "Carol", "age": 35}
    r = client.post("/api/v1/persons", json=payload)
    assert r.status_code == 201

    person_id = int(r.headers["Location"].rstrip("/").split("/")[-1])

    r = client.delete(f"/api/v1/persons/{person_id}")
    assert r.status_code == 204
