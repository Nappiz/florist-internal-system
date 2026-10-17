from crud import cashflow_crud
from use_cases.cashflow.common import require_superadmin, report_query


def history(db, actor, query):
    require_superadmin(actor)
    query = report_query(query)
    rows, total = cashflow_crud.history(db, query)
    return {'items': rows, 'total': total, 'limit': query.limit, 'offset': query.offset, 'currency': 'IDR', 'running_balance_scope': 'cash_account'}
