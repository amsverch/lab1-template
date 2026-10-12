from app.models import Base          # <-- берём Base отсюда, где она реально создана
from app.database import engine, SessionLocal
from app.main import app
import pytest
from fastapi.testclient import TestClient



# Фикстура для создания чистой БД перед каждым тестом
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    yield SessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


# Тест 1: Создание человека (проверка статуса 201 и заголовка Location)
def test_create_person(client):
    payload = {"name": "Alice", "age": 30}
    r = client.post("/persons", json=payload)
    assert r.status_code == 201
    assert "Location" in r.headers


# Тест 2: Получение списка (пустой список при старте) — ИСПРАВЛЕНО
def test_get_all_persons_empty(client):
    r = client.get("/persons")
    assert r.status_code == 200
    assert r.json() == ''


# Тест 3: Получение несуществующего человека (проверка 404)
def test_get_person_not_found(client):
    r = client.get("/persons/999")
    assert r.status_code == 404


# Тест 4: Обновление человека
def test_update_person(client):
    # Сначала создаем
    p = client.post("/persons", json={"name": "Bob", "age": 25})
    pid = int(p.headers["Location"].split("/")[-1])

    # Обновляем
    r = client.patch(f"/persons/{pid}", json={"age": 26})
    assert r.status_code == 200
    assert r.json()["age"] == 26


# Тест 5: Удаление человека
def test_delete_person(client):
    # Создаем
    p = client.post("/persons", json={"name": "Carol", "age": 40})
    pid = int(p.headers["Location"].split("/")[-1])

    # Удаляем
    r = client.delete(f"/persons/{pid}")
    assert r.status_code == 204

    # Проверяем, что его больше нет
    r2 = client.get(f"/persons/{pid}")
    assert r2.status_code == 404
