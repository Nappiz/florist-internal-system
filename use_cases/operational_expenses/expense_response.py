from use_cases.common.response import row_response
from crud import operational_expenses_crud as crud


def expense_response(db,row):
    result=row_response(row)
    paid=crud.paid_amount(db,row.id)
    result.update(paid_amount=paid,remaining_amount=row.amount-paid,payment_status='paid' if paid>=row.amount else ('partial' if paid else 'unpaid'))
    result['payments']=[row_response(payment) for payment in crud.payments(db,row.id)]
    result['receipts']=[{key:getattr(receipt,key) for key in ('id','expense_id','mime_type','size_bytes','original_name','created_at')} for receipt in crud.receipts(db,row.id)]
    return result
