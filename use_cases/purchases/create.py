from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from models.supplier_store_model import SupplierStore
from models.purchase_model import Purchase
from use_cases.common.validation import require_active
from use_cases.common.persistence import finish
from use_cases.audit.record import record
from use_cases.purchases.build_items import build_items
from use_cases.purchases.calculate import calculate
from use_cases.purchases.response import response


def create(db,actor,data):
    require_active(db,SupplierStore,data.supplier_id)
    if data.purchase_date>datetime.now(ZoneInfo('Asia/Jakarta')).date(): raise HTTPException(422,'Tanggal pembelian tidak boleh di masa depan.')
    identity=uuid4()
    values=data.model_dump(exclude={'items'})
    purchase=Purchase(id=identity,purchase_number=f'PUR-{data.purchase_date:%Y%m%d}-{identity.hex[:12].upper()}',created_by=actor.user.id,updated_by=actor.user.id,status='draft',payment_status='unpaid',**values)
    items=build_items(db,purchase,data.items)
    calculate(purchase,items)
    if purchase.total_amount==0: purchase.payment_status='paid'
    db.add(purchase)
    db.flush()
    db.add_all(items)
    record(db,actor,'create','purchase',identity)
    finish(db)
    return response(db,purchase)
