from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str


class AppSettingRead(BaseModel):
    category: str
    payload: dict[str, Any]


class AppSettingUpdate(BaseModel):
    payload: dict[str, Any]


class SupplierBase(BaseModel):
    document: str = Field(min_length=8, max_length=20)
    legal_name: str = Field(min_length=2, max_length=180)
    trade_name: str = Field(min_length=2, max_length=180)
    email: str = Field(min_length=3, max_length=180)
    phone: str = Field(min_length=8, max_length=30)
    address: str = Field(default="", max_length=255)
    city: str = Field(default="", max_length=100)
    state: str = Field(default="", min_length=0, max_length=2)
    zip_code: str = Field(default="", max_length=12)


class SupplierCreate(SupplierBase):
    pass


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CustomerBase(BaseModel):
    document: str = Field(min_length=8, max_length=20)
    legal_name: str = Field(min_length=2, max_length=180)
    trade_name: str = Field(default="", max_length=180)
    email: str = Field(default="", max_length=180)
    phone: str = Field(default="", max_length=30)
    address: str = Field(default="", max_length=255)
    city: str = Field(default="", max_length=100)
    state: str = Field(default="", max_length=2)
    zip_code: str = Field(default="", max_length=12)


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PayableCreate(BaseModel):
    invoice_id: int | None = None
    supplier_id: int | None = None
    supplier_name: str = Field(default="", max_length=180)
    due_date: str = Field(min_length=8, max_length=20)
    purchase_date: str = Field(min_length=8, max_length=20)
    amount: Decimal = Field(gt=0)
    payment_method: str = Field(min_length=2, max_length=40)
    description: str = Field(min_length=2, max_length=255)
    barcode: str = Field(default="", max_length=80)
    category: str = Field(default="Outros", max_length=80)
    notes: str = Field(default="", max_length=255)


class PayableRead(PayableCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str


class ProductionOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    product: str
    quantity: int
    progress: int
    station: str
    due: str
    status: str


class InventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    stock: Decimal
    unit: str
    minimum_stock: Decimal
    state: str
    color: str
    last_entry: str


class InventoryCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=30)
    name: str = Field(min_length=2, max_length=180)
    stock: Decimal = Field(ge=0)
    unit: str = Field(min_length=1, max_length=20)
    minimum_stock: Decimal = Field(ge=0)


class InventoryUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    unit: str = Field(min_length=1, max_length=20)
    minimum_stock: Decimal = Field(ge=0)


class StockMovementCreate(BaseModel):
    inventory_item_id: int
    movement_type: str = Field(pattern="^(Entrada|Saída)$")
    quantity: Decimal = Field(gt=0)
    reason: str = Field(min_length=2, max_length=180)
    reference: str = Field(default="", max_length=80)
    movement_date: str = Field(min_length=8, max_length=20)


class StockMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_item_id: int
    movement_type: str
    quantity: Decimal
    reason: str
    reference: str
    movement_date: str
    item_name: str
    sku: str


class InvoiceItemCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=30)
    description: str = Field(min_length=2, max_length=180)
    quantity: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(gt=0)


class InvoiceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    description: str
    quantity: Decimal
    unit_cost: Decimal
    total: Decimal


class PurchaseInvoiceCreate(BaseModel):
    number: str = Field(min_length=1, max_length=40)
    supplier: str = Field(min_length=2, max_length=180)
    supplier_id: int | None = None
    issue_date: str = Field(min_length=8, max_length=20)
    due_date: str = Field(default="", max_length=20)
    payment_method: str = Field(default="Boleto", max_length=40)
    description: str = Field(default="NF de entrada", max_length=255)
    barcode: str = Field(default="", max_length=80)
    category: str = Field(default="Insumos", max_length=80)
    notes: str = Field(default="", max_length=255)
    items: list[InvoiceItemCreate] = Field(min_length=1)


class PurchaseInvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    supplier: str
    issue_date: str
    due_date: str
    payment_method: str
    description: str
    barcode: str
    category: str
    notes: str
    status: str
    total: Decimal
    items: list[InvoiceItemRead]


class DashboardRead(BaseModel):
    production_month: int
    occupancy: float
    average_cost: Decimal
    contribution_margin: float
    orders: list[ProductionOrderRead]
    inventory: list[InventoryRead]


class ProductionOrderCreate(BaseModel):
    code: str = Field(min_length=3, max_length=30)
    product: str = Field(min_length=3, max_length=180)
    quantity: int = Field(gt=0)
    station: str = Field(min_length=2, max_length=80)
    due: str = Field(min_length=2, max_length=80)


class PriceSimulationRequest(BaseModel):
    cost: Decimal = Field(gt=0)
    tax: Decimal = Field(ge=0, lt=100)
    margin: Decimal = Field(ge=0, lt=100)


class PriceSimulationRead(BaseModel):
    cost: Decimal
    tax: Decimal
    margin: Decimal
    suggested_price: Decimal
    estimated_tax: Decimal
    contribution: Decimal
    markup: Decimal
    fiscal_status: str
