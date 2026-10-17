from typing import Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from pydantic import Field,HttpUrl
from schemas.catalogue_types import InputModel,Name,PageQuery,WebURL

Platform=Literal['shopee','tokopedia','tiktok','offline','other']


class SupplierCreate(InputModel):
    name: Name
    platform: Platform='other'
    shop_url: WebURL | None=None
    contact: str | None=Field(None,max_length=100)
    address: str | None=Field(None,max_length=2000)
    notes: str | None=Field(None,max_length=2000)
    is_active: bool=True


class SupplierUpdate(InputModel):
    name: Name | None=None
    platform: Platform | None=None
    shop_url: WebURL | None=None
    contact: str | None=Field(None,max_length=100)
    address: str | None=Field(None,max_length=2000)
    notes: str | None=Field(None,max_length=2000)
    is_active: bool | None=None


class SupplierQuery(PageQuery):
    platform: Platform | None=None


class SupplierResponse(BaseModel):
    id: UUID
    name: str
    platform: str
    shop_url: str | None
    contact: str | None
    address: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
