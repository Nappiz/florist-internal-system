from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID
from schemas.catalogue_types import WebURL
from pydantic import BaseModel, ConfigDict, Field

Amount = Annotated[int, Field(strict=True, gt=0, le=999999999999999)]


class ExpenseInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class ExpenseCreate(ExpenseInput):
    category_id: UUID
    title: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    vendor_name: str | None = Field(default=None, max_length=150)
    expense_date: date
    amount: Amount


class ExpenseUpdate(ExpenseInput):
    category_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    vendor_name: str | None = Field(default=None, max_length=150)
    expense_date: date | None = None
    amount: Amount | None = None


class ExpensePaymentCreate(ExpenseInput):
    payment_key: UUID
    cash_account_id: UUID
    payment_date: date
    amount: Amount
    method: str = Field(min_length=1, max_length=50)
    reference_number: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)
    proof_url: WebURL | None = None


class ExpenseVoid(ExpenseInput):
    reason: str = Field(min_length=1, max_length=2000)


class ExpenseListQuery(ExpenseInput):
    search: str | None = Field(default=None, max_length=150)
    category_id: UUID | None = None
    status: Literal['draft','posted','void'] | None = None
    payment_status: Literal['unpaid','partial','paid'] | None = None
    date_from: date | None = None
    date_to: date | None = None
    amount_min: int | None = Field(default=None, ge=0)
    amount_max: int | None = Field(default=None, ge=0)
    page: int = Field(default=1, ge=1, le=1000000)
    page_size: int = Field(default=50, ge=1, le=100)


class ExpenseResponse(ExpenseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    expense_number: str
    status: str
    payment_status: str
    paid_amount: int
    remaining_amount: int
    created_by: UUID
    posted_by: UUID | None
    posted_at: datetime | None
    voided_by: UUID | None
    voided_at: datetime | None
    void_reason: str | None
    created_at: datetime
    updated_at: datetime
    payments: list[dict]
    receipts: list[dict]


class ExpensePage(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int


class ExpenseReceiptResponse(BaseModel):
    id: UUID
    expense_id: UUID
    mime_type: str
    size_bytes: int
    original_name: str
    created_at: datetime


class ExpenseCategorySummary(BaseModel):
    category_id: UUID
    name: str
    classification: str
    amount: int
    paid_amount: int


class ExpenseTrend(BaseModel):
    month: str
    amount: int


class ExpenseSummary(BaseModel):
    date_basis: str
    payment_basis: str
    total_posted_expenses: int
    total_paid_expenses: int
    total_unpaid_expenses: int
    by_category: list[ExpenseCategorySummary]
    trend: list[ExpenseTrend]
