from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, UrlConstraints

Name = Annotated[str, Field(min_length=1, max_length=150)]
SKU = Annotated[str, Field(min_length=1, max_length=80)]
Quantity = Annotated[Decimal, Field(gt=0, max_digits=20, decimal_places=6, allow_inf_nan=False)]
Price = Annotated[int, Field(ge=0, le=999_999_999_999_999)]
ImageURL = Annotated[HttpUrl, UrlConstraints(max_length=2048)]


class CatalogueInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class FlowerMaterialInput(CatalogueInput):
    material_id: UUID
    quantity_required: Quantity
    unit: str = Field(min_length=1, max_length=32)


class FlowerBOM(CatalogueInput):
    materials: list[FlowerMaterialInput] = Field(default_factory=list, max_length=1000)


class FlowerCreate(CatalogueInput):
    sku: SKU
    name: Name
    category: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=5000)
    image_url: ImageURL | None = None
    selling_price: Price
    estimated_labor_cost: Price = 0
    is_active: bool = True
    bom: FlowerBOM | None = None


class FlowerUpdate(CatalogueInput):
    sku: SKU | None = None
    name: Name | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=5000)
    image_url: ImageURL | None = None
    selling_price: Price | None = None
    estimated_labor_cost: Price | None = None
    is_active: bool | None = None


class CatalogueListQuery(CatalogueInput):
    q: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    is_active: bool | None = None
    sort: Literal["newest", "name", "sku", "price_asc", "price_desc"] = "newest"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=1_000_000)


class MaterialRequirement(BaseModel):
    material_id: UUID
    quantity: Decimal
    unit: str


class CostSource(BaseModel):
    material_id: UUID
    unit_cost: Decimal | None
    source: Literal["inventory", "listing", "missing"]


class CatalogueCost(BaseModel):
    materials: list[MaterialRequirement]
    labor_cost: Decimal
    estimated_material_cost: Decimal | None
    estimated_hpp: Decimal | None
    estimated_profit: Decimal | None
    estimated_margin: Decimal | None
    cost_complete: bool
    cost_sources: list[CostSource]
    available_quantity: int


class FlowerResponse(CatalogueCost):
    id: UUID
    sku: str
    name: str
    category: str | None
    description: str | None
    image_url: str | None
    selling_price: int
    estimated_labor_cost: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FlowerPage(BaseModel):
    items: list[FlowerResponse]
    total: int
    limit: int
    offset: int

