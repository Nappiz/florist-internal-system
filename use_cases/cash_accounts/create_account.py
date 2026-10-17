from uuid import UUID, uuid4
from fastapi import HTTPException
from crud import cash_accounts_crud
from models.cash_account_model import CashAccount
from use_cases.audit.record import record
from use_cases.cashflow.common import require_superadmin, validate_date, operation, movement
from use_cases.cash_accounts.get_account import account_response
from use_cases.common.persistence import finish


def create_account(db, actor, data):
    require_superadmin(actor)
    validate_date(data.opening_date)
    if data.history_mode == 'backfill' and data.opening_balance:
        raise HTTPException(422, 'Historical backfill tidak boleh digabung saldo awal.')
    op = operation(db, actor, 'create_account', data)
    if op.result:
        return account_response(db, cash_accounts_crud.get(db, UUID(op.result['account_id'])))
    row = CashAccount(id=uuid4(), name=data.name, account_type=data.account_type, opening_date=data.opening_date, history_mode=data.history_mode, is_active=True, created_by=actor.user.id)
    db.add(row)
    db.flush()
    if data.opening_balance:
        movement(db, actor, account_id=row.id, transaction_date=data.opening_date, direction='IN', amount=data.opening_balance, category='opening_balance', source_type='opening', source_id=row.id, reason=data.reason, operation_key=op.operation_key)
    op.result = {'account_id': str(row.id)}
    record(db, actor, 'cash_account_opening', 'cash_account', row.id, data.model_dump(mode='json'))
    finish(db)
    return account_response(db, row)
