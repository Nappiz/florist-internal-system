from fastapi import HTTPException
from crud import operational_expenses_crud as crud
from use_cases.operational_expenses.access import get_authorized,require_draft
from use_cases.common.persistence import finish
from use_cases.audit.record import record


def delete_expense(db,actor,expense_id):
    row=get_authorized(db,actor,expense_id,lock=True)
    require_draft(row)
    if crud.payments(db,row.id): raise HTTPException(409,'Expense dengan histori pembayaran tidak dapat dihapus.')
    from services.expense_receipt_storage import remove_receipt
    receipts=crud.receipts(db,row.id)
    names=[receipt.storage_name for receipt in receipts]
    for receipt in receipts: db.delete(receipt)
    record(db,actor,'delete','operating_expense',row.id)
    crud.delete(db,row); finish(db)
    for name in names: remove_receipt(name)
