from typing import Annotated
from uuid import UUID
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.custom_bouquet_schema import BouquetCreate,BouquetUpdate,BouquetFinalize,BouquetResponse,BouquetListQuery,BouquetPage
from use_cases.custom_bouquets.create_bouquet import create_bouquet
from use_cases.custom_bouquets.update_bouquet import update_bouquet
from use_cases.custom_bouquets.get_bouquet import get_bouquet
from use_cases.custom_bouquets.list_bouquets import list_bouquets
from use_cases.custom_bouquets.finalize_bouquet import finalize_bouquet
from use_cases.custom_bouquets.archive_bouquet import archive_bouquet
from use_cases.custom_bouquets.duplicate_bouquet import duplicate_bouquet
from use_cases.custom_bouquets.estimate import estimate
from use_cases.custom_bouquets.get_materials import get_materials

router=APIRouter(prefix="/custom-bouquets",tags=["custom-bouquets"])

@router.post("/estimate")
def estimate_endpoint(data:BouquetCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return estimate(db,data)

@router.post("",response_model=BouquetResponse,status_code=201)
def create_endpoint(data:BouquetCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return create_bouquet(db,actor,data)

@router.get("",response_model=BouquetPage)
def list_endpoint(filters:Annotated[BouquetListQuery,Query()],actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_bouquets(db,filters)

@router.get("/{identity}",response_model=BouquetResponse)
def get_endpoint(identity:UUID,actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get_bouquet(db,identity)

@router.put("/{identity}",response_model=BouquetResponse)
def update_endpoint(identity:UUID,data:BouquetCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return update_bouquet(db,actor,identity,data)

@router.post("/{identity}/finalize",response_model=BouquetResponse)
def finalize_endpoint(identity:UUID,data:BouquetFinalize,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return finalize_bouquet(db,actor,identity,data)

@router.post("/{identity}/archive",response_model=BouquetResponse)
def archive_endpoint(identity:UUID,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return archive_bouquet(db,actor,identity)

@router.post("/{identity}/duplicate",response_model=BouquetResponse,status_code=201)
def duplicate_endpoint(identity:UUID,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return duplicate_bouquet(db,actor,identity)

@router.patch("/{identity}",response_model=BouquetResponse)
def patch_endpoint(identity:UUID,data:BouquetUpdate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return update_bouquet(db,actor,identity,data)

@router.get("/{identity}/materials")
def materials_endpoint(identity:UUID,actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get_materials(db,identity)
