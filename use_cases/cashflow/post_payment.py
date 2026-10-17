from fastapi import HTTPException
from crud import cashflow_crud
from use_cases.cashflow.common import require_accounts, movement


def post_payment(db, actor, source_type, payment, *, operation_key=None):
    """Append a payment movement inside the caller's parent-locked transaction; never commit."""
    if source_type not in ('order_payment', 'purchase_payment', 'expense_payment'):
        raise HTTPException(422, 'Sumber payment tidak valid.')
    if not getattr(actor.user, 'is_active', True):
        raise HTTPException(403, 'Pengguna tidak aktif.')
    if payment.id is None or payment.cash_account_id is None or payment.amount <= 0 or payment.amount > 999999999999999:
        raise HTTPException(422, 'Payment wajib memiliki identitas, cash account, dan jumlah valid.')
    if getattr(payment, 'reversed_at', None) is not None:
        raise HTTPException(409, 'Payment sudah dibalik.')
    require_accounts(db, [payment.cash_account_id], payment.payment_date)
    direction = 'IN' if source_type == 'order_payment' else 'OUT'
    existing = cashflow_crud.by_source(db, source_type, payment.id)
    if existing is not None:
        if (existing.cash_account_id, existing.amount, existing.transaction_date, existing.direction) != (payment.cash_account_id, payment.amount, payment.payment_date, direction):
            raise HTTPException(409, 'Movement payment bertentangan dengan sumber.')
        return existing
    category = {'order_payment': 'sales_payment', 'purchase_payment': 'material_purchase', 'expense_payment': 'operating_expense'}[source_type]
    if source_type == 'expense_payment':
        category = cashflow_crud.expense_category(db, payment.expense_id) or category
    row = movement(db, actor, account_id=payment.cash_account_id, transaction_date=payment.payment_date, direction=direction, amount=payment.amount, category=category, source_type=source_type, source_id=payment.id, reason=getattr(payment, 'notes', None), operation_key=operation_key)
    db.flush()
    return row
