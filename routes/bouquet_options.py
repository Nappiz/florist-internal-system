from typing import Annotated
from uuid import UUID
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.bouquet_option_schema import BouquetOptionCreate,BouquetOptionUpdate,BouquetOptionResponse,BouquetOptionQuery,BouquetOptionPage
from use_cases.bouquet_options.create_option import create_option
from use_cases.bouquet_options.update_option import update_option
from use_cases.bouquet_options.archive_option import archive_option
from use_cases.bouquet_options.get_option import get_option
from use_cases.bouquet_options.list_options import list_options

router=APIRouter(prefix="/bouquet-options",tags=["bouquet-options"])

@router.post("",response_model=BouquetOptionResponse,status_code=201)
def create_endpoint(data:BouquetOptionCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return create_option(db,actor,data)

@router.get("",response_model=BouquetOptionPage)
def list_endpoint(filters:Annotated[BouquetOptionQuery,Query()],actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_options(db,filters)

@router.get("/{identity}",response_model=BouquetOptionResponse)
def get_endpoint(identity:UUID,actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get_option(db,identity)

@router.put("/{identity}",response_model=BouquetOptionResponse)
def update_endpoint(identity:UUID,data:BouquetOptionCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return update_option(db,actor,identity,data)

@router.delete("/{identity}",status_code=204)
def archive_endpoint(identity:UUID,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    archive_option(db,actor,identity)

@router.patch("/{identity}",response_model=BouquetOptionResponse)
def patch_endpoint(identity:UUID,data:BouquetOptionUpdate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return update_option(db,actor,identity,data)
