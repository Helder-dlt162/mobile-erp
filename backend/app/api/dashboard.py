from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import InventoryItem, ProductionOrder
from app.schemas import DashboardRead

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardRead)
def dashboard(_: CurrentUser, db: DbSession) -> DashboardRead:
    orders = list(db.scalars(select(ProductionOrder).order_by(ProductionOrder.id)).all())
    inventory = list(db.scalars(select(InventoryItem).order_by(InventoryItem.id)).all())
    return DashboardRead(
        production_month=1248,
        occupancy=78.6,
        average_cost=Decimal("148.50"),
        contribution_margin=32.4,
        orders=orders,
        inventory=inventory,
    )
