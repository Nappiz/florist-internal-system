from fastapi import HTTPException
from crud import cashflow_crud
from use_cases.audit.record import record
from use_cases.cashflow.common import require_superadmin, require_accounts, operation, movement
from use_cases.common.persistence import finish
from use_cases.common.response import row_response


def transfer(db, actor, data):
    require_superadmin(actor)
    if data.from_account_id == data.to_account_id:
        raise HTTPException(422, 'Rekening asal dan tujuan harus berbeda.')
    op = operation(db, actor, 'transfer', data)
    if op.result:
        return {'operation_key': op.operation_key, 'transactions': [row_response(row) for row in cashflow_crud.by_operation(db, op.operation_key)]}
    try:
        require_accounts(db, [data.from_account_id, data.to_account_id], data.transaction_date)
        rows = [movement(db, actor, account_id=identity, transaction_date=data.transaction_date, direction=direction, amount=data.amount, category='internal_transfer', source_type='transfer', reason=data.reason, operation_key=op.operation_key) for identity, direction in ((data.from_account_id, 'OUT'), (data.to_account_id, 'IN'))]
        op.result = {'transaction_ids': [str(row.id) for row in rows]}
        record(db, actor, 'cash_transfer', 'cash_transaction', rows[0].id, data.model_dump(mode='json'))
        finish(db)
    except Exception:
        db.rollback()
        raise
    return {'operation_key': op.operation_key, 'transactions': [row_response(row) for row in rows]}
