from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, UrlConstraints, field_validator

Money = Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=2, allow_inf_nan=False)]
Quantity = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=3, allow_inf_nan=False)]
Name = Annotated[str, Field(min_length=1, max_length=150)]
Unit = Annotated[str, Field(min_length=1, max_length=32)]
Category = Annotated[str, Field(min_length=1, max_length=80)]
Marketplace = Annotated[str, Field(min_length=1, max_length=50)]
PurchaseUrl = Annotated[HttpUrl, UrlConstraints(max_length=2048)]


class SupplierInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("purchase_url", check_fields=False)
    @classmethod
    def reject_url_credentials(cls, value):
        if value is not None and (value.username is not None or value.password is not None):
            raise ValueError("Link pembelian tidak boleh mengandung credential.")
        if value is not None and len(str(value)) > 2048:
            raise ValueError("Link pembelian setelah normalisasi maksimal 2048 karakter.")
        return value


class SupplierCreate(SupplierInput):
    material_name: Name
    store_name: Name
    purchase_url: PurchaseUrl
    price: Money
    pack_quantity: Quantity = Decimal("1")
    unit: Unit = "pcs"
    category: Category | None = None
    variant: Name | None = None
    marketplace: Marketplace | None = None
    estimated_shipping_cost: Money | None = None
    last_checked_at: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class SupplierUpdate(SupplierInput):
    material_name: Name | None = None
    store_name: Name | None = None
    purchase_url: PurchaseUrl | None = None
    price: Money | None = None
    pack_quantity: Quantity | None = None
    unit: Unit | None = None
    category: Category | None = None
    variant: Name | None = None
    marketplace: Marketplace | None = None
    estimated_shipping_cost: Money | None = None
    last_checked_at: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class SupplierResponse(SupplierCreate):
    id: UUID
    last_checked_at: date
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime
    currency: Literal["IDR"] = "IDR"
    unit_price: Decimal
    landed_unit_price: Decimal | None = None


class SupplierListQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    q: str | None = Field(default=None, min_length=1, max_length=100)
    store_name: Name | None = None
    category: Category | None = None
    marketplace: Marketplace | None = None
    unit: Unit | None = None
    min_price: Money | None = None
    max_price: Money | None = None
    sort: Literal["newest", "price_asc", "price_desc", "unit_price_asc"] = "newest"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=1_000_000)


class SupplierPage(BaseModel):
    items: list[SupplierResponse]
    total: int
    limit: int
    offset: int
