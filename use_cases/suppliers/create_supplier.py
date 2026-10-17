from datetime import UTC, datetime

from sqlalchemy.orm import Session

from crud import suppliers_crud
from models.supplier_model import Supplier
from schemas.auth_schema import AuthContext
from schemas.supplier_schema import SupplierCreate, SupplierResponse
from use_cases.suppliers.supplier_response import supplier_response
from use_cases.suppliers.validate_supplier import BUSINESS_TIMEZONE, validate_supplier


def create_supplier(db: Session, actor: AuthContext, data: SupplierCreate) -> SupplierResponse:
    values = data.model_dump()
    if "last_checked_at" not in data.model_fields_set:
        values["last_checked_at"] = datetime.now(BUSINESS_TIMEZONE).date()
    validate_supplier(values)
    now = datetime.now(UTC)
    supplier = suppliers_crud.add(db, Supplier(
        **values, created_by=actor.user.id, updated_by=actor.user.id, created_at=now, updated_at=now,
    ))
    db.commit()
    db.refresh(supplier)
    return supplier_response(supplier)
