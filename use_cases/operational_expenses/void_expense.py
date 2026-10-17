from datetime import UTC, datetime
from fastapi import HTTPException
from crud import operational_expenses_crud as crud
from use_cases.operational_expenses.access import require_superadmin,get_authorized
from use_cases.operational_expenses.expense_response import expense_response
from use_cases.common.persistence import finish
from use_cases.audit.record import record


def void_expense(db,actor,expense_id,reason):
    require_superadmin(actor)
    row=get_authorized(db,actor,expense_id,lock=True)
    if not reason.strip(): raise HTTPException(422,'Alasan pembatalan wajib.')
    if row.status=='void': raise HTTPException(409,'Expense sudah void.')
    if crud.paid_amount(db,row.id): raise HTTPException(409,'Pembayaran harus direversal sebelum void.')
    row.status='void'; row.voided_by=actor.user.id; row.voided_at=datetime.now(UTC); row.void_reason=reason; row.updated_at=row.voided_at
    record(db,actor,'void','operating_expense',row.id,{'reason':reason})
    finish(db)
    return expense_response(db,row)
