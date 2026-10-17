from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import expenses_crud


def delete_expense(db: Session, expense_id: UUID) -> None:
    expense = expenses_crud.get_by_id(db, expense_id)
    if expense is None:
        raise HTTPException(404, "Catatan expense tidak ditemukan.")
    expenses_crud.delete(db, expense)
    db.commit()
