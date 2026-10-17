from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from schemas.cash_account_schema import CashAccountCreate, CashAccountQuery, CashAccountUpdate, CashAccountResponse, CashAccountOption
from schemas.catalogue_types import PageResponse
from use_cases.cash_accounts.create_account import create_account
from use_cases.cash_accounts.get_account import get_account
from use_cases.cash_accounts.list_accounts import list_accounts
from use_cases.cash_accounts.account_options import account_options
from use_cases.cash_accounts.update_account import update_account

router = APIRouter(prefix='/cash-accounts', tags=['cash accounts'])


@router.get('', response_model=PageResponse[CashAccountResponse])
def list_endpoint(query: CashAccountQuery = Depends(), actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return list_accounts(db, actor, query)


@router.get('/options', response_model=PageResponse[CashAccountOption])
def options_endpoint(query: CashAccountQuery = Depends(), actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return account_options(db, actor, query)


@router.post('', status_code=201, response_model=CashAccountResponse)
def create_endpoint(data: CashAccountCreate, actor=Depends(csrf_context), db: Session = Depends(get_db)):
    return create_account(db, actor, data)


@router.get('/{identity}', response_model=CashAccountResponse)
def get_endpoint(identity: UUID, actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_account(db, actor, identity)


@router.patch('/{identity}', response_model=CashAccountResponse)
def update_endpoint(identity: UUID, data: CashAccountUpdate, actor=Depends(csrf_context), db: Session = Depends(get_db)):
    return update_account(db, actor, identity, data)
