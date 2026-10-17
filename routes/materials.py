from schemas.catalogue_types import PageResponse
from schemas.material_schema import MaterialResponse
from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.material_schema import MaterialCreate,MaterialUpdate,MaterialQuery
from use_cases.materials.create import create
from use_cases.materials.get import get
from use_cases.materials.list import list_rows
from use_cases.materials.update import update
from use_cases.materials.archive import archive

router=APIRouter(prefix='/materials',tags=['materials'])


@router.post('',status_code=201,response_model=MaterialResponse)
def create_endpoint(data:MaterialCreate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return create(db,actor,data)


@router.get('',response_model=PageResponse[MaterialResponse])
def list_endpoint(query:MaterialQuery=Depends(),actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_rows(db,actor,query)


@router.get('/{identity}',response_model=MaterialResponse)
def get_endpoint(identity:UUID,actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get(db,actor,identity)


@router.patch('/{identity}',response_model=MaterialResponse)
def update_endpoint(identity:UUID,data:MaterialUpdate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return update(db,actor,identity,data)


@router.delete('/{identity}',status_code=204)
def archive_endpoint(identity:UUID,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    archive(db,actor,identity)
