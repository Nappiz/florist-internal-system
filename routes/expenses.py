from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.expense_schema import ExpenseCreate, ExpenseListQuery, ExpensePage, ExpenseResponse, ExpenseUpdate
from use_cases.expenses.create_expense import create_expense
from use_cases.expenses.delete_expense import delete_expense
from use_cases.expenses.get_expense import get_expense
from use_cases.expenses.list_expenses import list_expenses
from use_cases.expenses.update_expense import update_expense

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense_endpoint(data: ExpenseCreate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return create_expense(db, actor, data)


@router.get("", response_model=ExpensePage)
def list_expenses_endpoint(filters: Annotated[ExpenseListQuery, Query()], actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return list_expenses(db, filters)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense_endpoint(expense_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_expense(db, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense_endpoint(expense_id: UUID, data: ExpenseUpdate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return update_expense(db, actor, expense_id, data)


@router.delete("/{expense_id}", status_code=204)
def delete_expense_endpoint(expense_id: UUID, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    delete_expense(db, expense_id)
