from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from uuid import UUID
from pydantic import Field,HttpUrl
from schemas.catalogue_types import InputModel,Name,Qty,Money,QueryMoney,PageQuery,WebURL


class ListingCreate(InputModel):
    material_id: UUID
    supplier_id: UUID
    listing_name: Name
    listing_url: WebURL | None=None
    package_quantity: Qty
    package_unit: str=Field(min_length=1,max_length=32,pattern=r'.*\S.*')
    quantity_in_base_unit: Qty
    listed_price: Money
    last_checked_at: datetime | None=None
    notes: str | None=Field(None,max_length=2000)
    is_active: bool=True


class ListingUpdate(InputModel):
    listing_name: Name | None=None
    listing_url: WebURL | None=None
    package_quantity: Qty | None=None
    package_unit: str | None=Field(None,min_length=1,max_length=32,pattern=r'.*\S.*')
    quantity_in_base_unit: Qty | None=None
    listed_price: Money | None=None
    last_checked_at: datetime | None=None
    notes: str | None=Field(None,max_length=2000)
    is_active: bool | None=None


class ListingQuery(PageQuery):
    material_id: UUID | None=None
    supplier_id: UUID | None=None
    platform: str | None=Field(None,max_length=16)
    category: str | None=Field(None,max_length=80)
    min_price: QueryMoney | None=None
    max_price: QueryMoney | None=None
    sort: str=Field('newest',pattern='^(newest|price_asc|unit_price_asc)$')


class ListingResponse(BaseModel):
    id: UUID
    material_id: UUID
    supplier_id: UUID
    listing_name: str
    listing_url: str | None
    package_quantity: Decimal
    package_unit: str
    quantity_in_base_unit: Decimal
    listed_price: int
    normalized_unit_price: Decimal
    last_checked_at: datetime
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
