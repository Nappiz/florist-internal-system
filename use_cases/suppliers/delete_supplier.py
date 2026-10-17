from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import suppliers_crud


def delete_supplier(db: Session, supplier_id: UUID) -> None:
    supplier = suppliers_crud.get_by_id(db, supplier_id)
    if supplier is None:
        raise HTTPException(404, "Catatan supplier tidak ditemukan.")
    suppliers_crud.delete(db, supplier)
    db.commit()
