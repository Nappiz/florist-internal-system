from uuid import UUID
from fastapi import HTTPException
from crud import cashflow_crud
from use_cases.audit.record import record
from use_cases.cashflow.common import require_superadmin, require_accounts, operation, movement
from use_cases.common.persistence import finish
from use_cases.common.response import row_response


def adjust(db, actor, data):
    require_superadmin(actor)
    expected = {'capital_contribution': 'IN', 'owner_withdrawal': 'OUT', 'other_receipt': 'IN', 'other_disbursement': 'OUT'}
    if data.category in expected and data.direction != expected[data.category]:
        raise HTTPException(422, 'Arah adjustment tidak sesuai kategori.')
    op = operation(db, actor, 'adjustment', data)
    if op.result:
        return row_response(cashflow_crud.get(db, UUID(op.result['transaction_id'])))
    try:
        require_accounts(db, [data.cash_account_id], data.transaction_date)
        row = movement(db, actor, account_id=data.cash_account_id, transaction_date=data.transaction_date, direction=data.direction, amount=data.amount, category=data.category, source_type='adjustment', reason=data.reason, operation_key=op.operation_key)
        op.result = {'transaction_id': str(row.id)}
        record(db, actor, 'cash_adjustment', 'cash_transaction', row.id, data.model_dump(mode='json'))
        finish(db)
    except Exception:
        db.rollback()
        raise
    return row_response(row)
