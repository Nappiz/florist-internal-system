from datetime import UTC, datetime
from use_cases.operational_expenses.access import require_superadmin,get_authorized,require_draft,validate_values
from use_cases.operational_expenses.expense_response import expense_response
from use_cases.common.persistence import finish
from use_cases.audit.record import record


def post_expense(db,actor,expense_id):
    require_superadmin(actor)
    row=get_authorized(db,actor,expense_id,lock=True)
    require_draft(row)
    validate_values(db,{'category_id':row.category_id,'amount':row.amount,'expense_date':row.expense_date})
    row.status='posted'; row.posted_by=actor.user.id; row.posted_at=datetime.now(UTC); row.updated_at=row.posted_at
    record(db,actor,'post','operating_expense',row.id)
    finish(db)
    return expense_response(db,row)
