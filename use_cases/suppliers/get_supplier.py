from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import suppliers_crud
from schemas.supplier_schema import SupplierResponse
from use_cases.suppliers.supplier_response import supplier_response


def get_supplier(db: Session, supplier_id: UUID) -> SupplierResponse:
    supplier = suppliers_crud.get_by_id(db, supplier_id)
    if supplier is None:
        raise HTTPException(404, "Catatan supplier tidak ditemukan.")
    return supplier_response(supplier)
