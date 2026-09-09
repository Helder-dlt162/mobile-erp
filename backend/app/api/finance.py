from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import PayableAccount, Supplier
from app.schemas import PayableCreate, PayableRead

router = APIRouter(prefix="/finance/payables", tags=["Financeiro"])


@router.get("", response_model=list[PayableRead])
def list_payables(_: CurrentUser, db: DbSession) -> list[PayableAccount]:
    return list(db.scalars(select(PayableAccount).order_by(PayableAccount.due_date, PayableAccount.id)).all())


@router.post("", response_model=PayableRead, status_code=status.HTTP_201_CREATED)
def create_payable(payload: PayableCreate, _: CurrentUser, db: DbSession) -> PayableAccount:
    supplier = db.get(Supplier, payload.supplier_id) if payload.supplier_id else None
    if payload.supplier_id and not supplier:
        raise HTTPException(status_code=422, detail="Fornecedor não encontrado")
    values = payload.model_dump()
    if supplier:
        values["supplier_name"] = supplier.trade_name
    payable = PayableAccount(**values)
    db.add(payable)
    db.commit()
    db.refresh(payable)
    return payable


@router.post("/{payable_id}/pay", response_model=PayableRead)
def pay_payable(payable_id: int, _: CurrentUser, db: DbSession) -> PayableAccount:
    payable = db.get(PayableAccount, payable_id)
    if not payable:
        raise HTTPException(status_code=404, detail="Conta a pagar não encontrada")
    if payable.status == "Paga":
        raise HTTPException(status_code=409, detail="Conta já está paga")
    payable.status = "Paga"
    db.commit()
    db.refresh(payable)
    return payable