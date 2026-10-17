from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import expenses_crud
from models.expense_model import Expense
from schemas.expense_schema import ExpenseListQuery, ExpensePage
from use_cases.expenses.expense_response import expense_response


def list_expenses(db: Session, filters: ExpenseListQuery) -> ExpensePage:
    if filters.date_from is not None and filters.date_to is not None and filters.date_from > filters.date_to:
        raise HTTPException(422, "Tanggal awal tidak boleh melewati tanggal akhir.")
    if filters.min_total is not None and filters.max_total is not None and filters.min_total > filters.max_total:
        raise HTTPException(422, "Total minimum tidak boleh melebihi total maksimum.")
    order = {"newest":Expense.purchase_date.desc(), "oldest":Expense.purchase_date.asc(),
             "total_asc":Expense.total_amount.asc(), "total_desc":Expense.total_amount.desc()}[filters.sort]
    return ExpensePage(items=[expense_response(row) for row in expenses_crud.list_expenses(db, filters, order)],
                       total=expenses_crud.count(db, filters), limit=filters.limit, offset=filters.offset)
