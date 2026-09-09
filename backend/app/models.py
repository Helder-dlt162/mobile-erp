from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class OrderStatus(StrEnum):
    IN_PROGRESS = "Em produção"
    WAITING = "Aguardando"
    COMPLETED = "Concluída"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="admin")
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AppSetting(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    document: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    legal_name: Mapped[str] = mapped_column(String(180))
    trade_name: Mapped[str] = mapped_column(String(180))
    email: Mapped[str] = mapped_column(String(180))
    phone: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(255), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    state: Mapped[str] = mapped_column(String(2), default="")
    zip_code: Mapped[str] = mapped_column(String(12), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    invoices: Mapped[list["PurchaseInvoice"]] = relationship(back_populates="supplier_record")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    document: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    legal_name: Mapped[str] = mapped_column(String(180))
    trade_name: Mapped[str] = mapped_column(String(180), default="")
    email: Mapped[str] = mapped_column(String(180), default="")
    phone: Mapped[str] = mapped_column(String(30), default="")
    address: Mapped[str] = mapped_column(String(255), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    state: Mapped[str] = mapped_column(String(2), default="")
    zip_code: Mapped[str] = mapped_column(String(12), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PayableAccount(Base):
    __tablename__ = "payable_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("purchase_invoices.id"), nullable=True, unique=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    supplier_name: Mapped[str] = mapped_column(String(180), default="")
    due_date: Mapped[str] = mapped_column(String(20))
    purchase_date: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(String(255))
    barcode: Mapped[str] = mapped_column(String(80), default="")
    category: Mapped[str] = mapped_column(String(80), default="Outros")
    status: Mapped[str] = mapped_column(String(20), default="Em aberto")
    notes: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    product: Mapped[str] = mapped_column(String(180))
    quantity: Mapped[int]
    progress: Mapped[int] = mapped_column(default=0)
    station: Mapped[str] = mapped_column(String(80))
    due: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default=OrderStatus.WAITING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    stock: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    unit: Mapped[str] = mapped_column(String(20))
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    state: Mapped[str] = mapped_column(String(40))
    color: Mapped[str] = mapped_column(String(20), default="green")
    last_entry: Mapped[str] = mapped_column(String(30), default="09 set")

    invoice_items: Mapped[list["InvoiceItem"]] = relationship(back_populates="inventory_item")
    movements: Mapped[list["StockMovement"]] = relationship(back_populates="inventory_item")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.id"))
    movement_type: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    reason: Mapped[str] = mapped_column(String(180))
    reference: Mapped[str] = mapped_column(String(80), default="")
    movement_date: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    inventory_item: Mapped[InventoryItem] = relationship(back_populates="movements")


class PurchaseInvoice(Base):
    __tablename__ = "purchase_invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    supplier: Mapped[str] = mapped_column(String(180))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    issue_date: Mapped[str] = mapped_column(String(20))
    due_date: Mapped[str] = mapped_column(String(20), default="")
    payment_method: Mapped[str] = mapped_column(String(40), default="Boleto")
    description: Mapped[str] = mapped_column(String(255), default="NF de entrada")
    barcode: Mapped[str] = mapped_column(String(80), default="")
    category: Mapped[str] = mapped_column(String(80), default="Insumos")
    notes: Mapped[str] = mapped_column(String(255), default="")
    cancellation_reason: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(20), default="Pendente")
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items: Mapped[list["InvoiceItem"]] = relationship(back_populates="invoice", cascade="all, delete-orphan")
    supplier_record: Mapped[Supplier | None] = relationship(back_populates="invoices")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("purchase_invoices.id"))
    inventory_item_id: Mapped[int | None] = mapped_column(ForeignKey("inventory_items.id"), nullable=True)
    sku: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(180))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    invoice: Mapped[PurchaseInvoice] = relationship(back_populates="items")
    inventory_item: Mapped[InventoryItem | None] = relationship(back_populates="invoice_items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(255))
    status_code: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User | None] = relationship()
