from fastapi import HTTPException
from crud import operational_expenses_crud as crud
from use_cases.operational_expenses.access import get_authorized
from services.expense_receipt_storage import receipt_path


def download_receipt(db,actor,expense_id,receipt_id):
    row=get_authorized(db,actor,expense_id)
    receipt=crud.receipt(db,receipt_id)
    if receipt is None or receipt.expense_id!=row.id: raise HTTPException(404,'Receipt tidak ditemukan.')
    path=receipt_path(receipt.storage_name)
    if not path.is_file(): raise HTTPException(404,'File receipt tidak ditemukan.')
    return path,receipt.mime_type,receipt.original_name
