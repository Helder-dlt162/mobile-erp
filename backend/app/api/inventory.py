from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import InventoryItem
from app.schemas import InventoryCreate, InventoryRead

router = APIRouter(prefix="/inventory", tags=["Estoque"])


@router.get("", response_model=list[InventoryRead])
def list_inventory(_: CurrentUser, db: DbSession) -> list[InventoryItem]:
    return list(db.scalars(select(InventoryItem).order_by(InventoryItem.id)).all())


@router.post("", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(payload: InventoryCreate, _: CurrentUser, db: DbSession) -> InventoryItem:
    if db.scalar(select(InventoryItem).where(InventoryItem.sku == payload.sku)):
        raise HTTPException(status_code=409, detail="SKU já cadastrado")
    below_minimum = payload.stock <= payload.minimum_stock
    item = InventoryItem(
        **payload.model_dump(),
        state="Abaixo do mínimo" if below_minimum else "Normal",
        color="red" if below_minimum else "green",
        last_entry="Hoje",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
