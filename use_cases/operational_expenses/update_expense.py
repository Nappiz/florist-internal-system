from datetime import UTC, datetime
from use_cases.operational_expenses.access import get_authorized,require_draft,validate_values
from use_cases.operational_expenses.expense_response import expense_response
from use_cases.common.persistence import finish
from use_cases.audit.record import record


def update_expense(db,actor,expense_id,data):
    row=get_authorized(db,actor,expense_id,lock=True)
    require_draft(row)
    values=data.model_dump(exclude_unset=True)
    validate_values(db,values)
    for key,value in values.items(): setattr(row,key,value)
    row.updated_at=datetime.now(UTC)
    record(db,actor,'update','operating_expense',row.id,{'fields':list(values)})
    finish(db)
    return expense_response(db,row)
