from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ping():
    """Проверка базового эндпоинта /ping"""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health():
    """Проверка эндпоинта здоровья"""
    response = client.get("/health")
    assert response.status_code == 200