from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import expenses_crud
from schemas.expense_schema import ExpenseResponse
from use_cases.expenses.expense_response import expense_response


def get_expense(db: Session, expense_id: UUID) -> ExpenseResponse:
    expense = expenses_crud.get_by_id(db, expense_id)
    if expense is None:
        raise HTTPException(404, "Catatan expense tidak ditemukan.")
    return expense_response(expense)
