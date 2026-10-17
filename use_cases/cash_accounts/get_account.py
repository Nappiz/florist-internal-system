from fastapi import HTTPException
from crud import cash_accounts_crud, cashflow_crud
from use_cases.cashflow.common import require_superadmin
from use_cases.common.response import row_response


def account_response(db, account):
    return row_response(account) | {'balance': cashflow_crud.balance(db, account.id), 'currency': 'IDR'}


def get_account(db, actor, identity):
    require_superadmin(actor)
    account = cash_accounts_crud.get(db, identity)
    if account is None:
        raise HTTPException(404, 'Cash account tidak ditemukan.')
    return account_response(db, account)
