from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from schemas.cashflow_schema import AdjustmentInput, TransferInput, ReverseInput, CashflowQuery, BackfillInput
from schemas.cashflow_schema import SummaryResponse, CashHistoryResponse, BreakdownResponse, CashTransactionResponse, CashOperationResponse, ReconciliationResponse
from use_cases.cashflow.summary import summary
from use_cases.cashflow.history import history
from use_cases.cashflow.breakdown import breakdown
from use_cases.cashflow.export import export
from use_cases.cashflow.adjust import adjust
from use_cases.cashflow.transfer import transfer
from use_cases.cashflow.reverse_payment import reverse_payment
from use_cases.cashflow.reconcile import reconcile
from use_cases.cashflow.backfill import backfill

router = APIRouter(prefix='/cashflow', tags=['cashflow'])


@router.get('/summary', response_model=SummaryResponse)
def summary_endpoint(query: CashflowQuery = Depends(), actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return summary(db, actor, query)


@router.get('/transactions', response_model=CashHistoryResponse)
def history_endpoint(query: CashflowQuery = Depends(), actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return history(db, actor, query)


@router.get('/breakdown', response_model=BreakdownResponse)
def breakdown_endpoint(query: CashflowQuery = Depends(), actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return breakdown(db, actor, query)


@router.get('/export')
def export_endpoint(query: CashflowQuery = Depends(), actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return StreamingResponse(export(db, actor, query), media_type='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename="cashflow.csv"'})


@router.get('/reconciliation', response_model=ReconciliationResponse)
def reconciliation_endpoint(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=1_000_000), actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return reconcile(db, actor, limit, offset)


@router.post('/adjustments', status_code=201, response_model=CashTransactionResponse)
def adjust_endpoint(data: AdjustmentInput, actor=Depends(csrf_context), db: Session = Depends(get_db)):
    return adjust(db, actor, data)


@router.post('/transfers', status_code=201, response_model=CashOperationResponse)
def transfer_endpoint(data: TransferInput, actor=Depends(csrf_context), db: Session = Depends(get_db)):
    return transfer(db, actor, data)


@router.post('/transactions/{identity}/reverse', status_code=201, response_model=CashTransactionResponse)
def reverse_endpoint(identity: UUID, data: ReverseInput, actor=Depends(csrf_context), db: Session = Depends(get_db)):
    return reverse_payment(db, actor, identity, data)


@router.post('/backfill', status_code=201, response_model=CashOperationResponse)
def backfill_endpoint(data: BackfillInput, actor=Depends(csrf_context), db: Session = Depends(get_db)):
    return backfill(db, actor, data)
