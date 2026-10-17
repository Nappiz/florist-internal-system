from schemas.catalogue_types import PageResponse
from schemas.supplier_store_schema import SupplierResponse
from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.supplier_store_schema import SupplierCreate,SupplierUpdate,SupplierQuery
from use_cases.supplier_stores.create import create
from use_cases.supplier_stores.get import get
from use_cases.supplier_stores.list import list_rows
from use_cases.supplier_stores.update import update
from use_cases.supplier_stores.archive import archive

router=APIRouter(prefix='/suppliers',tags=['suppliers'])


@router.post('',status_code=201,response_model=SupplierResponse)
def create_endpoint(data:SupplierCreate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return create(db,actor,data)


@router.get('',response_model=PageResponse[SupplierResponse])
def list_endpoint(query:SupplierQuery=Depends(),actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_rows(db,actor,query)


@router.get('/{identity}',response_model=SupplierResponse)
def get_endpoint(identity:UUID,actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get(db,actor,identity)


@router.patch('/{identity}',response_model=SupplierResponse)
def update_endpoint(identity:UUID,data:SupplierUpdate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return update(db,actor,identity,data)


@router.delete('/{identity}',status_code=204)
def archive_endpoint(identity:UUID,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    archive(db,actor,identity)
