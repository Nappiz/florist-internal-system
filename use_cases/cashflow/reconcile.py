from crud import cashflow_crud
from use_cases.cashflow.common import require_superadmin


def reconcile(db, actor, limit=20, offset=0):
    require_superadmin(actor)
    items, total, counts = cashflow_crud.reconciliation(db, limit, offset)
    return {'items': items, 'total': total, 'limit': limit, 'offset': offset, 'issue_counts': counts, 'is_reconciled': total == 0}
