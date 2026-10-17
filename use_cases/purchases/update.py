from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from crud import purchases_crud
from use_cases.common.persistence import finish
from use_cases.audit.record import record
from use_cases.purchases.response import require,response
from use_cases.purchases.build_items import build_items
from use_cases.purchases.calculate import calculate


def update(db,actor,identity,data):
    # Header totals and replacement rows become valid together. Queries used for
    # validation must not flush a partially updated header between those steps.
    with db.no_autoflush:
        return _update(db,actor,identity,data)


def _update(db,actor,identity,data):
    purchase=require(db,identity)
    if purchase.status!='draft': raise HTTPException(409,'Hanya pembelian draft dapat diubah.')
    values=data.model_dump(exclude_unset=True,exclude={'items'})
    if not data.model_fields_set: raise HTTPException(422,'Isi minimal satu field.')
    if any(value is None for key,value in values.items() if key in {'purchase_date','discount_amount','shipping_cost'}): raise HTTPException(422,'Field wajib tidak boleh null.')
    if data.purchase_date and data.purchase_date>datetime.now(ZoneInfo('Asia/Jakarta')).date(): raise HTTPException(422,'Tanggal pembelian tidak boleh di masa depan.')
    if 'items' in data.model_fields_set and data.items is None: raise HTTPException(422,'Item tidak boleh null.')
    for key,value in values.items(): setattr(purchase,key,value)
    if data.items is not None:
        items=build_items(db,purchase,data.items)
        purchases_crud.clear_items(db,identity)
        db.add_all(items)
    else: items=purchases_crud.items(db,identity)
    calculate(purchase,items)
    paid=sum(payment.amount for payment in purchases_crud.payments(db,identity) if payment.reversed_at is None)
    if paid>purchase.total_amount: raise HTTPException(409,'Total baru lebih kecil dari pembayaran tercatat.')
    purchase.payment_status='paid' if paid==purchase.total_amount else ('partial' if paid else 'unpaid')
    purchase.updated_by=actor.user.id
    record(db,actor,'update','purchase',identity,{'fields':sorted(data.model_fields_set)})
    finish(db)
    return response(db,purchase)
