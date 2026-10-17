from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.supplier_schema import SupplierCreate, SupplierListQuery, SupplierPage, SupplierResponse, SupplierUpdate
from use_cases.suppliers.create_supplier import create_supplier
from use_cases.suppliers.delete_supplier import delete_supplier
from use_cases.suppliers.get_supplier import get_supplier
from use_cases.suppliers.list_suppliers import list_suppliers
from use_cases.suppliers.update_supplier import update_supplier

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("", response_model=SupplierResponse, status_code=201)
def create_supplier_endpoint(data: SupplierCreate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return create_supplier(db, actor, data)


@router.get("", response_model=SupplierPage)
def list_suppliers_endpoint(
    filters: Annotated[SupplierListQuery, Query()],
    actor: AuthContext = Depends(authenticated_context),
    db: Session = Depends(get_db),
):
    return list_suppliers(db, filters)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier_endpoint(supplier_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_supplier(db, supplier_id)


@router.patch("/{supplier_id}", response_model=SupplierResponse)
def update_supplier_endpoint(supplier_id: UUID, data: SupplierUpdate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return update_supplier(db, actor, supplier_id, data)


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier_endpoint(supplier_id: UUID, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    delete_supplier(db, supplier_id)
