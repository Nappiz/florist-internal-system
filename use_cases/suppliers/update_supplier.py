from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import suppliers_crud
from schemas.auth_schema import AuthContext
from schemas.supplier_schema import SupplierResponse, SupplierUpdate
from use_cases.suppliers.supplier_response import supplier_response
from use_cases.suppliers.validate_supplier import validate_supplier


def update_supplier(db: Session, actor: AuthContext, supplier_id: UUID, data: SupplierUpdate) -> SupplierResponse:
    supplier = suppliers_crud.get_by_id(db, supplier_id)
    if supplier is None:
        raise HTTPException(404, "Catatan supplier tidak ditemukan.")
    values = data.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(422, "Isi minimal satu field supplier untuk diperbarui.")
    validate_supplier(values)
    values.update(updated_by=actor.user.id, updated_at=datetime.now(UTC))
    suppliers_crud.update(db, supplier, values)
    db.commit()
    db.refresh(supplier)
    return supplier_response(supplier)
