from fastapi import HTTPException
from crud import cashflow_crud, cash_accounts_crud
from use_cases.audit.record import record
from use_cases.cashflow.common import require_superadmin, require_accounts, operation
from use_cases.cashflow.post_payment import post_payment
from use_cases.common.persistence import finish
from use_cases.common.response import row_response


def backfill(db, actor, data):
    require_superadmin(actor)
    keys = [(item.source_type, item.payment_id) for item in data.mappings]
    if len(set(keys)) != len(keys):
        raise HTTPException(422, 'Mapping payment ganda.')
    # Lock every parent first in deterministic order, then every account.
    mapped = []
    for item in sorted(data.mappings, key=lambda row: (row.source_type, str(row.payment_id))):
        payment = cashflow_crud.source_payment(db, item.source_type, item.payment_id)
        if payment is None:
            raise HTTPException(404, 'Historical payment tidak ditemukan.')
        model, column = cashflow_crud.parent_model(item.source_type)
        mapped.append((item, payment, model.__tablename__, str(getattr(payment, column))))
    for item, payment, _, _ in sorted(mapped, key=lambda row: (row[2], row[3])):
        cashflow_crud.lock_parent(db, item.source_type, payment)
    op = operation(db, actor, 'backfill', data)
    if op.result:
        return {'operation_key': op.operation_key, 'transactions': [row_response(row) for row in cashflow_crud.by_operation(db, op.operation_key)]}
    try:
        accounts = cash_accounts_crud.lock_many(db, {item.cash_account_id for item in data.mappings})
        account_map = {row.id: row for row in accounts}
        if len(account_map) != len({item.cash_account_id for item in data.mappings}):
            raise HTTPException(404, 'Cash account tidak ditemukan.')
        rows = []
        for item, _, _, _ in mapped:
            account = account_map[item.cash_account_id]
            if account.history_mode != 'backfill':
                raise HTTPException(409, 'Rekening saldo awal tidak boleh menerima historical backfill; mencegah saldo ganda.')
            payment = cashflow_crud.source_payment(db, item.source_type, item.payment_id, lock=True)
            if payment.cash_account_id not in (None, item.cash_account_id):
                raise HTTPException(409, 'Payment sudah dipetakan ke cash account berbeda.')
            existing = cashflow_crud.by_source(db, item.source_type, item.payment_id)
            if existing is not None:
                raise HTTPException(409, 'Payment sudah memiliki movement. Ulangi menggunakan operation key awal.')
            payment.cash_account_id = item.cash_account_id
            row = post_payment(db, actor, item.source_type, payment, operation_key=op.operation_key)
            rows.append(row)
        op.result = {'transaction_ids': [str(row.id) for row in rows]}
        record(db, actor, 'cash_historical_backfill', 'cash_transaction', rows[0].id, data.model_dump(mode='json'))
        finish(db)
    except Exception:
        db.rollback()
        raise
    return {'operation_key': op.operation_key, 'transactions': [row_response(row) for row in rows]}
