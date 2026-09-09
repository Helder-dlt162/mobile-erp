from decimal import Decimal

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
