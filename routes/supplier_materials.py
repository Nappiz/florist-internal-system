from schemas.catalogue_types import PageResponse
from schemas.supplier_material_schema import ListingResponse
from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.supplier_material_schema import ListingCreate,ListingUpdate,ListingQuery
from use_cases.supplier_materials.create import create
from use_cases.supplier_materials.get import get
from use_cases.supplier_materials.list import list_rows
from use_cases.supplier_materials.update import update
from use_cases.supplier_materials.archive import archive

router=APIRouter(prefix='/supplier-materials',tags=['supplier-materials'])


@router.post('',status_code=201,response_model=ListingResponse)
def create_endpoint(data:ListingCreate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return create(db,actor,data)


@router.get('',response_model=PageResponse[ListingResponse])
def list_endpoint(query:ListingQuery=Depends(),actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_rows(db,actor,query)


@router.get('/{identity}',response_model=ListingResponse)
def get_endpoint(identity:UUID,actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get(db,actor,identity)


@router.patch('/{identity}',response_model=ListingResponse)
def update_endpoint(identity:UUID,data:ListingUpdate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return update(db,actor,identity,data)


@router.delete('/{identity}',status_code=204)
def archive_endpoint(identity:UUID,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    archive(db,actor,identity)
