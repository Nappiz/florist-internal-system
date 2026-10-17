from use_cases.operational_expenses.access import get_authorized
from use_cases.operational_expenses.expense_response import expense_response


def get_expense(db,actor,expense_id):
    return expense_response(db,get_authorized(db,actor,expense_id))
