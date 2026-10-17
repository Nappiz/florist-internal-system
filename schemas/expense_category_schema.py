from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    classification: Literal['operational','equipment','other'] = 'operational'


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    classification: Literal['operational','equipment','other'] | None = None
    is_active: bool | None = None


class CategoryResponse(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    is_active: bool
