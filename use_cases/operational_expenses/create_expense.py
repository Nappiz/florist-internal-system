from uuid import uuid4
from crud import operational_expenses_crud as crud
from models.operating_expense_model import OperatingExpense
from use_cases.operational_expenses.access import validate_values
from use_cases.operational_expenses.expense_response import expense_response
from use_cases.common.persistence import finish
from use_cases.audit.record import record


def create_expense(db,actor,data):
    values=data.model_dump()
    validate_values(db,values)
    row=crud.add(db,OperatingExpense(**values,expense_number='EXP-'+uuid4().hex.upper(),created_by=actor.user.id))
    db.flush()
    record(db,actor,'create','operating_expense',row.id)
    finish(db)
    return expense_response(db,row)
