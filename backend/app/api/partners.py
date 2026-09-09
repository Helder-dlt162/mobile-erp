from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select

from app.core.dependencies import CurrentUser, DbSession
from app.models import Customer, PurchaseInvoice, Supplier
from app.schemas import CustomerCreate, CustomerRead, SupplierCreate, SupplierRead

suppliers_router = APIRouter(prefix="/suppliers", tags=["Fornecedores"])
customers_router = APIRouter(prefix="/customers", tags=["Clientes"])


@suppliers_router.get("", response_model=list[SupplierRead])
def list_suppliers(_: CurrentUser, db: DbSession, q: str = Query(default="", max_length=100)) -> list[Supplier]:
    statement = select(Supplier).order_by(Supplier.trade_name)
    if q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Supplier.trade_name.ilike(term), Supplier.legal_name.ilike(term), Supplier.document.ilike(term)))
    return list(db.scalars(statement).all())


@suppliers_router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, _: CurrentUser, db: DbSession) -> Supplier:
    if db.scalar(select(Supplier).where(Supplier.document == payload.document)):
        raise HTTPException(status_code=409, detail="CNPJ/CPF já cadastrado")
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@suppliers_router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(supplier_id: int, payload: SupplierCreate, _: CurrentUser, db: DbSession) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    duplicate = db.scalar(select(Supplier).where(Supplier.document == payload.document, Supplier.id != supplier_id))
    if duplicate:
        raise HTTPException(status_code=409, detail="CNPJ/CPF já cadastrado")
    for field, value in payload.model_dump().items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@suppliers_router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: int, _: CurrentUser, db: DbSession) -> None:
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    if db.scalar(select(PurchaseInvoice).where(PurchaseInvoice.supplier_id == supplier_id)):
        raise HTTPException(status_code=409, detail="Fornecedor possui NFs vinculadas e não pode ser excluído")
    db.delete(supplier)
    db.commit()


@customers_router.get("", response_model=list[CustomerRead])
def list_customers(_: CurrentUser, db: DbSession, q: str = Query(default="", max_length=100)) -> list[Customer]:
    statement = select(Customer).order_by(Customer.legal_name)
    if q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Customer.legal_name.ilike(term), Customer.trade_name.ilike(term), Customer.document.ilike(term)))
    return list(db.scalars(statement).all())


@customers_router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, _: CurrentUser, db: DbSession) -> Customer:
    if db.scalar(select(Customer).where(Customer.document == payload.document)):
        raise HTTPException(status_code=409, detail="CNPJ/CPF já cadastrado")
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@customers_router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, payload: CustomerCreate, _: CurrentUser, db: DbSession) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    duplicate = db.scalar(select(Customer).where(Customer.document == payload.document, Customer.id != customer_id))
    if duplicate:
        raise HTTPException(status_code=409, detail="CNPJ/CPF já cadastrado")
    for field, value in payload.model_dump().items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@customers_router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, _: CurrentUser, db: DbSession) -> None:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(customer)
    db.commit()
