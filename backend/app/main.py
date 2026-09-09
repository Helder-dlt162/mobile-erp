from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api import auth, dashboard, finance, inventory, invoices, movements, partners, pricing, production, settings as settings_api
from app.core.config import get_settings
from app.db import Base, SessionLocal, engine
from app.middleware import RequestAuditMiddleware
from app.seed import seed_database

settings = get_settings()


def migrate_existing_schema() -> None:
    inspector = inspect(engine)
    invoice_columns = {column["name"] for column in inspector.get_columns("purchase_invoices")}
    if "supplier_id" not in invoice_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE purchase_invoices ADD COLUMN supplier_id INTEGER REFERENCES suppliers(id)"))
    payable_columns = {column["name"] for column in inspector.get_columns("payable_accounts")}
    if "invoice_id" not in payable_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE payable_accounts ADD COLUMN invoice_id INTEGER REFERENCES purchase_invoices(id)"))
    for column, definition in {
        "due_date": "VARCHAR(20) DEFAULT ''",
        "payment_method": "VARCHAR(40) DEFAULT 'Boleto'",
        "description": "VARCHAR(255) DEFAULT 'NF de entrada'",
        "barcode": "VARCHAR(80) DEFAULT ''",
        "category": "VARCHAR(80) DEFAULT 'Insumos'",
        "notes": "VARCHAR(255) DEFAULT ''",
    }.items():
        if column not in invoice_columns:
            with engine.begin() as connection:
                connection.execute(text(f"ALTER TABLE purchase_invoices ADD COLUMN {column} {definition}"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_existing_schema()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(RequestAuditMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(production.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(partners.suppliers_router, prefix="/api")
app.include_router(partners.customers_router, prefix="/api")
app.include_router(finance.router, prefix="/api")
app.include_router(movements.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")
app.include_router(pricing.router, prefix="/api")


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "atelier-erp-api", "environment": settings.app_env}
