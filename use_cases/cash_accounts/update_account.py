from fastapi import HTTPException
from crud import cash_accounts_crud
from use_cases.audit.record import record
from use_cases.cashflow.common import require_superadmin, operation
from use_cases.cash_accounts.get_account import account_response
from use_cases.common.persistence import finish


def update_account(db, actor, identity, data):
    require_superadmin(actor)
    account = cash_accounts_crud.get(db, identity, lock=True)
    if account is None:
        raise HTTPException(404, 'Cash account tidak ditemukan.')
    op = operation(db, actor, 'update_account', data, {'account_id': str(identity)})
    if op.result:
        return account_response(db, account)
    for field in ('name', 'is_active'):
        value = getattr(data, field)
        if value is not None:
            setattr(account, field, value)
    record(db, actor, 'cash_account_update', 'cash_account', account.id, data.model_dump(mode='json'))
    op.result = {'account_id': str(identity)}
    finish(db)
    return account_response(db, account)
