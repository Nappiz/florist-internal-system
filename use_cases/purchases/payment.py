from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from models.purchase_payment_model import PurchasePayment
from use_cases.cashflow.post_payment import post_payment
from use_cases.cashflow.common import require_accounts
from crud import purchases_crud
from use_cases.common.persistence import finish
from use_cases.audit.record import record
from use_cases.purchases.response import require,response


def payment(db,actor,identity,data):
    purchase=require(db,identity)
    if purchase.status=='cancelled': raise HTTPException(409,'Pembelian dibatalkan tidak dapat menerima pembayaran baru.')
    payments=purchases_crud.payments(db,identity)
    previous=next((row for row in payments if row.payment_key==data.payment_key),None)
    if previous:
        if any(getattr(previous,key)!=value for key,value in data.model_dump().items()): raise HTTPException(409,'Payment key sudah digunakan dengan isi berbeda.')
        return response(db,purchase)
    if data.payment_date>datetime.now(ZoneInfo('Asia/Jakarta')).date(): raise HTTPException(422,'Tanggal pembayaran tidak boleh di masa depan.')
    paid=sum(row.amount for row in payments if row.reversed_at is None)+data.amount
    if paid>purchase.total_amount: raise HTTPException(409,'Pembayaran melebihi total pembelian.')
    require_accounts(db,[data.cash_account_id],data.payment_date)
    payment_row=PurchasePayment(id=uuid4(),purchase_id=identity,created_by=actor.user.id,**data.model_dump())
    db.add(payment_row)
    db.flush()
    post_payment(db,actor,"purchase_payment",payment_row)
    purchase.payment_status='paid' if paid==purchase.total_amount else 'partial'
    purchase.updated_by=actor.user.id
    record(db,actor,'payment','purchase',identity,{'amount':data.amount,'payment_key':str(data.payment_key)})
    finish(db)
    return response(db,purchase)
