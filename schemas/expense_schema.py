from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Money = Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=2, allow_inf_nan=False)]
Total = Annotated[Decimal, Field(ge=0, max_digits=20, decimal_places=2, allow_inf_nan=False)]
PackCount = Annotated[int, Field(strict=True, ge=1, le=1000000)]


class ExpenseInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ExpenseCreate(ExpenseInput):
    supplier_id: UUID
    purchase_date: date | None = None
    pack_count: PackCount = 1
    price_per_pack: Money | None = None
    shipping_cost: Money = Decimal("0")
    discount_amount: Money = Decimal("0")
    payment_method: str | None = Field(default=None, min_length=1, max_length=50)
    reference_number: str | None = Field(default=None, min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


class ExpenseUpdate(ExpenseInput):
    supplier_id: UUID | None = None
    purchase_date: date | None = None
    pack_count: PackCount | None = None
    price_per_pack: Money | None = None
    shipping_cost: Money | None = None
    discount_amount: Money | None = None
    payment_method: str | None = Field(default=None, min_length=1, max_length=50)
    reference_number: str | None = Field(default=None, min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


class ExpenseResponse(BaseModel):
    id: UUID
    supplier_id: UUID | None
    material_name: str
    store_name: str
    purchase_url: str
    pack_quantity: Decimal
    unit: str
    category: str | None
    variant: str | None
    marketplace: str | None
    purchase_date: date
    pack_count: int
    price_per_pack: Decimal
    shipping_cost: Decimal
    discount_amount: Decimal
    subtotal_amount: Decimal
    total_amount: Decimal
    total_quantity: Decimal
    currency: Literal["IDR"] = "IDR"
    payment_method: str | None
    reference_number: str | None
    notes: str | None
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class ExpenseListQuery(ExpenseInput):
    q: str | None = Field(default=None, min_length=1, max_length=100)
    supplier_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    min_total: Total | None = None
    max_total: Total | None = None
    sort: Literal["newest", "oldest", "total_asc", "total_desc"] = "newest"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=1000000)


class ExpensePage(BaseModel):
    items: list[ExpenseResponse]
    total: int
    limit: int
    offset: int
