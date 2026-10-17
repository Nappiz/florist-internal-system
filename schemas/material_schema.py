from typing import Literal
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from pydantic import Field,HttpUrl
from schemas.catalogue_types import InputModel,Name,SKU,NonnegativeQty,PageQuery,WebURL

Unit=Literal['pcs','meter','gram','ml','cm','kg','liter','sheet','roll','set']


class MaterialCreate(InputModel):
    sku: SKU
    name: Name
    category: str | None=Field(None,max_length=80)
    description: str | None=Field(None,max_length=2000)
    base_unit: Unit='pcs'
    minimum_stock: NonnegativeQty=Decimal('0')
    image_url: WebURL | None=None
    is_active: bool=True


class MaterialUpdate(InputModel):
    sku: SKU | None=None
    name: Name | None=None
    category: str | None=Field(None,max_length=80)
    description: str | None=Field(None,max_length=2000)
    base_unit: Unit | None=None
    minimum_stock: NonnegativeQty | None=None
    image_url: WebURL | None=None
    is_active: bool | None=None


class MaterialQuery(PageQuery):
    category: str | None=Field(None,max_length=80)
    base_unit: Unit | None=None


class MaterialResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    category: str | None
    description: str | None
    base_unit: str
    minimum_stock: Decimal
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
