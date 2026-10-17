from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import expenses_crud, suppliers_crud
from models.expense_model import Expense
from schemas.auth_schema import AuthContext
from schemas.expense_schema import ExpenseCreate, ExpenseResponse
from use_cases.expenses.calculate_expense import calculate_expense
from use_cases.expenses.expense_response import expense_response
from use_cases.expenses.supplier_snapshot import supplier_snapshot
from use_cases.expenses.validate_expense import BUSINESS_TIMEZONE, validate_expense


def create_expense(db: Session, actor: AuthContext, data: ExpenseCreate) -> ExpenseResponse:
    values = data.model_dump(exclude_unset=True)
    validate_expense(values)
    supplier = suppliers_crud.get_by_id(db, data.supplier_id)
    if supplier is None:
        raise HTTPException(404, "Catatan supplier tidak ditemukan.")
    values = data.model_dump()
    if "purchase_date" not in data.model_fields_set:
        values["purchase_date"] = datetime.now(BUSINESS_TIMEZONE).date()
    if "price_per_pack" not in data.model_fields_set:
        values["price_per_pack"] = supplier.price
    values.update(supplier_snapshot(supplier))
    values["subtotal_amount"], values["total_amount"] = calculate_expense(
        values["pack_count"], values["price_per_pack"], values["shipping_cost"], values["discount_amount"],
    )
    now = datetime.now(UTC)
    expense = expenses_crud.add(db, Expense(**values, created_by=actor.user.id, updated_by=actor.user.id, created_at=now, updated_at=now))
    db.commit()
    db.refresh(expense)
    return expense_response(expense)
