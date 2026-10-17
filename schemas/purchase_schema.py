from datetime import date,datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Literal
from uuid import UUID
from pydantic import Field
from schemas.catalogue_types import InputModel,Qty,Money,QueryMoney


class PurchaseItemInput(InputModel):
    material_id: UUID
    supplier_listing_id: UUID | None=None
    quantity: Qty
    quantity_base: Qty | None=None
    unit_price: Money | None=None


class PurchaseCreate(InputModel):
    supplier_id: UUID
    purchase_date: date
    reference_number: str | None=Field(None,max_length=100)
    discount_amount: Money=0
    shipping_cost: Money=0
    notes: str | None=Field(None,max_length=2000)
    items: list[PurchaseItemInput]=Field(min_length=1,max_length=100)


class PurchaseUpdate(InputModel):
    purchase_date: date | None=None
    reference_number: str | None=Field(None,max_length=100)
    discount_amount: Money | None=None
    shipping_cost: Money | None=None
    notes: str | None=Field(None,max_length=2000)
    items: list[PurchaseItemInput] | None=Field(None,min_length=1,max_length=100)


class PurchaseQuery(InputModel):
    q: str | None=Field(None,min_length=1,max_length=100)
    supplier_id: UUID | None=None
    status: Literal['draft','ordered','received','cancelled'] | None=None
    payment_status: Literal['unpaid','partial','paid'] | None=None
    date_from: date | None=None
    date_to: date | None=None
    min_total: QueryMoney | None=None
    max_total: QueryMoney | None=None
    limit: int=Field(20,ge=1,le=100)
    offset: int=Field(0,ge=0,le=1_000_000)


class PaymentInput(InputModel):
    cash_account_id: UUID
    payment_key: UUID
    payment_date: date
    amount: int=Field(strict=True,gt=0,le=999999999999999)
    method: str | None=Field(None,max_length=50)
    reference_number: str | None=Field(None,max_length=100)
    notes: str | None=Field(None,max_length=2000)


class PurchaseItemResponse(BaseModel):
    id: UUID
    purchase_id: UUID
    material_id: UUID
    supplier_listing_id: UUID | None
    material_name_snapshot: str
    base_unit_snapshot: str
    quantity: Decimal
    quantity_base: Decimal
    unit_price: int
    subtotal: int


class PurchasePaymentResponse(BaseModel):
    cash_account_id: UUID | None
    reversed_at: datetime | None
    id: UUID
    purchase_id: UUID
    payment_key: UUID
    payment_date: date
    amount: int
    method: str | None
    reference_number: str | None
    notes: str | None
    created_by: UUID | None
    created_at: datetime


class PurchaseSummary(BaseModel):
    id: UUID
    purchase_number: str
    supplier_id: UUID
    purchase_date: date
    reference_number: str | None
    subtotal: int
    discount_amount: int
    shipping_cost: int
    total_amount: int
    status: Literal['draft','ordered','received','cancelled']
    payment_status: Literal['unpaid','partial','paid']
    notes: str | None
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class PurchaseResponse(PurchaseSummary):
    items: list[PurchaseItemResponse]
    payments: list[PurchasePaymentResponse]
    currency: Literal['IDR']='IDR'


class PurchaseListSummary(PurchaseSummary):
    item_names: list[str]=Field(default_factory=list)
