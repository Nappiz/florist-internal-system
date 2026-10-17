from datetime import UTC, datetime
from uuid import UUID
from fastapi import HTTPException
from crud import cashflow_crud
from use_cases.audit.record import record
from use_cases.cashflow.common import require_superadmin, validate_date, operation, movement
from crud import cash_accounts_crud
from use_cases.common.persistence import finish
from use_cases.common.response import row_response


def reverse_payment(db, actor, transaction_id, data):
    require_superadmin(actor)
    original = cashflow_crud.get(db, transaction_id)
    if original is None:
        raise HTTPException(404, 'Cash transaction tidak ditemukan.')
    if original.source_type not in ('order_payment', 'purchase_payment', 'expense_payment'):
        raise HTTPException(409, 'Hanya payment yang dapat dibalik melalui workflow ini.')
    payment = cashflow_crud.source_payment(db, original.source_type, original.source_id)
    if payment is None:
        raise HTTPException(409, 'Sumber payment tidak ditemukan; jalankan rekonsiliasi.')
    # All posting flows lock the parent before locking accounts; maintain that order.
    parent = cashflow_crud.lock_parent(db, original.source_type, payment)
    payment = cashflow_crud.source_payment(db, original.source_type, original.source_id, lock=True)
    op = operation(db, actor, 'reverse_payment', data, {'transaction_id': str(transaction_id)})
    if op.result:
        return row_response(cashflow_crud.get(db, UUID(op.result['transaction_id'])))
    try:
        if payment.reversed_at is not None or cashflow_crud.reversal(db, original.id) is not None:
            raise HTTPException(409, 'Payment sudah dibalik.')
        if (payment.amount, payment.cash_account_id, payment.payment_date) != (original.amount, original.cash_account_id, original.transaction_date):
            raise HTTPException(409, 'Sumber payment berbeda; rekonsiliasi diperlukan.')
        if data.transaction_date < original.transaction_date:
            raise HTTPException(422, 'Tanggal reversal tidak boleh sebelum payment.')
        account = cash_accounts_crud.get(db, original.cash_account_id, lock=True)
        # Inactive accounts can still be corrected; no new payment is accepted on them.
        validate_date(data.transaction_date, account)
        row = movement(db, actor, account_id=original.cash_account_id, transaction_date=data.transaction_date, direction='OUT' if original.direction == 'IN' else 'IN', amount=original.amount, category=original.category, source_type='refund' if original.source_type == 'order_payment' else 'reversal', source_id=original.id, reason=data.reason, operation_key=op.operation_key, reversal_of_id=original.id)
        payment.reversed_at = datetime.now(UTC)
        db.flush()
        paid = cashflow_crud.paid_amount(db, original.source_type, payment)
        total = parent.amount if original.source_type == 'expense_payment' else parent.total_amount
        parent.payment_status = 'unpaid' if paid == 0 else 'paid' if paid >= total else 'partial'
        if hasattr(parent, 'updated_by'):
            parent.updated_by = actor.user.id
        parent.updated_at = datetime.now(UTC)
        op.result = {'transaction_id': str(row.id)}
        record(db, actor, 'payment_reversal', original.source_type, payment.id, {'reason': data.reason, 'transaction_id': str(row.id), 'operation_key': str(op.operation_key)})
        finish(db)
    except Exception:
        db.rollback()
        raise
    return row_response(row)
