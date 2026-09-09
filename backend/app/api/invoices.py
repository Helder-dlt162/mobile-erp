from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import CurrentUser, DbSession
from app.models import InventoryItem, InvoiceItem, PayableAccount, PurchaseInvoice, Supplier
from app.schemas import PurchaseInvoiceCreate, PurchaseInvoiceRead

router = APIRouter(prefix="/invoices", tags=["Notas fiscais"])


@router.get("", response_model=list[PurchaseInvoiceRead])
def list_invoices(_: CurrentUser, db: DbSession) -> list[PurchaseInvoice]:
    statement = select(PurchaseInvoice).options(selectinload(PurchaseInvoice.items)).order_by(PurchaseInvoice.id.desc())
    return list(db.scalars(statement).unique().all())


@router.post("", response_model=PurchaseInvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: PurchaseInvoiceCreate, _: CurrentUser, db: DbSession) -> PurchaseInvoice:
    if db.scalar(select(PurchaseInvoice).where(PurchaseInvoice.number == payload.number)):
        raise HTTPException(status_code=409, detail="Número de NF já cadastrado")
    supplier = db.get(Supplier, payload.supplier_id) if payload.supplier_id else None
    if payload.supplier_id and not supplier:
        raise HTTPException(status_code=422, detail="Fornecedor não encontrado")
    items: list[InvoiceItem] = []
    total = Decimal("0")
    for item_payload in payload.items:
        inventory_item = db.scalar(select(InventoryItem).where(InventoryItem.sku == item_payload.sku))
        if not inventory_item:
            raise HTTPException(status_code=422, detail=f"SKU {item_payload.sku} não está cadastrado no estoque")
        item_total = item_payload.quantity * item_payload.unit_cost
        total += item_total
        items.append(InvoiceItem(inventory_item_id=inventory_item.id, total=item_total, **item_payload.model_dump()))
    supplier_name = supplier.trade_name if supplier else payload.supplier
    invoice = PurchaseInvoice(number=payload.number, supplier=supplier_name, supplier_id=supplier.id if supplier else None, issue_date=payload.issue_date, due_date=payload.due_date, payment_method=payload.payment_method, description=payload.description, barcode=payload.barcode, category=payload.category, notes=payload.notes, total=total, items=items)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/{invoice_id}/receive", response_model=PurchaseInvoiceRead)
def receive_invoice(invoice_id: int, _: CurrentUser, db: DbSession) -> PurchaseInvoice:
    invoice = db.scalar(select(PurchaseInvoice).options(selectinload(PurchaseInvoice.items)).where(PurchaseInvoice.id == invoice_id))
    if not invoice:
        raise HTTPException(status_code=404, detail="NF não encontrada")
    if invoice.status == "Recebida":
        raise HTTPException(status_code=409, detail="NF já recebida no estoque")
    for invoice_item in invoice.items:
        inventory_item = db.get(InventoryItem, invoice_item.inventory_item_id)
        if not inventory_item:
            raise HTTPException(status_code=422, detail=f"Material do SKU {invoice_item.sku} não encontrado")
        inventory_item.stock += invoice_item.quantity
        inventory_item.last_entry = "Hoje"
        inventory_item.state = "Abaixo do mínimo" if inventory_item.stock <= inventory_item.minimum_stock else "Normal"
        inventory_item.color = "red" if inventory_item.stock <= inventory_item.minimum_stock else "green"
    invoice.status = "Recebida"
    payable = db.scalar(select(PayableAccount).where(PayableAccount.invoice_id == invoice.id))
    if not payable:
        payable = PayableAccount(
            invoice_id=invoice.id,
            supplier_id=invoice.supplier_id,
            supplier_name=invoice.supplier,
            due_date=invoice.due_date or invoice.issue_date,
            purchase_date=invoice.issue_date,
            amount=invoice.total,
            payment_method=invoice.payment_method,
            description=invoice.description or f"NF de entrada {invoice.number}",
            barcode=invoice.barcode,
            category=invoice.category,
            notes=invoice.notes,
        )
        db.add(payable)
    db.commit()
    db.refresh(invoice)
    return invoice
