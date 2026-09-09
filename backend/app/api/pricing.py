from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.schemas import PriceSimulationRead, PriceSimulationRequest

router = APIRouter(prefix="/pricing", tags=["Custos e preços"])


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@router.post("/simulate", response_model=PriceSimulationRead)
def simulate(payload: PriceSimulationRequest, _: CurrentUser) -> PriceSimulationRead:
    divisor = Decimal("1") - (payload.tax + payload.margin) / Decimal("100")
    suggested = payload.cost / divisor
    estimated_tax = suggested * payload.tax / Decimal("100")
    contribution = suggested - payload.cost - estimated_tax
    return PriceSimulationRead(
        cost=money(payload.cost), tax=payload.tax, margin=payload.margin,
        suggested_price=money(suggested), estimated_tax=money(estimated_tax),
        contribution=money(contribution), markup=money(suggested / payload.cost),
        fiscal_status="Pendente: confirme Lucro Real ou Simples Nacional",
    )
