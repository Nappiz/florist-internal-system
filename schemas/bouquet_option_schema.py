from typing import Literal
from uuid import UUID
from pydantic import BaseModel,ConfigDict,Field
from schemas.catalogue_types import WebURL
from schemas.custom_bouquet_schema import Input,Money,Count,AdditionalMaterial

OptionGroup=Literal["wrapping","ribbon","greeting_card","accessory"]

class BouquetOptionCreate(Input):
    name: str=Field(min_length=1,max_length=150)
    option_group: OptionGroup
    description: str|None=Field(None,max_length=2000)
    image_url: WebURL|None=None
    selling_price: Money
    min_quantity: Count=1
    max_quantity: Count=100
    requires_materials: bool=True
    is_active: bool=True
    materials: list[AdditionalMaterial]=Field(default_factory=list,max_length=1000)

class BouquetOptionUpdate(Input):
    name: str|None=Field(None,min_length=1,max_length=150)
    option_group: OptionGroup|None=None
    description: str|None=Field(None,max_length=2000)
    image_url: WebURL|None=None
    selling_price: Money|None=None
    min_quantity: Count|None=None
    max_quantity: Count|None=None
    requires_materials: bool|None=None
    is_active: bool|None=None
    materials: list[AdditionalMaterial]|None=Field(None,max_length=1000)

class BouquetOptionResponse(BouquetOptionCreate):
    model_config=ConfigDict(from_attributes=True)
    id: UUID

class BouquetOptionQuery(Input):
    option_group: OptionGroup|None=None
    is_active: bool|None=None
    limit: int=Field(20,ge=1,le=100)
    offset: int=Field(0,ge=0,le=1000000)

class BouquetOptionPage(BaseModel):
    items: list[BouquetOptionResponse]
    total: int
    limit: int
    offset: int
