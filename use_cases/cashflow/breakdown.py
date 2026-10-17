from crud import cashflow_crud
from use_cases.cashflow.common import require_superadmin, report_query


def breakdown(db, actor, query):
    require_superadmin(actor)
    query = report_query(query)
    return {'items': cashflow_crud.breakdown(db, query), 'period': {'date_from': query.date_from, 'date_to': query.date_to, 'timezone': 'Asia/Jakarta'}, 'currency': 'IDR'}
