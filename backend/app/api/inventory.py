from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import InventoryItem, InvoiceItem, PurchaseInvoice
from app.schemas import InventoryCreate, InventoryRead, InventoryUpdate

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


@router.put("/{item_id}", response_model=InventoryRead)
def update_inventory_item(item_id: int, payload: InventoryUpdate, _: CurrentUser, db: DbSession) -> InventoryItem:
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    item.state = "Abaixo do mínimo" if item.stock <= item.minimum_stock else "Normal"
    item.color = "red" if item.stock <= item.minimum_stock else "green"
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(item_id: int, _: CurrentUser, db: DbSession) -> None:
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    received_link = db.query(InvoiceItem).join(PurchaseInvoice).filter(InvoiceItem.inventory_item_id == item_id, PurchaseInvoice.status == "Recebida").first()
    if received_link:
        raise HTTPException(status_code=409, detail="Material possui entradas fiscais recebidas e não pode ser excluído")
    db.delete(item)
    db.commit()
