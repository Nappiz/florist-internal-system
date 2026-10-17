from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import expenses_crud, suppliers_crud
from schemas.auth_schema import AuthContext
from schemas.expense_schema import ExpenseResponse, ExpenseUpdate
from use_cases.expenses.calculate_expense import calculate_expense
from use_cases.expenses.expense_response import expense_response
from use_cases.expenses.supplier_snapshot import supplier_snapshot
from use_cases.expenses.validate_expense import validate_expense


def update_expense(db: Session, actor: AuthContext, expense_id: UUID, data: ExpenseUpdate) -> ExpenseResponse:
    values = data.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(422, "Isi minimal satu field expense untuk diperbarui.")
    validate_expense(values)
    # Supplier deletion also locks supplier then expense through SET NULL.
    # Acquire explicit supplier references first to keep the lock order consistent.
    supplier = None
    if "supplier_id" in values:
        supplier = suppliers_crud.get_by_id(db, values["supplier_id"])
        if supplier is None:
            raise HTTPException(404, "Catatan supplier tidak ditemukan.")
    expense = expenses_crud.get_by_id(db, expense_id)
    if expense is None:
        raise HTTPException(404, "Catatan expense tidak ditemukan.")
    if supplier is not None and supplier.id != expense.supplier_id:
        values.update(supplier_snapshot(supplier))
        if "price_per_pack" not in values:
            values["price_per_pack"] = supplier.price
    values["subtotal_amount"], values["total_amount"] = calculate_expense(
        values.get("pack_count", expense.pack_count), values.get("price_per_pack", expense.price_per_pack),
        values.get("shipping_cost", expense.shipping_cost), values.get("discount_amount", expense.discount_amount),
    )
    values.update(updated_by=actor.user.id, updated_at=datetime.now(UTC))
    expenses_crud.update(db, expense, values)
    db.commit()
    db.refresh(expense)
    return expense_response(expense)
