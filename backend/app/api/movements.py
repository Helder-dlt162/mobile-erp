from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import InventoryItem, StockMovement
from app.schemas import StockMovementCreate, StockMovementRead

router = APIRouter(prefix="/stock-movements", tags=["Movimentações de estoque"])


def serialize(movement: StockMovement) -> StockMovementRead:
    return StockMovementRead(
        id=movement.id,
        inventory_item_id=movement.inventory_item_id,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        reason=movement.reason,
        reference=movement.reference,
        movement_date=movement.movement_date,
        item_name=movement.inventory_item.name,
        sku=movement.inventory_item.sku,
    )


@router.get("", response_model=list[StockMovementRead])
def list_movements(_: CurrentUser, db: DbSession) -> list[StockMovementRead]:
    movements = list(db.scalars(select(StockMovement).join(StockMovement.inventory_item).order_by(StockMovement.id.desc())).all())
    return [serialize(movement) for movement in movements]


@router.post("", response_model=StockMovementRead, status_code=status.HTTP_201_CREATED)
def create_movement(payload: StockMovementCreate, _: CurrentUser, db: DbSession) -> StockMovementRead:
    item = db.get(InventoryItem, payload.inventory_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    if payload.movement_type == "Saída" and item.stock < payload.quantity:
        raise HTTPException(status_code=409, detail=f"Saldo insuficiente para {item.sku}. Disponível: {item.stock}")
    item.stock += payload.quantity if payload.movement_type == "Entrada" else -payload.quantity
    item.last_entry = payload.movement_date if payload.movement_type == "Entrada" else item.last_entry
    item.state = "Abaixo do mínimo" if item.stock <= item.minimum_stock else "Normal"
    item.color = "red" if item.stock <= item.minimum_stock else "green"
    movement = StockMovement(**payload.model_dump())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return serialize(movement)