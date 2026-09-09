import os

os.environ["DATABASE_URL"] = "sqlite:///./test_atelier_erp.db"

from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, engine, SessionLocal
from app.seed import seed_database


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_database(db)

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_dashboard() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    dashboard = client.get("/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dashboard.status_code == 200
    assert dashboard.json()["orders"]


def test_protected_route_rejects_anonymous_request() -> None:
    response = client.get("/api/inventory")
    assert response.status_code == 401


def test_price_simulation() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    response = client.post("/api/pricing/simulate", headers={"Authorization": f"Bearer {token}"}, json={"cost": "148.50", "tax": "12.45", "margin": "32"})
    assert response.status_code == 200
    assert response.json()["suggested_price"] == "267.33"
