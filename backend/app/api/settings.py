from typing import Any

from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import AppSetting
from app.schemas import AppSettingRead, AppSettingUpdate

router = APIRouter(prefix="/settings", tags=["Configurações"])

DEFAULTS: dict[str, dict[str, Any]] = {
    "general": {"company_name": "Ateliê Móveis", "timezone": "America/Sao_Paulo", "date_format": "DD/MM/YYYY", "currency": "BRL", "language": "pt-BR"},
    "production": {"default_shift": "08:00-18:00", "working_days": "Segunda a sexta", "allow_backdated_entries": False},
    "inventory": {"negative_stock": False, "default_movement_reason": "Ajuste manual", "low_stock_alert": True},
    "purchasing": {"require_supplier_on_invoice": True, "auto_create_payable": False},
    "finance": {"due_alert_days": 7, "default_payment_method": "Boleto", "allow_overdue_payment": True},
    "fiscal": {"provider": "SEFAZ", "document_type": "NF-e", "environment": "homologacao", "state": "PR", "issuer_cnpj": "", "state_registration": "", "series": "1", "next_number": "1", "technical_contact": "", "certificate_type": "A1", "certificate_reference": "", "certificate_expires_at": "", "csc_reference": "", "status": "Não configurado"},
}


@router.get("", response_model=list[AppSettingRead])
def list_settings(_: CurrentUser, db: DbSession) -> list[AppSettingRead]:
    existing = {setting.category: setting for setting in db.scalars(select(AppSetting)).all()}
    result: list[AppSettingRead] = []
    for category, defaults in DEFAULTS.items():
        result.append(AppSettingRead(category=category, payload={**defaults, **(existing[category].payload if category in existing else {})}))
    return result


@router.put("/{category}", response_model=AppSettingRead)
def update_settings(category: str, update: AppSettingUpdate, _: CurrentUser, db: DbSession) -> AppSettingRead:
    current = db.scalar(select(AppSetting).where(AppSetting.category == category))
    base = DEFAULTS.get(category, {})
    if current:
        current.payload = {**base, **update.payload}
    else:
        current = AppSetting(category=category, payload={**base, **update.payload})
        db.add(current)
    db.commit()
    db.refresh(current)
    return AppSettingRead(category=current.category, payload=current.payload)