from crud import cash_accounts_crud
from use_cases.cashflow.common import require_superadmin
from use_cases.cash_accounts.get_account import account_response


def list_accounts(db, actor, query):
    require_superadmin(actor)
    rows, total = cash_accounts_crud.page(db, query)
    return {'items': [account_response(db, row) for row in rows], 'total': total, 'limit': query.limit, 'offset': query.offset}
