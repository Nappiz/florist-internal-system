from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.flower_schema import CatalogueCost, CatalogueInput, CatalogueListQuery, FlowerMaterialInput, ImageURL, Name, Price, Quantity, SKU


class ProductFlowerInput(CatalogueInput):
    flower_id: UUID
    quantity_required: Quantity


class ProductBOM(CatalogueInput):
    flowers: list[ProductFlowerInput] = Field(default_factory=list, max_length=1000)
    materials: list[FlowerMaterialInput] = Field(default_factory=list, max_length=1000)


class ProductCreate(CatalogueInput):
    sku: SKU
    name: Name
    category: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=5000)
    image_url: ImageURL | None = None
    selling_price: Price
    assembly_labor_cost: Price = 0
    is_active: bool = True
    bom: ProductBOM | None = None


class ProductUpdate(CatalogueInput):
    sku: SKU | None = None
    name: Name | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=5000)
    image_url: ImageURL | None = None
    selling_price: Price | None = None
    assembly_labor_cost: Price | None = None
    is_active: bool | None = None


class ProductResponse(CatalogueCost):
    id: UUID
    sku: str
    name: str
    category: str | None
    description: str | None
    image_url: str | None
    selling_price: int
    assembly_labor_cost: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductPage(BaseModel):
    items: list[ProductResponse]
    total: int
    limit: int
    offset: int

