from datetime import datetime
from decimal import Decimal
from typing import Annotated,Literal
from uuid import UUID
from pydantic import BaseModel,ConfigDict,Field
from schemas.catalogue_types import WebURL

Money=Annotated[int,Field(strict=True,ge=0,le=999999999999999)]
Count=Annotated[int,Field(strict=True,ge=1,le=1000000)]
Amount=Annotated[Decimal,Field(gt=0,le=Decimal("999999999999.999999"),max_digits=18,decimal_places=6,allow_inf_nan=False)]

class Input(BaseModel):
    model_config=ConfigDict(extra="forbid",str_strip_whitespace=True)

class Personalization(Input):
    recipient_name: str|None=Field(None,max_length=150)
    gift_message: str|None=Field(None,max_length=2000)
    color_theme: str|None=Field(None,max_length=150)
    special_notes: str|None=Field(None,max_length=2000)

class FlowerSelection(Input):
    flower_id: UUID
    quantity: Count=1

class OptionSelection(Input):
    bouquet_option_id: UUID
    quantity: Count=1

class AdditionalMaterial(Input):
    material_id: UUID
    quantity_required: Amount
    unit: str=Field(min_length=1,max_length=32)

class BouquetCreate(Input):
    name: str|None=Field(None,min_length=1,max_length=150)
    customer_reference: str|None=Field(None,max_length=150)
    description: str|None=Field(None,max_length=2000)
    image_reference: WebURL|None=None
    personalization: Personalization=Field(default_factory=Personalization)
    flowers: list[FlowerSelection]=Field(default_factory=list,max_length=1000)
    options: list[OptionSelection]=Field(default_factory=list,max_length=100)
    additional_materials: list[AdditionalMaterial]=Field(default_factory=list,max_length=1000)

class BouquetUpdate(Input):
    name: str|None=Field(None,min_length=1,max_length=150)
    customer_reference: str|None=Field(None,max_length=150)
    description: str|None=Field(None,max_length=2000)
    image_reference: WebURL|None=None
    personalization: Personalization|None=None
    flowers: list[FlowerSelection]|None=Field(None,max_length=1000)
    options: list[OptionSelection]|None=Field(None,max_length=100)
    additional_materials: list[AdditionalMaterial]|None=Field(None,max_length=1000)

class BouquetFinalize(Input):
    final_price: Money|None=None
    reason: str|None=Field(None,min_length=1,max_length=2000)

class BouquetResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: UUID
    configuration_number: str
    name: str
    status: str
    customer_reference: str|None
    description: str|None
    image_reference: str|None
    personalization: dict
    estimated_hpp: Decimal|None
    cost_complete: bool
    proposed_price: int
    final_price: int|None
    price_override_reason: str|None
    assembly_fee: int
    assembly_labor_cost: Decimal
    pricing_version: int
    recipe_snapshot: dict
    created_by: UUID|None
    updated_by: UUID|None
    created_at: datetime
    updated_at: datetime

class BouquetListQuery(Input):
    status: Literal["draft","finalized","archived"]|None=None
    q: str|None=Field(None,min_length=1,max_length=100)
    limit: int=Field(20,ge=1,le=100)
    offset: int=Field(0,ge=0,le=1000000)

class BouquetPage(BaseModel):
    items: list[BouquetResponse]
    total: int
    limit: int
    offset: int
