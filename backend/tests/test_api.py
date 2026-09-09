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


def test_create_inventory_item() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    response = client.post(
        "/api/inventory",
        headers={"Authorization": f"Bearer {token}"},
        json={"sku": "MAT-TEST", "name": "Material de teste", "stock": "2", "unit": "un", "minimum_stock": "5"},
    )
    assert response.status_code == 201
    assert response.json()["state"] == "Abaixo do mínimo"


def test_create_production_order() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    response = client.post(
        "/api/production-orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "OP-TEST", "product": "Banqueta de teste", "quantity": 10, "station": "Corte", "due": "15 set, 08:00"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "Aguardando"


def test_invoice_receipt_updates_inventory() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    before = client.get("/api/inventory", headers=headers).json()
    tauari_before = next(item for item in before if item["sku"] == "MAT-001")["stock"]
    invoice = client.post("/api/invoices", headers=headers, json={"number": "NF-TEST-001", "supplier": "Fornecedor de teste", "issue_date": "09/09/2026", "items": [{"sku": "MAT-001", "description": "Madeira Tauari", "quantity": "2", "unit_cost": "35.50"}]})
    assert invoice.status_code == 201
    assert invoice.json()["status"] == "Pendente"
    received = client.post(f"/api/invoices/{invoice.json()['id']}/receive", headers=headers)
    assert received.status_code == 200
    assert received.json()["status"] == "Recebida"
    after = client.get("/api/inventory", headers=headers).json()
    tauari_after = next(item for item in after if item["sku"] == "MAT-001")["stock"]
    assert float(tauari_after) == float(tauari_before) + 2


def test_supplier_customer_and_invoice_link() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    supplier = client.post("/api/suppliers", headers=headers, json={"document": "12345678000199", "legal_name": "Fornecedor MVP Ltda", "trade_name": "Fornecedor MVP", "email": "contato@fornecedormvp.com", "phone": "41999999999", "city": "Curitiba", "state": "PR"})
    assert supplier.status_code == 201
    supplier_id = supplier.json()["id"]
    assert client.get("/api/suppliers?q=Fornecedor MVP", headers=headers).json()[0]["id"] == supplier_id
    customer = client.post("/api/customers", headers=headers, json={"document": "98765432000188", "legal_name": "Cliente MVP Ltda", "trade_name": "Cliente MVP"})
    assert customer.status_code == 201
    invoice = client.post("/api/invoices", headers=headers, json={"number": "NF-SUPPLIER-001", "supplier": "fallback", "supplier_id": supplier_id, "issue_date": "09/09/2026", "items": [{"sku": "MAT-001", "description": "Madeira Tauari", "quantity": "1", "unit_cost": "35.50"}]})
    assert invoice.status_code == 201
    assert invoice.json()["supplier"] == "Fornecedor MVP"


def test_invoice_accepts_multiple_items_and_payable_flow() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    invoice = client.post("/api/invoices", headers=headers, json={"number": "NF-MULTI-001", "supplier": "Fornecedor", "issue_date": "09/09/2026", "items": [{"sku": "MAT-001", "description": "Madeira", "quantity": "1", "unit_cost": "20"}, {"sku": "MAT-024", "description": "Espuma", "quantity": "2", "unit_cost": "5"}]})
    assert invoice.status_code == 201
    assert len(invoice.json()["items"]) == 2
    payable = client.post("/api/finance/payables", headers=headers, json={"supplier_name": "Fornecedor", "due_date": "10/10/2026", "purchase_date": "09/09/2026", "amount": "150.50", "payment_method": "Boleto", "description": "Compra de insumos", "category": "Insumos"})
    assert payable.status_code == 201
    paid = client.post(f"/api/finance/payables/{payable.json()['id']}/pay", headers=headers)
    assert paid.status_code == 200
    assert paid.json()["status"] == "Paga"


def test_receiving_invoice_creates_payable() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    invoice = client.post("/api/invoices", headers=headers, json={"number": "NF-PAYABLE-001", "supplier": "Fornecedor", "issue_date": "09/09/2026", "due_date": "09/10/2026", "payment_method": "PIX", "description": "Compra com financeiro", "items": [{"sku": "MAT-001", "description": "Madeira", "quantity": "1", "unit_cost": "42"}]})
    assert invoice.status_code == 201
    received = client.post(f"/api/invoices/{invoice.json()['id']}/receive", headers=headers)
    assert received.status_code == 200
    payables = client.get("/api/finance/payables", headers=headers).json()
    payable = next(item for item in payables if item["invoice_id"] == invoice.json()["id"])
    assert payable["due_date"] == "09/10/2026"
    assert payable["payment_method"] == "PIX"


def test_admin_can_create_user_with_module_permissions() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post("/api/users", headers=headers, json={"name": "Operador PCP", "email": "pcp@atelier.com", "password": "operador123", "permissions": ["dashboard", "production"]})
    assert created.status_code == 201
    assert created.json()["permissions"] == ["dashboard", "production"]
    listed = client.get("/api/users", headers=headers)
    assert any(user["email"] == "pcp@atelier.com" for user in listed.json())


def test_stock_movement_updates_balance_and_rejects_overdraft() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    inventory = client.get("/api/inventory", headers=headers).json()
    item = next(item for item in inventory if item["sku"] == "MAT-001")
    before = float(item["stock"])
    movement = client.post("/api/stock-movements", headers=headers, json={"inventory_item_id": item["id"], "movement_type": "Saída", "quantity": "1", "reason": "Consumo de teste", "reference": "OP-TEST", "movement_date": "09/09/2026"})
    assert movement.status_code == 201
    after = client.get("/api/inventory", headers=headers).json()
    assert float(next(entry for entry in after if entry["id"] == item["id"])["stock"]) == before - 1
    overdraft = client.post("/api/stock-movements", headers=headers, json={"inventory_item_id": item["id"], "movement_type": "Saída", "quantity": "999999", "reason": "Saída inválida", "movement_date": "09/09/2026"})
    assert overdraft.status_code == 409


def test_settings_include_fiscal_sefaz_configuration() -> None:
    login = client.post("/api/auth/login", json={"email": "admin@atelier.com", "password": "atelier123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    settings = client.get("/api/settings", headers=headers)
    assert settings.status_code == 200
    fiscal = next(item for item in settings.json() if item["category"] == "fiscal")
    assert fiscal["payload"]["provider"] == "SEFAZ"
    updated = client.put("/api/settings/fiscal", headers=headers, json={"payload": {"state": "SP", "environment": "homologacao"}})
    assert updated.status_code == 200
    assert updated.json()["payload"]["state"] == "SP"
