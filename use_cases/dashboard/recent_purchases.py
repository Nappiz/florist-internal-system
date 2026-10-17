from crud import reports_crud
from use_cases.reports.period import resolve_period
from use_cases.common.response import row_response


def recent_purchases(db,actor,query):
    period,_,_=resolve_period(query)
    rows=reports_crud.recent_purchases(db,period['date_from'],period['date_to'],query.limit)
    return {'period':period,'items':[row_response(row) for row in rows],'limit':query.limit}
