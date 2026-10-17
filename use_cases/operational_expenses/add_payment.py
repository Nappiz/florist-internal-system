from datetime import UTC, datetime, timezone, timedelta
from fastapi import HTTPException
from crud import operational_expenses_crud as crud
from models.expense_payment_model import ExpensePayment
from use_cases.operational_expenses.access import require_superadmin,get_authorized
from use_cases.operational_expenses.expense_response import expense_response
from use_cases.common.persistence import finish,flush
from use_cases.audit.record import record


def add_payment(db,actor,expense_id,data):
    require_superadmin(actor)
    row=get_authorized(db,actor,expense_id,lock=True)
    values=data.model_dump()
    values["proof_url"]=str(data.proof_url) if data.proof_url is not None else None
    existing=crud.payment_by_key(db,data.payment_key)
    if existing is not None:
        if existing.expense_id!=row.id or any(getattr(existing,key)!=value for key,value in values.items()):
            raise HTTPException(409,'Kunci pembayaran sudah digunakan dengan data berbeda.')
        return expense_response(db,row)
    if row.status!='posted': raise HTTPException(409,'Pembayaran hanya untuk expense posted.')
    if data.payment_date>datetime.now(timezone(timedelta(hours=7))).date(): raise HTTPException(422,'Tanggal pembayaran tidak boleh di masa depan.')
    paid=crud.paid_amount(db,row.id)
    if data.amount<=0 or paid+data.amount>row.amount: raise HTTPException(409,'Pembayaran melebihi sisa tagihan.')
    payment=crud.add(db,ExpensePayment(expense_id=row.id,created_by=actor.user.id,**values))
    try:
        flush(db)
        from use_cases.cashflow.post_payment import post_payment
        post_payment(db,actor,'expense_payment',payment)
        row.payment_status='paid' if paid+data.amount==row.amount else 'partial'
        row.updated_at=datetime.now(UTC)
        record(db,actor,'payment','operating_expense',row.id,{'payment_id':str(payment.id),'payment_key':str(payment.payment_key),'amount':payment.amount})
        finish(db)
    except Exception:
        db.rollback()
        raise
    return expense_response(db,row)
