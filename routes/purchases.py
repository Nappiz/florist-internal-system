from schemas.catalogue_types import PageResponse
from schemas.purchase_schema import PurchaseListSummary,PurchaseResponse
from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.purchase_schema import PurchaseCreate,PurchaseUpdate,PurchaseQuery,PaymentInput
from use_cases.purchases.create import create
from use_cases.purchases.get import get
from use_cases.purchases.list import list_rows
from use_cases.purchases.update import update
from use_cases.purchases.order import order
from use_cases.purchases.receive import receive
from use_cases.purchases.cancel import cancel
from use_cases.purchases.payment import payment

router=APIRouter(prefix='/purchases',tags=['purchases'])


@router.post('',status_code=201,response_model=PurchaseResponse)
def create_endpoint(data:PurchaseCreate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return create(db,actor,data)


@router.get('',response_model=PageResponse[PurchaseListSummary])
def list_endpoint(query:PurchaseQuery=Depends(),actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_rows(db,actor,query)


@router.get('/{identity}',response_model=PurchaseResponse)
def get_endpoint(identity:UUID,actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get(db,actor,identity)


@router.patch('/{identity}',response_model=PurchaseResponse)
def update_endpoint(identity:UUID,data:PurchaseUpdate,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return update(db,actor,identity,data)


@router.post('/{identity}/order',response_model=PurchaseResponse)
def order_endpoint(identity:UUID,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return order(db,actor,identity)


@router.post('/{identity}/receive',response_model=PurchaseResponse)
def receive_endpoint(identity:UUID,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return receive(db,actor,identity)


@router.post('/{identity}/cancel',response_model=PurchaseResponse)
def cancel_endpoint(identity:UUID,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return cancel(db,actor,identity)


@router.post('/{identity}/payments',status_code=201,response_model=PurchaseResponse)
def payment_endpoint(identity:UUID,data:PaymentInput,actor=Depends(csrf_context),db:Session=Depends(get_db)):
    return payment(db,actor,identity,data)
