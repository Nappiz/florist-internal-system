from crud import cashflow_crud
from use_cases.cashflow.common import require_superadmin, report_query


def summary(db, actor, query):
    require_superadmin(actor)
    query = report_query(query)
    opening, inflow, outflow = map(int, cashflow_crud.totals(db, query))
    return {'period': {'date_from': query.date_from, 'date_to': query.date_to, 'timezone': 'Asia/Jakarta'}, 'cash_account_id': query.cash_account_id, 'opening_balance': opening, 'cash_in': inflow, 'cash_out': outflow, 'net_cashflow': inflow - outflow, 'closing_balance': opening + inflow - outflow, 'currency': 'IDR'}
