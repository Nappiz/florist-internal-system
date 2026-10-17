from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, Field
from schemas.catalogue_types import InputModel

PositiveMoney = Annotated[int, Field(strict=True, gt=0, le=999999999999999)]


class AdjustmentInput(InputModel):
    operation_key: UUID
    cash_account_id: UUID
    transaction_date: date
    direction: Literal['IN', 'OUT']
    amount: PositiveMoney
    category: Literal['capital_contribution', 'owner_withdrawal', 'correction', 'other_receipt', 'other_disbursement']
    reason: str = Field(min_length=1, max_length=2000)


class TransferInput(InputModel):
    operation_key: UUID
    from_account_id: UUID
    to_account_id: UUID
    transaction_date: date
    amount: PositiveMoney
    reason: str = Field(min_length=1, max_length=2000)


class ReverseInput(InputModel):
    operation_key: UUID
    reason: str = Field(min_length=1, max_length=2000)
    transaction_date: date


class CashflowQuery(InputModel):
    cash_account_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    period: Literal['today', 'this_week', 'this_month'] | None = None
    source_type: str | None = Field(None, max_length=32)
    category: str | None = Field(None, max_length=100)
    direction: Literal['IN', 'OUT'] | None = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0, le=1_000_000)


class HistoricalMapping(InputModel):
    source_type: Literal['order_payment', 'purchase_payment', 'expense_payment']
    payment_id: UUID
    cash_account_id: UUID


class BackfillInput(InputModel):
    operation_key: UUID
    reason: str = Field(min_length=1, max_length=2000)
    mappings: list[HistoricalMapping] = Field(min_length=1, max_length=500)


class ReportPeriod(BaseModel):
    date_from: date | None
    date_to: date | None
    timezone: Literal['Asia/Jakarta'] = 'Asia/Jakarta'


class CashTransactionResponse(BaseModel):
    id: UUID
    transaction_number: str
    cash_account_id: UUID
    transaction_date: date
    direction: Literal['IN', 'OUT']
    amount: int
    category: str
    source_type: str
    source_id: UUID
    description: str | None
    operation_key: UUID | None
    reversal_of_id: UUID | None
    created_by: UUID | None
    created_at: datetime


class HistoryItem(CashTransactionResponse):
    account_name: str
    running_balance: int


class CashHistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    limit: int
    offset: int
    currency: Literal['IDR'] = 'IDR'
    running_balance_scope: Literal['cash_account'] = 'cash_account'


class SummaryResponse(BaseModel):
    period: ReportPeriod
    cash_account_id: UUID | None
    opening_balance: int
    cash_in: int
    cash_out: int
    net_cashflow: int
    closing_balance: int
    currency: Literal['IDR'] = 'IDR'


class BreakdownItem(BaseModel):
    category: str
    direction: Literal['IN', 'OUT']
    amount: int


class BreakdownResponse(BaseModel):
    items: list[BreakdownItem]
    period: ReportPeriod
    currency: Literal['IDR'] = 'IDR'


class CashOperationResponse(BaseModel):
    operation_key: UUID
    transactions: list[CashTransactionResponse]


class ReconciliationItem(BaseModel):
    source_type: str
    payment_id: UUID
    transaction_id: UUID | None
    issue: str


class ReconciliationResponse(BaseModel):
    items: list[ReconciliationItem]
    total: int
    limit: int
    offset: int
    issue_counts: dict[str, int]
    is_reconciled: bool
