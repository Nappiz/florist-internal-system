from decimal import Decimal
from typing import Annotated,Generic,TypeVar
from pydantic import BaseModel,ConfigDict,Field,HttpUrl

Name=Annotated[str,Field(min_length=1,max_length=150,pattern=r'.*\S.*')]
SKU=Annotated[str,Field(min_length=1,max_length=64,pattern=r'^[A-Za-z0-9_.-]+$')]
Qty=Annotated[Decimal,Field(gt=0,le=Decimal('999999999999.999999'),decimal_places=6,allow_inf_nan=False)]
NonnegativeQty=Annotated[Decimal,Field(ge=0,le=Decimal('999999999999.999999'),decimal_places=6,allow_inf_nan=False)]
Money=Annotated[int,Field(strict=True,ge=0,le=999999999999999)]
QueryMoney=Annotated[int,Field(ge=0,le=999999999999999)]
WebURL=Annotated[HttpUrl,Field(max_length=2048)]


class InputModel(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)


class PageQuery(InputModel):
    q: Annotated[str,Field(min_length=1,max_length=100)] | None=None
    is_active: bool | None=True
    limit: int=Field(20,ge=1,le=100)
    offset: int=Field(0,ge=0,le=1_000_000)


T=TypeVar('T')


class PageResponse(BaseModel,Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
