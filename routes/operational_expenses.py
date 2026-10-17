from typing import Annotated
from uuid import UUID
from fastapi import APIRouter,Depends,Query,Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.operational_expense_schema import ExpenseCreate,ExpenseUpdate,ExpensePaymentCreate,ExpenseVoid,ExpenseListQuery,ExpenseResponse,ExpensePage,ExpenseReceiptResponse,ExpenseSummary
from use_cases.operational_expenses.create_expense import create_expense
from use_cases.operational_expenses.update_expense import update_expense
from use_cases.operational_expenses.get_expense import get_expense
from use_cases.operational_expenses.list_expenses import list_expenses
from use_cases.operational_expenses.delete_expense import delete_expense
from use_cases.operational_expenses.post_expense import post_expense
from use_cases.operational_expenses.add_payment import add_payment
from use_cases.operational_expenses.void_expense import void_expense
from use_cases.operational_expenses.expense_summary import expense_summary
from use_cases.operational_expenses.upload_receipt import upload_receipt
from use_cases.operational_expenses.download_receipt import download_receipt

router=APIRouter(prefix='/expenses',tags=['operational-expenses'])


@router.post('',response_model=ExpenseResponse,status_code=201)
def create_endpoint(data:ExpenseCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return create_expense(db,actor,data)


@router.get('',response_model=ExpensePage)
def list_endpoint(filters:Annotated[ExpenseListQuery,Query()],actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_expenses(db,actor,filters)


@router.get('/summary',response_model=ExpenseSummary)
def summary_endpoint(filters:Annotated[ExpenseListQuery,Query()],actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return expense_summary(db,actor,filters)


@router.get('/{expense_id}',response_model=ExpenseResponse)
def get_endpoint(expense_id:UUID,actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get_expense(db,actor,expense_id)


@router.patch('/{expense_id}',response_model=ExpenseResponse)
def update_endpoint(expense_id:UUID,data:ExpenseUpdate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return update_expense(db,actor,expense_id,data)


@router.delete('/{expense_id}',status_code=204)
def delete_endpoint(expense_id:UUID,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    delete_expense(db,actor,expense_id)


@router.post('/{expense_id}/post',response_model=ExpenseResponse)
def post_endpoint(expense_id:UUID,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return post_expense(db,actor,expense_id)


@router.post('/{expense_id}/payments',response_model=ExpenseResponse,status_code=201)
def payment_endpoint(expense_id:UUID,data:ExpensePaymentCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return add_payment(db,actor,expense_id,data)


@router.post('/{expense_id}/void',response_model=ExpenseResponse)
def void_endpoint(expense_id:UUID,data:ExpenseVoid,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return void_expense(db,actor,expense_id,data.reason)


@router.post('/{expense_id}/receipts',response_model=ExpenseReceiptResponse,status_code=201)
async def upload_endpoint(expense_id:UUID,request:Request,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return await upload_receipt(db,actor,expense_id,request.stream(),request.headers.get('content-type'))


@router.get('/{expense_id}/receipts/{receipt_id}')
def download_endpoint(expense_id:UUID,receipt_id:UUID,actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    path,mime,name=download_receipt(db,actor,expense_id,receipt_id)
    return FileResponse(path,media_type=mime,filename=name,headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'})
