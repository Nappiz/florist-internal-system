from schemas.catalogue_types import PageResponse
from schemas.inventory_schema import BalanceResponse,InventoryResponse,MovementResponse
from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.inventory_schema import InventoryQuery,AdjustmentInput
from use_cases.inventory.get import get
from use_cases.inventory.list import list_rows
from use_cases.inventory.movements import movements
from use_cases.inventory.adjust import adjust

router=APIRouter(prefix='/inventory',tags=['inventory'])


@router.get('',response_model=PageResponse[InventoryResponse])
def inventory_endpoint(query:InventoryQuery=Depends(),actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_rows(db,actor,query)


@router.get('/movements',response_model=PageResponse[MovementResponse])
def movements_endpoint(query:InventoryQuery=Depends(),actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return movements(db,actor,query)


@router.get('/low-stock',response_model=PageResponse[InventoryResponse])
def low_stock_endpoint(query:InventoryQuery=Depends(),actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_rows(db,actor,query,low_stock=True)


@router.post('/adjustments',status_code=201,response_model=BalanceResponse)
def adjust_endpoint(data:AdjustmentInput,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return adjust(db,actor,data)


@router.get('/{identity}',response_model=InventoryResponse)
def material_endpoint(identity:UUID,actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get(db,actor,identity)
