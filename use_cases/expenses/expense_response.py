from models.expense_model import Expense
from schemas.expense_schema import ExpenseResponse


def expense_response(expense: Expense) -> ExpenseResponse:
    values = {field: getattr(expense, field) for field in ExpenseResponse.model_fields if field not in {"currency", "total_quantity"}}
    values["total_quantity"] = expense.pack_quantity * expense.pack_count
    return ExpenseResponse(**values)
