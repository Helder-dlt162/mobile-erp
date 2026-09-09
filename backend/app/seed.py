from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import InventoryItem, ProductionOrder, User


ORDERS = [
    {"code": "OP-2408", "product": "Cadeira Lina · Natural", "quantity": 180, "progress": 72, "station": "Montagem", "due": "Hoje, 16:00", "status": "Em produção"},
    {"code": "OP-2407", "product": "Banqueta Oca · Nogueira", "quantity": 96, "progress": 41, "station": "Usinagem", "due": "Amanhã, 10:00", "status": "Em produção"},
    {"code": "OP-2406", "product": "Cadeira Lina · Preta", "quantity": 240, "progress": 100, "station": "Expedição", "due": "Concluída", "status": "Concluída"},
    {"code": "OP-2405", "product": "Banqueta Oca · Natural", "quantity": 120, "progress": 0, "station": "Corte", "due": "12 set, 08:00", "status": "Aguardando"},
]

INVENTORY = [
    {"sku": "MAT-001", "name": "Madeira Tauari · 25 mm", "stock": Decimal("18.4"), "unit": "m³", "minimum_stock": Decimal("8"), "state": "Normal", "color": "green"},
    {"sku": "MAT-024", "name": "Espuma D28 · 40 mm", "stock": Decimal("132"), "unit": "un", "minimum_stock": Decimal("60"), "state": "Normal", "color": "green"},
    {"sku": "MAT-017", "name": "Tecido Linho Cru", "stock": Decimal("38"), "unit": "m", "minimum_stock": Decimal("30"), "state": "Repor em breve", "color": "yellow"},
    {"sku": "MAT-031", "name": "Verniz PU Acetinado", "stock": Decimal("12"), "unit": "L", "minimum_stock": Decimal("20"), "state": "Abaixo do mínimo", "color": "red"},
]


def seed_database(db: Session) -> None:
    if db.scalar(select(User).limit(1)) is None:
        db.add(User(name="Rafael Silva", email="admin@atelier.com", password_hash=hash_password("atelier123"), role="admin"))
    if db.scalar(select(ProductionOrder).limit(1)) is None:
        db.add_all(ProductionOrder(**order) for order in ORDERS)
    if db.scalar(select(InventoryItem).limit(1)) is None:
        db.add_all(InventoryItem(**item) for item in INVENTORY)
    db.commit()
