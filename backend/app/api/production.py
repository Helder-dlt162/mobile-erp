from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import ProductionOrder
from app.schemas import ProductionOrderCreate, ProductionOrderRead

router = APIRouter(prefix="/production-orders", tags=["Produção"])


@router.get("", response_model=list[ProductionOrderRead])
def list_orders(_: CurrentUser, db: DbSession) -> list[ProductionOrder]:
    return list(db.scalars(select(ProductionOrder).order_by(ProductionOrder.id.desc())).all())


@router.post("", response_model=ProductionOrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: ProductionOrderCreate, _: CurrentUser, db: DbSession) -> ProductionOrder:
    if db.scalar(select(ProductionOrder).where(ProductionOrder.code == payload.code)):
        raise HTTPException(status_code=409, detail="Código de OP já cadastrado")
    order = ProductionOrder(**payload.model_dump(), progress=0, status="Aguardando")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
